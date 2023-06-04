odoo.define('point_of_sale.OKcoinClosePosPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');
    const { identifyError } = require('point_of_sale.utils');
    const { ConnectionLostError, ConnectionAbortedError} = require('@web/core/network/rpc_service')
    const { useState } = owl;

    class OKcoinClosePosPopup extends ClosePosPopup {
        setup() {
            super.setup();
            useListener('click', this.onClick);
            this.manualInputCashCount = false;
            this.cashControl = this.env.pos.config.cash_control;
            this.closeSessionClicked = false;
            this.moneyDetails = null;
            Object.assign(this, this.props.info);
            this.state = useState({
                displayMoneyDetailsPopup: false,
            });
            Object.assign(this.state, this.props.info.state);
        }
        //@override
        async BTC() {
            alert("BTC-USD button clicked");
            console.log("BTC-USD button clicked");
            }
        }

    OKcoinClosePosPopup.template = 'OKcoinClosePosPopup';
    Registries.Component.add(OKcoinClosePosPopup);

    return OKcoinClosePosPopup;
});
