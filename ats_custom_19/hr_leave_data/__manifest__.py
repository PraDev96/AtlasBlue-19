# -*- coding: utf-8 -*-

{
    'name': "Leave Data",
    'description': """
        Leave Data
    """,
    'author': "Atlas-Blue",
    'category': "HR/Leave",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['boutiqaat_hr_base', 'hr_leave_custom', 'hr_leave_payment', 'hr_payroll'],
    'license': "AGPL-3",

    'data': [
        'data/hr_leave_data.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
