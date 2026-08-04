# -*- coding: utf-8 -*-

{
    'name': "Partner Address Details",
    'author': "Atlas-Blue",
    'category': "Contact",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['base', 'account', 'contacts'],

    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
