# -*- coding: utf-8 -*-

{
    'name': "Atlas Product Creation",
    'summary': "Atlas Product Creation Restriction",
    'description': """
        Atlas Product Creation Security Restriction.
    """,
    'author': "Atlas-Blue",
    'category': "Product",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['product', 'base', 'hr_expense'],
    'license': "AGPL-3",

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
