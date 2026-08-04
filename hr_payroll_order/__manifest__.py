# -*- coding: utf-8 -*-

{
    'name': "Payroll Extend",
    'summary': "Payroll Extend",
    'description': """
        HR Payroll Order.
    """,
    'author': "Atlas-Blue",
    'category': "HR/Payroll",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['hr_payroll'],
    'license': "AGPL-3",

    'data': [
        'views/hr_payslip_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
