# -*- coding: utf-8 -*-

{
    'name': "Fleet Handover",
    'summary': "Fleet Handover.",
    'description': """
        Fleet Handover Letter.
    """,
    'author': "Atlas-Blue",
    'category': "HR/Fleet",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['hr_atlas_blue'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'data/fleet_handover_data.xml',
        'report/fleet_handover_report.xml',
        'report/fleet_handover_templates.xml',
        'report/vehicle_assign_date_pdf_report.xml',
        'views/fleet_handover_views.xml',
        'wizard/vehicle_assign_date_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
