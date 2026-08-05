# -*- coding: utf-8 -*-

{
    'name': "Shipping Move Entry",
    'summary': "Shipping Move Entry",
    'description': """
        Shipping Move Entry.
    """,
    'author': "Atlas-Blue",
    'category': "Inventory/Inventory",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['stock', 'stock_account', 'stock_landed_costs'],
    'license': "AGPL-3",

    'data': [
        'views/stock_picking_view.xml',
        'views/stock_move_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
