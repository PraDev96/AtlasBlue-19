# -*- coding: utf-8 -*-

{
    'name': "Auto Project Progress Send",
    'summary': "Auto send Project Progress e-mail.",
    'description': """
        send Project Progress reminder automatic notifier auto Send Mail For Project Progress.
    """,
    'author': "Atlas-Blue",
    'category': "Project",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['project'],
    'license': "AGPL-3",

    'data': [
        'security/group.xml',
        'data/cron_job.xml',
        'data/project_email_template.xml',
        'report/project_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
