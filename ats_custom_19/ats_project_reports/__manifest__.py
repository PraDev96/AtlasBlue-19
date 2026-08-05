# -*- coding: utf-8 -*-

{
    'name': "Project Reports",
    'summary': "Multiple Project Reports.",
    'description': """
        This module will Multiple Project Reports like Daily or within a date period.
        It will Print:
        - Daily Report
        - Weekly Report
        - Quarterly Report
        - Within the Date Period
    """,
    'author': "Atlas-Blue",
    'website': "https://www.atlasblue.me/en",
    'version': "19.0.1.0.0",
    'category': "Project",
    'depends': ['atlas_base', 'project', 'hr_timesheet'],
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'data': [
        'security/ir.model.access.csv',
        'wizards/project_report_wizard_views.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'application': False,
    'auto_install': False,
}
