# -*- coding: utf-8 -*-

{
    'name': "HR Timesheet Cutoff",
    'summary': "HR Timesheet Cutoff",
    'description': """
        Turn-off the timesheet if it is exceed 8.5 hours.
    """,
    'author': "Atlas-Blue",
    'category': "Human Resources/Employees",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['project'],
    'license': "LGPL-3",

    'data': [
        # 'data/timesheet_cutoff_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
