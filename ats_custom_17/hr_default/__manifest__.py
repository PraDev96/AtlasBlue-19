# -*- coding: utf-8 -*-

{
    'name': "Employees Default Details",
    'author': "Atlas-Blue",
    'category': "HR",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['hr_contract'],

    'data': [
        'security/ir.model.access.csv',
        'view/hr_default_view.xml',
        'view/res_company_view.xml',
        'view/article_type_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
