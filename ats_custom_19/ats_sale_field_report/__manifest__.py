# -*- coding: utf-8 -*-

{
    'name': "Sale Hide Field Report",
    'summary': "Hide Quantity, Price, and the Whole row in the report",
    'description': """
        Hide the columns like Quantity, Price, and the whole Row in the report.
    """,
    'author': "Atlas-Blue",
    'category': "Sales",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['sale', 'atlas_base', 'sale_management', 'product_package'],
    'license': "AGPL-3",

    'data': [
        'reports/sale_hide_field_report.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
