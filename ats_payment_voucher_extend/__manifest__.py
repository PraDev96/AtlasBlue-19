# -*- coding: utf-8 -*-

{
    'name': "Account Payment Voucher Extend",
    'summary': "EAccount Payment Voucher Extend",
    'description': """
        Account Payment Receipt/Voucher Report Extend.
    """,
    'author': "Atlas-Blue",
    'category': "Accounting/Accounting",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['account'],
    'license': "AGPL-3",

    'data': [
        'reports/payment_receipt_template.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
