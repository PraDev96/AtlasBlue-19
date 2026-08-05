# -*- coding: utf-8 -*-

{
    'name': "Stock Force Availability",
    'summary': "Stock Force Availability",
    'description': """
        Stock Force Availability.
    """,
    'author': "Atlas-Blue",
    'category': "Operations/Inventory",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['stock'],
    'license': "AGPL-3",

    'data': [
        'security/stock_force_availability_security.xml',
        'views/stock_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
