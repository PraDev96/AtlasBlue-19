# -*- coding: utf-8 -*-

{
    'name': "Product Brand",
    'summary': "Product Brand",
    'description': """
        Product Branding.
    """,
    'author': "Atlas-Blue",
    'category': "Product",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['sale_stock'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
