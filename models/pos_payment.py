from odoo import api, fields, models, _
from odoo.tools import formatLang, float_is_zero
from odoo.exceptions import ValidationError, UserError
try:
   import qrcode
except ImportError:
   qrcode = None
try:
   import base64
except ImportError:
   base64 = None
from io import BytesIO

class PosPayment(models.Model):
   _inherit = "pos.payment"
    
   okcoin_invoice_id = fields.Char('OKcoin Invoice ID')
   conversion_rate = fields.Float('Conversion rate')
   invoiced_sat_amount = fields.Float('Invoiced Satoshi Amount', digits=(12,4))
   okcoin_payment_link = fields.Char('OKcoin Payment Link')
   okcoin_payment_link_qr_code = fields.Binary('Okcoin QR Code', compute="_generate_qr") #binary field that is computed into a QR

   def _generate_qr(self): #called by compute field to change binary into QR
       for rec in self:
           if qrcode and base64:
               qr = qrcode.QRCode(
                   version=1,
                   error_correction=qrcode.constants.ERROR_CORRECT_L, #use low error correction to keep QR less complex and small
                   box_size=8,
                   border=4,
               )
               qr.add_data(rec.okcoin_payment_link)
               qr.make(fit=True)
               img = qr.make_image()
               temp = BytesIO()
               img.save(temp, format="PNG")
               qr_image = base64.b64encode(temp.getvalue())
               rec.update({'okcoin_payment_link_qr_code': qr_image}) #update the field with QR
           else:
               raise UserError(_('Necessary Requirements To Run This Operation Is Not Satisfied'))
   


