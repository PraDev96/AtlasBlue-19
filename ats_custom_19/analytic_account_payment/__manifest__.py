# -*- coding: utf-8 -*-

{
    'name': "Analytic Account on Payments",
    'summary': "Analytic Account on Payments",
    'author': "Atlas-Blue",
    'category': "Accounting/Accounting",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['account', 'analytic', 'stock_account'],

    'data': [
        'views/account_analytic_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
