{
    "name": "MI Lightning Rod Point of Sale - Exchanger",
    "summary": "MI Lightning Rod Point of Sale - Exchanger",
    "author": "ERP-FTW",
    "website": "https://www.milightningrod.com",
    "category": "Point of Sale",
    "version": "1.0",
    "depends": ["point_of_sale", "account", "pos_restaurant"],
    "data": [
        "security/ir.model.access.csv",
        "views/okcoin_account_journal.xml",
        "views/pos_payment.xml",
        "views/okcoin_instance.xml",
    ],
    'assets': {
        'point_of_sale.assets': [
            'mlr_pos_exchanger/static/src/js/models.js',
            'mlr_pos_exchanger/static/src/js/ValidatePaymentScreen.js',
            'mlr_pos_exchanger/static/src/js/create_invoice.js',
            'mlr_pos_exchanger/static/src/xml/OrderReceipt.xml',
            'mlr_pos_exchanger/static/src/xml/ClosePosPopup.xml',
            'mlr_pos_exchanger/static/src/js/OKClosePosPopup.js',
            'mlr_pos_exchanger/static/src/xml/create_invoice.xml'
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "OPL-1",
}
