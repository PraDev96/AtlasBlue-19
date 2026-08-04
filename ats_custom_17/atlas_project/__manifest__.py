# -*- coding: utf-8 -*-

{
    'name': "Atlas Blue Project",
    'author': "Atlas-Blue",
    'category': "Extra Tool",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['helpdesk', 'atlas_base', 'utm', 'base', 'sale_subscription', 'project'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        # 'data/ir_cron.xml',
        'reports/invoice_report.xml',
        'reports/sale_quotation_report.xml',
        'views/crm_views.xml',
        'views/helpdesk_views.xml',
        'views/sale_order_views.xml',
        'views/subscription_view.xml',
        'views/call_reason_views.xml',
        'views/call_receive_views.xml',
        'views/sale_portal_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
