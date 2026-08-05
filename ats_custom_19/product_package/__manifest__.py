# -*- coding: utf-8 -*-

{
    'name': "Product Package",
    'summary': "Product Package",
    'author': "Atlas-Blue",
    'category': "Sale",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['sale', 'partner_address'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'views/package_config_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
