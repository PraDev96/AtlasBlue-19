# -*- coding: utf-8 -*-

{
    'name': "Civil Project Checklist",
    'summary': "Civil Project Checklist.",
    'description': """
        This will create Project Checklists for civil Projects according to the Checklist Tasks from Project Template.
    """,
    'category': "Project",
    'author': "Atlas-Blue",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['web', 'portal', 'project', 'atlas_base', 'atlas_checklist', 'atlas_blue_timesheet_portal', 'ats_hr_timesheet_limit', 'ats_report_custom_layout'],
    'license': "LGPL-3",

    'data': [
        'security/checklist_security.xml',
        'data/ir_sequence_data.xml',
        'reports/civil_checklist_report.xml',
        'reports/civil_checklist_template.xml',
        'views/project_task_views.xml',
        'views/project_checklist_views.xml',
        'views/civil_checklist_portal_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ats_civil_project_checklist/static/src/js/civil_checklist_portal.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
