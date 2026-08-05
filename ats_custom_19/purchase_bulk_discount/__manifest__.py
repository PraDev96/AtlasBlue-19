# -*- coding: utf-8 -*-

{
    'name': "Purchase Bulk Discount",
    'summary': "Purchase Bulk Discount",
    'description': """
        Purchase Bulk Discount.
    """,
    'author': "Atlas-Blue",
    'category': "Purchase",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['purchase'],
    'license': "AGPL-3",

    'data': [
        'views/purchase_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
