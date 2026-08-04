# -*- coding: utf-8 -*-

{
    'name': "Employees Violation",
    'summary': "Employees Violation",
    'description': """
        Employees Violations.
    """,
    'author': "Atlas-Blue",
    'category': "HR",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['boutiqaat_hr_payslip'],
    'license': "AGPL-3",

    'data': [
        'security/hr_violation_security.xml',
        'security/ir.model.access.csv',
        'data/hr_violation_data.xml',
        'view/hr_violation_view.xml',
        'view/employee_view.xml',
        'wizard/violation_done_wizard_view.xml',
        'view/violation_report_view.xml',
        'report/violation_report_template_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
