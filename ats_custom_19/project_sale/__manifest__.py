# -*- coding: utf-8 -*-

{
    'name': "Project Sale",
    'author': "Atlas-Blue",
    'category': "Project",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['project', 'sale_management', 'sale', 'sale_project', 'account', 'sale_purchase', 'hr', 'stock',
                'hr_expense', 'calendar', 'sale_timesheet', 'fleet', 'analytic', 'project_team', 'sale_subscription'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/data.xml',
        'views/views.xml',
        'views/sale_view.xml',
        'views/project_views.xml',
        'views/calendar_views.xml',
        'views/report_sale_quote.xml',
        'views/report_visit_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
