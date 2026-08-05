# -*- coding: utf-8 -*-

{
    'name': "Sales: Recurring Invoice",
    'summary': "Sales: Recurring Invoice",
    'description': """
        Sales: Recurring Invoice.
    """,
    'author': "Atlas-Blue",
    'category': "Account",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['account'],
    'license': "AGPL-3",

    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/sale_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
