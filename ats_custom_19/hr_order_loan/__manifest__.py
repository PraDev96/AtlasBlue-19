# -*- coding: utf-8 -*-

{
    'name': "Order Food Loan",
    'author': "Atlas-Blue",
    'category': "HR/Payslip",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['ohrms_loan'],

    'data': [
        'security/hr_loan_security.xml',
        'view/hr_loan_view.xml',
        'view/loan_report_view.xml',
        'report/loan_report_template_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
