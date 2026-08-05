# -*- coding: utf-8 -*-

{
    'name': "Boutiqaat HR Base",
    'author': "Atlas-Blue",
    'category': "Human Resources",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['hr_default', 'hr_holidays'],

    'data': [
        'security/ir.model.access.csv',
        'data/boutiqaat_hr_base_data.xml',
        'views/views.xml',
        'views/hr_emp_discount_views.xml',
        'views/hr_views.xml',
        'views/hr_holidays_views.xml',
        'views/hr_mail_notification_view.xml',
        'views/res_bank_view.xml',
        'wizard/import_employee_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
