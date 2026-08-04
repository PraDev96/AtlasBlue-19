# -*- coding: utf-8 -*-

{
    'name': "Partner Employee Link",
    'author': "Atlas-Blue",
    'category': "HR",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['hr'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_partner_employee_link_view.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
