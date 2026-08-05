# -*- coding: utf-8 -*-

{
    'name': "Sale BOQ Report",
    'summary': "Sale BOQ Report",
    'description': """
        Sale BOQ Report.
    """,
    'author': "Atlas-Blue",
    'category': "Sales",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['sale', 'project', 'atlas_base'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'views/boq_report.xml',
        'views/report_project_equip.xml',
        'views/sale_report_templates.xml',
        'views/swimming_pool_latter.xml',
        'views/electrical_load.xml',
        'views/project_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
