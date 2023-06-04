odoo.define("point_of_sale.OKClosePosPopup", function (require) {
    "use strict";

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const ClosePosPopup = require("point_of_sale.ClosePosPopup");
    const { useListener } = require("@web/core/utils/hooks");
    const rpc = require('web.rpc');
    const Registries = require('point_of_sale.Registries');
    const { identifyError } = require('point_of_sale.utils');
    const { ConnectionLostError, ConnectionAbortedError} = require('@web/core/network/rpc_service')
    const { useState } = owl;

    class OKcoinClosePosPopup extends ClosePosPopup {

      setup() {
        super.setup();
        useListener('click', this.onClick);}

    async BTC() {
        alert("BTC-USD button clicked");
        console.log("OKcoin button clicked");
        //rpc.query({
        //    route: "/okcoin/sell-session",
        //    params: {
        //    amount: 0.01
        //    }
        //})
        //.then(function (result) {
        //console.log("OKcoin then function")

         //alert(`Converted invoice created ${result}`);
          //})


    }}

    OKClosePosPopup.template = 'OKClosePosPopup';
    Registries.Component.add(OKClosePosPopup);

    return OKClosePosPopup;
      });