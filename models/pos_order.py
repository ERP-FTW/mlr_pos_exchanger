# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import requests
import json

class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    @api.model 
    def _process_order(self, order, draft, existing_order): #super function to update orders on okcoin journal, not sure if used
        print( '_process_order_process_order inherti')
        res = super()._process_order(order, draft, existing_order)
        pos_order_obj = self.search([('id', '=', res)])
        account_journal_obj = self.env['account.journal'].search([("use_okcoin_server","=",True)])
        pos_payment_method_obj = self.env['pos.payment.method'].search([("journal_id","in",account_journal_obj.ids)])
        return res
    
    @api.model
    def _payment_fields(self, order, ui_paymentline): #super function to update payment fields
        fields = super(PosOrderInherit, self)._payment_fields(
            order, ui_paymentline)
        pay_method = self.env['pos.payment.method'].search(
            [('id', '=', int(ui_paymentline['payment_method_id']))])
        if pay_method != False: # if there is a payment method
            if pay_method.journal_id.use_okcoin_server: # if the method is connected to the okcoin journal update the appropriate fields
                fields.update({
                    'okcoin_invoice_id': ui_paymentline.get('okcoin_invoice_id'),
                    'okcoin_payment_link': ui_paymentline.get('okcoin_payment_link'),
                    'invoiced_sat_amount': ui_paymentline.get('invoiced_sat_amount'),
                    'conversion_rate': ui_paymentline.get('conversion_rate'),
                })
        return fields
