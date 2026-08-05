# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Product Bundle Pack in Odoo",
    "category": 'Sales',
    "summary": 'Combine two or more product pack product kit product bundle product pack item on product combo product on sale bundle product delivery bundle product pack kit combine product combine product variant bundle item pack sales bundle delivery pack bundle',
    "description": """
	BrowseInfo developed a new odoo/OpenERP module apps.
	This module is use to
    odoo create Product Bundle Product Pack Bundle Pack of Product Combined Product pack odoo
    odoo Product Pack Custom Combo Product Bundle Product Customized product Group product odoo
    odoo Custom product bundle Custom Product Pack odoo combo product pack combo product combo bundle pack combo bundle product pack
    odoo combo product pack multiple product pack group product pack choice odoo
    odoo product Pack Price Product Bundle pack price product Bundle Discount product Bundle Offer bundle price

    """,
    "sequence": 1,
    "author": "Browseinfo",
    "website": "https://www.browseinfo.in",
    "version": '19.0.1.0.0',
    'license': "LGPL-3",
    "depends": ['sale', 'product', 'stock', 'sale_stock', 'sale_management', 'purchase'],

    "data": [
        'wizard/product_bundle_wizard_view.xml',
        'views/product_view.xml',
        'security/ir.model.access.csv'
    ],
    "price": 35,
    "currency": 'EUR',
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ['static/description/Banner.png'],
}
