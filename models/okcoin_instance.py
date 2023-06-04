 # -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError
import requests, logging, json, datetime, hmac, base64
import numpy as np
_logger = logging.getLogger(__name__)


class OKcoinInstance(models.Model):
    _name = 'okcoin.instance'
    _description = 'OKcoin V5 Instance'

    name = fields.Char(string='Name')
    server_url = fields.Char(string='Server URL')
    api_key = fields.Char(string='API Key')
    secret_key = fields.Char(string='Secret Key')
    pass_phrase = fields.Char(string='Password')
    maker_taker = fields.Selection([('taker', 'Taker'), ('maker', 'Maker')])
    convert_percent = fields.Integer()
    state = fields.Selection(
        [("draft", "Not Confirmed"), ("active", "Active"), ("inactive", "Inactive")],
        default="draft",
        string="State",
    )


    def get_okcoin_timestamp(self):
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
        print(timestamp)
        return timestamp

    def get_signature(self, t, method, request_path, body=None):
        if str(body) == '{}' or str(body) == 'None' or body == None:
            body = ''
        message = str(t) + str.upper(method) + request_path + str(body)
        mac = hmac.new(bytes(self.secret_key, encoding='utf8'), bytes(message, encoding='utf-8'),  digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)

    def get_header(self, sig, t):
        CONTENT_TYPE = 'Content-Type'
        OK_ACCESS_KEY = 'OK-ACCESS-KEY'
        OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
        OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
        OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'
        APPLICATION_JSON = 'application/json'
        GET = 'GET'
        POST = 'POST'
        header = dict()
        header[CONTENT_TYPE] = APPLICATION_JSON
        header[OK_ACCESS_KEY] = self.api_key
        header[OK_ACCESS_SIGN] = sig
        header[OK_ACCESS_TIMESTAMP] = t
        header[OK_ACCESS_PASSPHRASE] = self.pass_phrase
        return header

    def parse_params_to_str(self, params):
        url = '?'
        for key, value in params.items():
            url = url + str(key) + '=' + str(value) + '&'
        return url[0:-1]

    def query(self, type, request_path, body=''):
        if type == "POST":
            body = json.dumps(body)
            print(body)
        else:
            if body != '':
                body = self.parse_params_to_str(body)
        timestamp = self.get_okcoin_timestamp()
        print(body)
        signature = self.get_signature(timestamp, type, request_path, body)
        header = self.get_header(signature, timestamp)
        if type == 'GET':
            response = requests.get(self.server_url + request_path + body, headers=header)
        else:
            print(self.server_url+ request_path)
            response = requests.post(self.server_url + request_path, data=body, headers=header)
        return response

    def test_okcoin_connection(self):
        try:
            request_path = '/api/v5/account/balance'
            body = ''
            response = self.query('GET', request_path, body)
            is_success = True if response.status_code == 200 else False
            return is_success
        except Exception as e:
            raise UserError(_("Test Connection Error: %s", e.args))

    def action_test_connection(self):
        is_success = self.test_okcoin_connection()
        type = (
            "success"
            if is_success
            else "danger"
        )
        messages = (
            "Everything seems properly set up!"
            if is_success
            else "Server credential is wrong. Please check credential."
        )
        title = _("Connection Testing")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": messages,
                "sticky": False,
                "type": type
            },
        }

    def action_activate(self):
        is_success = self.test_okcoin_connection()
        if is_success:
            # Get Conversion Rate
            #self.conversion_rate = self.action_get_conversion_rate_source()
            self.state = 'active'
            # Auto create Account Journal and POS Payment Method at the first Activate
            journal = self.env['account.journal'].search(
                [("use_okcoin_server", "=", True), ("type", "=", "bank"), ('company_id', '=', self.env.company.id)],
                limit=1)
            if not journal:
                journal = self.env['account.journal'].search(
                    [("type", "=", "bank"), ('company_id', '=', self.env.company.id)], limit=1)
                new_okcoin_server_journal = journal.copy()
                new_okcoin_server_journal.write({
                    'name': 'OKcoin Server',
                    'use_okcoin_server': True,
                    'code': 'OKcoin',
                    'okcoin_server_instance_id': self.id
                })
                new_okcoin_server_pos_payment_method = self.env['pos.payment.method'].create({
                    'name': 'OKcoin Server',
                    'company_id': self.env.company.id,
                    'journal_id': new_okcoin_server_journal.id
                }
                )
                new_okcoin_server_pos_payment_method = self.env['pos.payment.method'].create({
                    'name': 'OKcoin Server (Lightning)',
                    'company_id': self.env.company.id,
                    'journal_id': new_okcoin_server_journal.id
                }
                )

    def action_deactivate(self):
        self.state = 'inactive'


    def action_create_invoice_lightning(self, pos_payment_obj):  # creates lightning invoice
        try:
            invoiced_info = self.get_amount_sats(pos_payment_obj)  # gets the invoiced satoshi amount and conversion rate from get_amount_sats function
            amount_btc = invoiced_info['invoiced_sat_amount']/100000000 # converts sats to millisats as required by btcpayserver
            formatted_amount_btc = np.format_float_positional(amount_btc, trim='-')
            request_path = '/api/v5/asset/deposit-lightning?ccy=BTC&amt=' + str(formatted_amount_btc) + '&to=18'
            body = ''
            type = "GET"
            response = self.query(type, request_path, body)
            response_json = response.json()
            result = response_json.get('data')[0] if response.status_code == 200 else None
            result.update(invoiced_info)  # attach invoiced info (sat amount and conversion rate to API response
            return result  # returns merged resuls
        except Exception as e:
            _logger.info(" lightning invoice exception")
            raise UserError(_("Create OKcoin Lightning Invoice: %s", e.args))


    def action_get_conversion_rate(self): #obtains conversion rate from OKcoin server
        _logger.info('called get conversion rate')
        try:
            request_path = '/api/v5/market/ticker?instId=BTC-USD'
            body = ''
            type = "GET"
            response = self.query(type, request_path, body)
            response_json = response.json()
            result = response_json.get('data')[0].get('last') if response.status_code == 200 else None
            return result
        except Exception as e:
            _logger.info("conversion rate exception")
            raise UserError(_("Get Conversion Rate: %s", e.args))

    def get_amount_sats(self, pos_payment_obj): #obtains amount of satoshis to invoice by calling action_get_conversion_rate and and doing the math, returns dict of both values
        try:
            okcoin_conversion_rate = self.action_get_conversion_rate()
            amount_sats = round((float(pos_payment_obj.get('amount')) / float(okcoin_conversion_rate)) * 100000000, 0) #conversion to satoshis and rounding to one decimal
            invoiced_info = {'conversion_rate': okcoin_conversion_rate,
                             'invoiced_sat_amount': amount_sats
                             }
            return invoiced_info #return dictionary with results of both functions
        except Exception as e:
            _logger.info("amount sats exception")
            raise UserError(_("Get Millisat amount: %s", e.args))


    def action_check_lightning_invoice(self, lightning_invoice_id): #checks status of lightning invoices, only
        try:
            request_path = '/api/v5/asset/deposit-history?ccy=BTC' #+ lightning_invoice_id
            body = ''
            type = "GET"
            response = self.query(type, request_path, body)
            response_json = response.json()
            results = response_json.get('data') if response.status_code == 200 else None
            for result in results:
                if result.get('to') == lightning_invoice_id:
                    return result
            return {'state':'-1'}
        except Exception as e:
            raise UserError(_("Check OKcoin Lightning Invoice: %s", lightning_invoice_id, e.args))


    def action_sell(self, pos_payment_obj): #checks status of lightning invoices, only
        try:
            invoiced_sat_amount = pos_payment_obj.get('invoiced_sat_amount')
            convert_percent = self.convert_percent
            _logger.info(invoiced_sat_amount)
            conversion_sat_amount = (invoiced_sat_amount/100000000)*(convert_percent/100)
            _logger.info(conversion_sat_amount)
            request_path = '/api/v5/trade/order'
            body = {
                "instId":"BTC-USD",
                "tdMode":"cash",
                "clOrdId":"test",
                "side":"sell",
                "ordType":"market",
                "sz":str(conversion_sat_amount)} #minimum - 0.0001
            type = "POST"
            _logger.info(body)
            response = self.query(type, request_path, body)
            response_json = response.json()
            _logger.info(response_json)
            result = response_json.get('data')[0] if response.status_code == 200 else None
            _logger.info(result)
            if result.get('clOrdId') == "test":
                if result.get('sCode') == "0":
                    _logger.info(result)
                    return result
                else:
                    result = {'sCode':'-1', 'clOrdId':clOrdId}
                    _logger.info(result)
                    return result
        except Exception as e:
            _logger.info("sale order exception")
            raise UserError(_("Check OKcoin Lightning Invoice: %s", lightning_invoice_id, e.args))