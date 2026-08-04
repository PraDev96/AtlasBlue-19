# -*- coding: utf-8 -*-

{
    'name': "HR Penalty",
    'summary': "HR Penalty",
    'description': """
        HR Penalty.
    """,
    'author': "Atlas-Blue",
    'category': "HR/Payroll",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['boutiqaat_hr_payslip'],
    'license': "AGPL-3",

    'data': [
        'security/hr_penalty_security.xml',
        'security/ir.model.access.csv',
        'data/hr_penalty_data.xml',
        'report/penalty_report_template_view.xml',
        'wizard/penalty_done_wizard_view.xml',
        'views/employee_view.xml',
        'views/hr_penalty_view.xml',
        'views/penalty_report_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
