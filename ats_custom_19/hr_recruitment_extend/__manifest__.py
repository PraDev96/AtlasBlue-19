# -*- coding: utf-8 -*-

{
    'name': "Employees Applications Extend",
    'summary': "Employees Recruitment Extend",
    'description': """
        Employees Recruitment Extend.
    """,
    'author': "Atlas-Blue",
    'category': "HR/Recruitment",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['base', 'hr_recruitment'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'view/hr_recruitment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
