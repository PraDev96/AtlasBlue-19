# -*- coding: utf-8 -*-

{
    'name': "Employees Accommodation",
    'summary': "Employees Accommodation",
    'description': """
        HR Employees Accommodation Details.
    """,
    'author': "Atlas-Blue",
    'category': "HR",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['fleet', 'hr_fleet', 'hr_atlas_blue', 'fleet_driver'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'data/hr_accommodation_data.xml',
        'wizards/import_accommodation_wizard_view.xml',
        'wizards/import_employee_number_wizard_view.xml',
        'wizards/import_employee_leave_wizard_view.xml',
        'wizards/import_employee_link_project_wizard_view.xml',
        'views/hr_accommodation_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
