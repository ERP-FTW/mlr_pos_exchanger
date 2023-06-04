odoo.define("point_of_sale.CustomValidatePaymentScreen", function (require) {
    "use strict";
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");
    var rpc = require('web.rpc');
  
    const CustomValidatePaymentScreen = (PaymentScreen) =>
      class extends PaymentScreen {
        setup() {
          super.setup();
        }
        async validateOrder(isForceValidate) {
            for (let line of this.paymentLines) {
                console.log(line.name)
                if (line.name === "OKcoin Server (Lightning)") { //if OKcoin Lightning is the payment method upon clicking validate button call controller to check invoice status
                  //debugger
                  console.log(line.name +" " + this.currentOrder.name+ ""+ line.okcoin_invoice_id + " " +line.conversion_rate);
                    let route = '/okcoin/lightninginvoice'
                    let params = {
                                'invoice_id':line.okcoin_invoice_id,
                                'invoiced_sat_amount': line.invoiced_sat_amount,
                                'order_name': this.currentOrder.name,

                            }
                  try{
                      let receipt_data = await rpc.query({
                          route: route,
                          params: params
                      })
                      //debugger;
                      if (receipt_data){
                          var parsed_data=JSON.parse(receipt_data)
                          let is_payment_process = 'okcoin_invoice_id' in parsed_data
                           if (parsed_data.error){
                                throw new Error(parsed_data.error_message)
                            }
                             if (is_payment_process) {
                                 const codeWriter = new window.ZXing.BrowserQRCodeSvgWriter();
                                 let qr_code_svg = new XMLSerializer().serializeToString(codeWriter.write(parsed_data['okcoin_payment_link_qr_code'], 150, 150));
                                 //debugger;
                                 line.okcoin_payment_link_qr_code = "data:image/svg+xml;base64," + window.btoa(qr_code_svg)
                                 line.okcoin_payment_link = parsed_data['okcoin_payment_link']
                                 line.okcoin_invoice_id = parsed_data['okcoin_invoice_id']
                                 line.invoiced_sat_amount = parsed_data['invoiced_sat_amount']
                                 line.conversion_rate = parsed_data['conversion_rate']


                             }
                      }
                  
                  }
                  catch(error){
                      console.log(error)
                      console.log("Receipt Fetch Failed.")
                      this.showPopup("ErrorPopup", {
                            title: this.env._t("Payment Failed"),
                            body: this.env._t(error),
                        });
                      return;
                  }
              }
            }
          super.validateOrder(isForceValidate);
        }
      };
    // CustomValidatePaymentScreen.template = "point_of_sale.CustomValidatePaymentScreenTemplate";
  
    Registries.Component.extend(PaymentScreen, CustomValidatePaymentScreen);
  
    return CustomValidatePaymentScreen;
  });
  