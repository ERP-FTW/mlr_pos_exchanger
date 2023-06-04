odoo.define('pos_buttons.CustomButton', function(require) { //custombutton added to Action Pad that passes current order to okcoin for creation of invoice, attachment as payment line, and generation of QR code
'use strict';
    var rpc = require('web.rpc')
    const { Gui } = require('point_of_sale.Gui');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    var pos_model = require('point_of_sale.models');

    class CustomButton extends PosComponent {

        _btc_qr_code_process(order,response){
      /*
          Helper fuction to extract qrcode and process for receipt show
      */

        const codeWriter = new window.ZXing.BrowserQRCodeSvgWriter();
        let qr_code_svg = new XMLSerializer().serializeToString(codeWriter.write(response['okcoin_payment_link_qr_code'], 150, 150));
        //debugger;
        order.selected_paymentline.okcoin_payment_link_qr_code = "data:image/svg+xml;base64,"+ window.btoa(qr_code_svg)
        order.selected_paymentline.okcoin_payment_link = response['okcoin_payment_link']
        order.selected_paymentline.okcoin_invoice_id = response['okcoin_invoice_id']
        order.selected_paymentline.invoiced_sat_amount = response['invoiced_sat_amount']
        order.selected_paymentline.conversion_rate = response['conversion_rate']

        return order // updates payment line with okcoin fields

        }

        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        get currentOrder() {
           return this.env.pos.get_order();
        }
    async onClick() {
        var self = this;
        var current_id = this.currentOrder.uid;
        var order_ref = this.currentOrder.name;
        var subtotal = this.currentOrder.get_subtotal();
        var tax = this.currentOrder.get_total_tax();

        rpc.query({ //calls python method to create lightning invoice through controller
            route: "/okcoin/submitlightningorder",
            params: {
                partner_id: this.currentOrder.partner,
                amount: subtotal,
                uuid: this.currentOrder.uid,
                order_name: this.currentOrder.name,
              },
            })
            .then(function (result) {
              console.log("Done"+self.currentOrder.name);
              let json_result = JSON.parse(result); //get the updated json from models
              let paidOrder = self.currentOrder; //mark order as paid to add a payment line
              paidOrder.add_paymentline(self.env.pos.payment_methods.find(pm => pm.name == 'OKcoin Server (Lightning)') || ''); //add payment line with payment method of OKcoin server Lightning
              paidOrder = self._btc_qr_code_process(paidOrder,json_result); // create QR code from updated json
              //self.currentOrder.selected_paymentline.is_btc_split = false;
              self.currentOrder.selected_paymentline.okcoin_invoice_id = json_result['okcoin_invoice_id']; //attach okcoin invoice as id
              self.currentOrder.selected_paymentline.invoiced_sat_amount = json_result['invoiced_sat_amount']; //attach okcoin invoice as id

                // Save temp order to env.pos for global
              self.env.pos.tempSplitPaidOrder = paidOrder;
              //self.showScreen("BillScreen");
              alert('Current order: ' + self.currentOrder.name +'\nInvoice created: ' + json_result['okcoin_invoice_id']); //popup alert to inform user of invoice id created for current order
              //console.log(result);
              });


        }
    }
    CustomButton.template = 'CustomButton';

    ProductScreen.addControlButton({
        component: CustomButton,
    });

    Registries.Component.add(CustomButton);

    return CustomButton;
});