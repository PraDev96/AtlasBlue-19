# -*- coding: utf-8 -*-

{
    'name': "Atlas Security",
    'summary': "Atlas Security",
    'description': """
        Atlas Security.
    """,
    'author': "Atlas-Blue",
    'category': "Extra Tool",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['base', 'mail', 'calendar'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
