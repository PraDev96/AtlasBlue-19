# -*- coding: utf-8 -*-

{
    'name': "Atlas Report Custom Layout",
    'summary': "Atlas Report Custom Layout",
    'description': """
        Atlas Blue Custom Report Layout.
    """,
    'author': "Atlas-Blue",
    'category': "Hidden",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['web', 'base'],
    'license': "LGPL-3",

    'data': [
        'report/atlas_custom_report_layout.xml',
    ],
    'assets': {
        'web.assets_common': [
            "ats_report_custom_layout/static/src/scss/primary_variables.scss",
        ],
        'web.report_assets_common': [
            "ats_report_custom_layout/static/src/scss/primary_variables.scss",
        ],
        'web._assets_primary_variables': [
            "ats_report_custom_layout/static/src/scss/primary_variables.scss",
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
