# -*- coding: utf-8 -*-

{
    'name': "Leave Approve",
    'author': "Atlas-Blue",
    'category': "HR/Leave",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['hr_holidays', 'hr_attendance_time', 'hr_leave_payment', 'resource'],

    'data': [
        'security/hr_leave_custom_security.xml',
        'security/ir.model.access.csv',
        'data/hr_leave_data.xml',
        'views/hr_views.xml',
        'wizard/resume_work_wizard_view.xml',
        'wizard/import_hr_leave_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
