# -*- coding: utf-8 -*-

{
    'name': "Atlas Checklist",
    'description': 'Atlas Checklist',
    'author': "Atlas-Blue",
    'category': "Project",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['base', 'project'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'reports/checklist_report.xml',
        'views/project_checklist_views.xml',
        'views/project_project_views.xml',
        'views/menuitem_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
