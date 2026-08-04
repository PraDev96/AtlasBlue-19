# -*- coding: utf-8 -*-

{
    'name': "Project Completion History",
    'summary': "Track Project Completion History of Total Completion(%) changes.",
    'description': """
        This module logs whenever the Total Completion(%) of a project changes due to task progress updates.
        It tracks:
        - Who made the change
        - The task that caused the change
        - Previous value
        - New updated value
        - The difference
        - Weightage Pulled Amount
    """,
    'author': "Atlas-Blue",
    'website': "https://www.atlasblue.me/en",
    'version': "17.0.1.0.0",
    'category': "Project",
    'depends': ['project', 'atlas_base', 'hr_atlas_blue'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_completion_history_views.xml',
        'views/project_task_views.xml',
        'views/project_views.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'application': False,
    'auto_install': False,
}
