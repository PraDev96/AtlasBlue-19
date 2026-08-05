# -*- coding: utf-8 -*-

{
    'name': "Attachment Extend",
    'summary': 'Attachment Extend',
    'description': """
        Attachment Additional Details.
    """,
    "author": "AtlasBlue",
    'version': '19.0.1.0.0',
    "website": "https://www.atlasblue.me/en",
    'category': 'Sales',
    'depends': ['base', 'atlas_base', 'project', 'contacts', 'attachment_zipped_download'],
    "license": "OPL-1",

    'data': [
        'views/ir_attachment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'application': False,
}
