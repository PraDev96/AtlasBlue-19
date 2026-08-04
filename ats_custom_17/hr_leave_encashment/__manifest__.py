# -*- coding: utf-8 -*-

{
    'name': "HR Leave Encasement",
    'author': "Atlas-Blue",
    'category': "HR",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['payslip_emp_inputs'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/emp_leave_encashment_views.xml',
        'views/leave_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
