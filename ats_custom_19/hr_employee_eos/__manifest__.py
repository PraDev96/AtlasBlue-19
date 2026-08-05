# -*- coding: utf-8 -*-

{
    'name': "Employee End Of Service",
    'author': "Atlas-Blue",
    'category': "HR/EOS",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'license': "LGPL-3",
    'depends': ['hr_payroll', 'hr_default', 'hr_holidays', 'hr_contract', 'boutiqaat_reports'],

    'data': [
        'security/ir.model.access.csv',
        'data/hr_data.xml',
        'data/data.xml',
        'data/cron.xml',
        'views/hr_views.xml',
        # "views/res_config_views.xml",
        'views/report_eos.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
