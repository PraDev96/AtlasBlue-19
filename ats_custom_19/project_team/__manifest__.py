# -*- coding: utf-8 -*-

{
    'name': "Project - Set Team and members",
    'author': "Atlas-Blue",
    'summary': "Project Team Management",
    'category': "Project Management",
    'website': "https://www.atlasblue.me/en",
    'version': "19.0.1.0.0",
    'license': "AGPL-3",
    'depends': ['project', 'crm'],

    'data': [
        'views/project_team_view.xml',
    ],
    'images': [
        'static/description/ProjectTeam.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
