# -*- coding: utf-8 -*-

{
    'name': "Leave Payment",
    'author': "Atlas-Blue",
    'category': "HR/Leave",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['hr_holidays', 'payslip_emp_inputs', 'boutiqaat_hr_base'],

    'data': [
        'views/hr_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
