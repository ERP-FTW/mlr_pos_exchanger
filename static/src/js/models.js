odoo.define('mlr_point_of_sale.models', function (require) { // super point of sale models

    var models = require('point_of_sale.models');
    var { Order, Payment } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosOKcoinServerPayment = (Payment) => class PosOKcoinPayment extends Payment {
        
        constructor(obj, options) {
            super(...arguments);
            this.okcoin_invoice_id = this.okcoin_invoice_id;
            this.okcoin_payment_link_qr_code = this.okcoin_payment_link_qr_code;
            this.okcoin_payment_link = this.okcoin_payment_link;
            this.invoiced_sat_amount = this.invoiced_sat_amount;
            this.conversion_rate = this.conversion_rate;
        }
        //@override
        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.okcoin_invoice_id = this.okcoin_invoice_id;
            json.okcoin_payment_link_qr_code = this.okcoin_payment_link_qr_code;
            json.okcoin_payment_link = this.okcoin_payment_link;
            json.invoiced_sat_amount = this.invoiced_sat_amount;
            json.conversion_rate = this.conversion_rate;
            return json;
        }
        //@override
        init_from_JSON(json) {
            //debugger;
            super.init_from_JSON(...arguments);
            this.okcoin_invoice_id = json.okcoin_invoice_id;
            this.okcoin_payment_link_qr_code = json.okcoin_payment_link_qr_code;
            this.okcoin_payment_link = json.okcoin_payment_link;
            this.invoiced_sat_amount = json.invoiced_sat_amount;
            this.conversion_rate = json.conversion_rate;
        }
    }
    Registries.Model.extend(Payment, PosOKcoinServerPayment);

});
