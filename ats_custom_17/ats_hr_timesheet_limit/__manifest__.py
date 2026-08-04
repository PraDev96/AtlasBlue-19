# -*- coding: utf-8 -*-

{
    'name': "Timesheet Daily Limit",
    'summary': "Restrict Timesheet Entries based on a Daily Maximum Limit.",
    'description': """
        This allows Administrators to set a Maximum Daily Limit for Timesheet Entries.
        Users will be Restricted from adding more hours than the configured Limit.
    """,
    'author': "Atlas-Blue",
    'category': "Services/Timesheet",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['project', 'hr_timesheet', 'atlas_blue_timesheet_portal'],
    'license': "LGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'security/timesheet_limit_security.xml',
        'wizard/overtime_confirm_wizard_views.xml',
        'views/portal_templates.xml',
        'views/hr_timesheet_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ats_hr_timesheet_limit/static/src/js/timesheet_portal_limit.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
