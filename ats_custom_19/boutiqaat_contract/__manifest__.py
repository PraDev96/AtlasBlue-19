# -*- coding: utf-8 -*-

{
    'name': "Boutiqaat HR Contract",
    'author': "Atlas-Blue",
    'category': "Human Resources",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['hr_contract', 'boutiqaat_hr_base'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/upd_contract_views.xml',
        'views/contract_views.xml',
        'views/working_schedule_views.xml',
        'wizard/increment_contract_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
