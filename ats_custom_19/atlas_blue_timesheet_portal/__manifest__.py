# -*- coding: utf-8 -*-

{
    'name': "Timesheet Portal (editable)",
    'description': "Fill in Timesheet via the Portal",
    'author': "Atlas-Blue",
    'category': "Website",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': [
        'base', 'crm', 'project', 'portal', 'website', 'hr_timesheet', 'atlas_base', 'hr_payroll',
        'hr_atlas_blue', 'project_sale', 'atlas_checklist', 'boutiqaat_contract', 'project_enterprise'
    ],
    'license': "AGPL-3",

    'data': [
        'security/hr_timesheet_portal_security.xml',
        'security/ir.model.access.csv',
        'views/portal.xml',
        'views/project_view.xml',
        'views/hr_contract_view.xml',
        'views/portal_invisible.xml',
        'views/employee_cost_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'atlas_blue_timesheet_portal/static/src/js/sweetalert.min.js',
            'atlas_blue_timesheet_portal/static/src/js/project_portal.js',
            'atlas_blue_timesheet_portal/static/src/scss/timesheet_portal.scss',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}
