# -*- coding: utf-8 -*-

{
    'name': "Timesheet with the Attendance",
    'summary': "Timesheet app with the attendance app",
    'description': """
        Timesheet app with the attendance app.
    """,
    'author': "Services/Timesheet",
    'category': "Operations/Inventory",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['account', 'hr_timesheet', 'timesheet_grid'],
    'license': "AGPL-3",

    'data': [
        'views/account_analytic_line_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
