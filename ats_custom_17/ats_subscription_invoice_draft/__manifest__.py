# -*- coding: utf-8 -*-

{
    'name': "Subscription Invoice Draft",
    'summary': "To avoid the auto post the invoice for subscription sale orders.",
    'description': """
        This is used to avoid the auto post the Invoices for Subscription Sale Orders.
    """,
    'author': "Atlas-Blue",
    'category': "Sales/Subscriptions",
    'version': "17.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['sale_subscription'],
    'license': "AGPL-3",

    'data': [
        'views/sale_subscription_plan_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
