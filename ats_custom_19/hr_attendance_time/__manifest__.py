# -*- coding: utf-8 -*-

{
    'name': "HR Attendance More Fields",
    'author': "Atlas-Blue",
    'category': "Human Resources",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['hr_attendance', 'boutiqaat_hr_base', 'hr_holidays'],

    'data': [
        'security/ir.model.access.csv',
        'views/attendance_views.xml',
        'views/views.xml',
        'wizard/attendance_wiz_views.xml',
        'wizard/imp_attendance_views.xml',
        'wizard/imp_contract_views.xml',
        'wizard/att_calendar_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
