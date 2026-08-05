# -*- coding: utf-8 -*-

{
    'name': "Quick Add Multiple Products on Sales in Odoo",
    'summary': "Quick Add mass Products on Sales Quick Add Products on Sales quick product add Quick add-to-cart multiple Products sale order line quick add mass Products sales order line quick add mass Products easy add mass Products on sales easy to add products.",
    'description': """
        This module add button Add Quick Product in sale order by click on it
        it will open one pop-up and allow you to add product from there.
        Odoo quick sale order line quick sales order line quick add product easy add product
        Odoo add product quickly on sales add product quick on sales order Quick add-to-cart Product on Sales
        odoo Quick add-to-cart Products on Sales in odoo quickly add product in sale order line Quick Add Product on Sale order line
        Odoo Sale order line Quick Add Product Easy to add product on sale order line quickly add product in order line
        Odoo Quick Add Product on order line Sale order line Quick Add Product Easy to add product on order line
        odoo quickly add product in sales order line Quick Add on Sales order line Sales order line Quick Add Product.
        Odoo Easy to add product on sales order line

        This module add button Add Quick multiple Products in sale order by click on it
        it will open one pop-up and allow you to add multiple Products from there.
        Odoo quick add multiple Products sale order line quick add multiple Products sales order line quick add multiple Products easy add multiple Products
        Odoo add multiple Products quickly on sales add multiple Products quick on sales order Quick add-to-cart multiple Products on Sales
        odoo Quick add-to-cart multiple Products on Sales in odoo quickly add multiple Products in sale order line Quick Add multiple Products on Sale order line
        Odoo Sale order line multiple Products Quick Add multiple Products Easy to add multiple Products on sale order line quickly add multiple Products in order line
        Odoo Quick Add multiple Products on order line Sale order line Quick Add multiple Products Easy to add multiple Products on order line
        odoo quickly add multiple Products in sales order line Quick Add multiple Products on Sales order line Sales order line Quick Add multiple Products
        Odoo Easy to add multiple Products on sales order line

        Odoo quick add mass Products sale order line quick add mass Products sales order line quick add mass Products easy add mass Products
        Odoo add mass Products quickly on sales add mass Products quick on sales order Quick add-to-cart mass Products on Sales
        odoo Quick add-to-cart mass Products on Sales in odoo quickly add mass Products in sale order line Quick Add mass Products on Sale order line
        Odoo Sale order line mass Products Quick Add mass Products Easy to add mass Products on sale order line quickly add mass Products in order line
        Odoo Quick Add mass Products on order line Sale order line Quick Add mass Products Easy to add mass Products on order line
        odoo quickly add mass Products in sales order line Quick Add mass Products on Sales order line Sales order line Quick Add mass Products
        Odoo Easy to add mass Products on sales order line.
    """,
    'author': "Atlas-Blue",
    'category': "Project",
    'version': "19.0.1.0.0",
    'website': "https://www.atlasblue.me/en",
    'depends': ['sale_management', 'atlas_base'],
    'license': "AGPL-3",

    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_quick_add_product.xml',
        'views/sale_order_view.xml',
    ],
    "images": ['static/description/Banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
