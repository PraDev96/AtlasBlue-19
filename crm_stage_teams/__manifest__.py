# -*- coding: utf-8 -*-

{
    'name': "CRM Stage Teams",
    'summary': "CRM Stage Teams.",
    'description': """
        Add Team in CRM Stage.
    """,
    'author': "Atlas-Blue",
    'category': "Project",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['crm', 'project_team'],
    'license': "AGPL-3",

    'data': [
        'views/crm_stage_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
