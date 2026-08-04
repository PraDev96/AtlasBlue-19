# -*- coding: utf-8 -*-

{
    'name': "Project - Sale - Contract",
    'summary': "Project Sale Contract",
    'description': """
        Project Sale Contract Details.
    """,
    'author': "Atlas-Blue",
    'category': "Sales",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['project', 'sales_team', 'sale'],
    'license': "AGPL-3",
    'external_dependencies': {
        'python': ['deep-translator'],
    },

    'data': [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
        'views/sale_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
