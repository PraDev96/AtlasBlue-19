# -*- coding: utf-8 -*-

{
    'name': "HR Payslip Employee Inputs",
    'author': "Atlas-Blue",
    'category': "HR",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['hr_payroll', 'hr_payroll_account'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/input_data.xml',
        'views/emp_inputs_views.xml',
        'views/employee_views.xml',
        'views/bulk_input_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
