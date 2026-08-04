# -*- coding: utf-8 -*-

import os
from openpyxl import load_workbook
from odoo import models, fields, _, api


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def update_product_cost_from_xlsx(self):
        """
            This is for updating the product cost from the older database on
        """
        product_ids = self.env.context.get('active_ids')
        module_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(module_path, 'product_9_1_24.xlsx')

        workbook = load_workbook(filename=file_path, data_only=True)
        sheet = workbook.active

        headers = ["id", "default_code", "name", "price", "cost", "qty_on_hand", "cost_method"]
        data_list = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_data = dict(zip(headers, row))
            if int(row_data.get('id')) in product_ids:
                data_list.append(row_data)

        for row in data_list:
            product = self.env['product.product'].sudo().search([('id', '=', int(row.get('id')))], limit=1)
            if product.standard_price == 0 and row.get('cost'):
                product.write({
                    'standard_price': row.get('cost')
                })

        return "Product descriptions updated successfully."

