# -*- coding: utf-8 -*-

{
    'name': "Account based on Opportunity Type",
    'description': """
        Atlas Blue COA set Opportunity Type in Accounts while Customer Invoice
    """,
    'author': "Atlas-Blue",
    'category': "Account",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['atlas_base'],

    'data': [
        'views/account_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
