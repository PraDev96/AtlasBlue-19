# -*- coding: utf-8 -*-

{
    'name': "Boutiqaat HR Payslip",
    'author': "Atlas-Blue",
    'category': "HR/Payslip",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['hr_payroll', 'hr_contract', 'payslip_emp_inputs', 'boutiqaat_hr_base', 'boutiqaat_contract', 'hr_attendance_time', 'ohrms_loan', 'hr_leave_payment'],

    'data': [
        'security/ir.model.access.csv',
        'data/boutiqaat_hr_payslip_india_data.xml',
        'data/boutiqaat_hr_payslip_kuwait_data.xml',
        'data/boutiqaat_hr_payslip_uae_data.xml',
        'data/kuwait_hourly_data.xml',
        'data/kuwait_daily_data.xml',
        'data/other_rules.xml',
        'views/payslip_report.xml',
        'views/report_payslip.xml',
        'views/payslip_views.xml',
        'views/structure_type_views.xml',
        'wizard/wizard_payslip_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
