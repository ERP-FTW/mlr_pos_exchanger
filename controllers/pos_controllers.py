# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import http
from odoo.http import request
import json
import logging
import requests

_logger = logging.getLogger(__name__)

class OKcoinController(http.Controller):
    
    @http.route('/okcoin/submitlightningorder', type='json', auth='user', csrf=False, methods=['POST']) #creates a lightning invoice based on current order
    def okcoin_lightning_payment_link(self, **kw):
        try:
            okcoin_invoice = request.env['okcoin.instance'].search([('state', '=', 'active')], limit=1).action_create_invoice_lightning(kw) #calls function to create invoice and passes kw
            okcoin_invoice_id = okcoin_invoice.get('invoice') #retrieves invoice id
            okcoin_payment_link = okcoin_invoice.get('invoice') #retrieves invoice itself
            conversion_rate = okcoin_invoice.get('conversion_rate') #retrieves conversion rate of transaction
            invoiced_sat_amount = okcoin_invoice['invoiced_sat_amount'] #retrieves invoiced satoshi amount
            return json.dumps({ #returns information that will be placed on bill receipt and stored in database if ultimately paid
                'error':False,
                'okcoin_payment_link_qr_code': "lightning:"+okcoin_payment_link, #adds lightning prefix for QR code
                'okcoin_payment_link': okcoin_payment_link, #the invoice itself
                'okcoin_invoice_id': okcoin_invoice_id,
                'invoiced_sat_amount': invoiced_sat_amount,
                'conversion_rate': conversion_rate
            })
        except Exception as e: #error if invoice cannot be created
            _logger.info('submit lightning exception')
            return json.dumps({
                 'error':True,
                 'error_message': "Internal Server Error!!"
            })
    @http.route('/okcoin/lightninginvoice', type='json', auth='user', csrf=False, methods=['POST']) #checks status of the lightning transaction
    #three possible statuses: Paid, Unpaid, and Expired. Status of an existing invoice will be displayed if unpaid or expired
    def okcoin_check_lightning_invoice(self, **kw):

        try:
            okcoin_invoice = request.env['okcoin.instance'].search([('state', '=', 'active')], limit=1).action_check_lightning_invoice(kw.get('invoice_id')) #calls function to get invoice status, should also check that invoice id is not blank
            _logger.info('okcoin_invoice')
            _logger.info(okcoin_invoice)
            _logger.info('state')
            _logger.info(okcoin_invoice['state'])

            if okcoin_invoice['state'] == '2':
                sale_order = request.env['okcoin.instance'].search([('state', '=', 'active')], limit=1).action_sell(kw)  # calls function to get invoice status, should also check that invoice id is not blank
                _logger.info('sale order made')
                return json.dumps({
                    'error': False,
                    'invoice_status': 'Paid'
                })
            elif okcoin_invoice['state'] == '1':
                return json.dumps({
                    'error': True,
                    'invoice_status': 'Uncredited',
                    'error_message': "Lightning: payment not credited yet, check again in a minute."
                })
            elif okcoin_invoice['state'] == '-1':
                return json.dumps({
                    'error': True,
                    'error_message': "Lightning: payment not found, check with customer and/or manager."
                })
            else:
                return json.dumps({
                    'error': True,
                    'error_message': "Lightning: unknown error with invoice. Check with manager or technical support"
                })
        except Exception as e: #if an invoice status cannot be obtained, currently assumed to be due to no invoice having been created
             return json.dumps({
                 'error': True,
                 'error_message': "Lightning: invoice likely not created. Create invoice through invoice button or split screen."
            })