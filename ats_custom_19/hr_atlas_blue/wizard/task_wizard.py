# -*- coding: utf-8 -*-

import io
import base64
import xlsxwriter
from odoo import models, fields


class Branch(models.Model):
    _name = 'fleet.branch'
    _description = "Fleet Branch"


class FieldServiceConsumedWizard(models.TransientModel):
    _name = 'field.service.consumed.wizard'
    _description = "Field Service Consumed Wizard"

    filename = fields.Binary()
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    product_ids = fields.Many2many('product.product', string="Products")
    product_category_ids = fields.Many2many('product.category', string="Product Category")
    partner_ids = fields.Many2many('res.partner', string="Customers")
    branch_ids = fields.Many2many('fleet.branch', string="Branch")
    service_type = fields.Selection([('product', 'Product'), ('category', 'Category')], string="Type", default='product', required=True)

    def get_lang_format(self):
        lang_code = self.env.user.lang or 'en_US'
        return self.env['res.lang']._lang_get(lang_code).date_format

    def get_lang_time_format(self):
        lang_code = self.env.user.lang or 'en_US'
        return self.env['res.lang']._lang_get(lang_code).time_format

    def get_date_format(self, dt, date_format=False):
        if not date_format:
            date_format = self.get_lang_format()

        return dt.strftime(date_format) if dt else ''

    def get_datetime_format(self, dt, datetime_format=False):
        if not datetime_format:
            datetime_format = self.get_lang_format() + ' ' + self.get_lang_time_format()

        return dt.strftime(datetime_format) if dt else ''

    def _compute_lines_data(self):
        def if_fsm_material_line(sale_line_id, task):
            is_not_timesheet_line = sale_line_id.product_id != task.project_id.timesheet_product_id
            is_not_empty = sale_line_id.product_uom_qty != 0
            is_not_service_from_so = sale_line_id != task.sale_line_id
            return all([is_not_timesheet_line, is_not_empty, is_not_service_from_so])

        sale_domain = [
            ('sale_order_id', '!=', False),
            # ('sale_order_id.date_order', '>=', self.start_date),
            # ('sale_order_id.date_order', '<=', self.end_date)
            ('planned_date_begin', '>=', self.planned_date_begin),
            ('planned_date_end', '<=', self.planned_date_end),
        ]
        if self.partner_ids:
            sale_domain.append(('partner_id', 'in', self.partner_ids.ids))

        if self.branch_ids:
            sale_domain.append(('branch_id', 'in', self.branch_ids.ids))

        tasks = self.env['project.task'].search(sale_domain)

        all_material_sale_lines = self.env['sale.order.line']
        data_dict = []

        for task in tasks:
            material_sale_lines = task.sale_order_id.order_line.filtered(lambda sol: if_fsm_material_line(sol, task))
            all_material_sale_lines |= material_sale_lines

        if self.product_ids:
            all_material_sale_lines = all_material_sale_lines.filtered(lambda line: line.product_id in self.product_ids)

        if self.product_category_ids:
            all_material_sale_lines = all_material_sale_lines.filtered(lambda line: line.product_id.categ_id in self.product_category_ids)

        for line in all_material_sale_lines:
            if line.product_id.type != 'service':
                product_id = line.product_id.id
                task_ids = line.order_id.tasks_ids
                product_lines = []
                for item in data_dict:
                    if product_id == item['product_id']:
                        product_lines.append(item)

                #         ◦ Customer
                #         ◦ Customer Location
                #         ◦ Branch
                #         ◦ Customer Vehicle
                #         ◦ Vehicle Model
                #         ◦ Start date and End Date
                if not product_lines:
                    data_dict.append({
                        'product_id': line.product_id.id,
                        'product': line.product_id.name,
                        'int_ref': line.product_id.default_code,
                        'sale_price': line.price_unit or 0.0,
                        'cost': line.product_id.standard_price or 0.0,
                        'qty': line.product_uom_qty,
                        'task_id': task_ids.id if task_ids else False,
                        'task_name': task_ids.name if task_ids else '',
                        'partner': task_ids.partner_id.name if task_ids and task_ids.partner_id else '',
                        'customer_location': task_ids.customer_location.name if task_ids else '',
                        'branch': task_ids.branch_id.name if task_ids and task_ids.branch_id else '',
                        'vehicle_number': task_ids.vehicle_id.name if task_ids and task_ids.vehicle_id else '',
                        'model_number': task_ids.model_id.name if task_ids and task_ids.model_id else '',
                        'start_date': task_ids.planned_date_begin if task_ids else '',
                        'end_date': task_ids.planned_date_end if task_ids else '',
                        'title': task_ids.name if task_ids else '',
                        'title_tags': ", ".join(task_ids.title_ids.mapped('name')) if task_ids else '',
                    })
                else:
                    flag = False
                    if task_ids:
                        for product_line in product_lines:
                            if product_line['task_id'] == task_ids.id:
                                product_line['qty'] = product_line['qty'] + + line.product_uom_qty
                                flag = True

                    if not flag:
                        data_dict.append({
                            'product_id': line.product_id.id,
                            'product': line.product_id.name,
                            'int_ref': line.product_id.default_code,
                            'sale_price': line.price_unit or 0.0,
                            'cost': line.product_id.standard_price or 0.0,
                            'qty': line.product_uom_qty,
                            'task_id': task_ids.id if task_ids else False,
                            'task_name': task_ids.name if task_ids else '',
                            'partner': task_ids.partner_id.name if task_ids and task_ids.partner_id else '',
                            'customer_location': task_ids.customer_location.name if task_ids else '',
                            'branch': task_ids.branch_id.name if task_ids and task_ids.branch_id else '',
                            'vehicle_number': task_ids.vehicle_id.name if task_ids and task_ids.vehicle_id else '',
                            'model_number': task_ids.model_id.name if task_ids and task_ids.model_id else '',
                            'start_date': task_ids.planned_date_begin if task_ids else '',
                            'end_date': task_ids.planned_date_end if task_ids else '',
                            'title': task_ids.name if task_ids else '',
                            'title_tags': ", ".join(task_ids.title_ids.mapped('name')) if task_ids else '',
                        })

        return data_dict

    def action_xlsx(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        data_dict = self._compute_lines_data()
        sheet = workbook.add_worksheet('Field Service Consumed Product')
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 2, 20)
        sheet.set_column(3, 3, 50)
        sheet.set_column(4, 9, 20)

        # sheet style
        heading = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        cell = workbook.add_format({'bold': True})

        currency_format = workbook.add_format({'num_format': '#,###0.000'})

        # Main Info
        sheet.merge_range(0, 1, 0, 5, 'Field Service Consumed Product', heading)
        # # Header

        col = 0

        sheet.write(3, col, 'Internal Reference', cell)
        col += 1
        sheet.write(3, col, 'Product', cell)
        col += 1
        sheet.write(3, col, 'Sale Price', cell)
        col += 1
        sheet.write(3, col, 'Cost Price', cell)
        col += 1
        sheet.write(3, col, 'Material Quantity', cell)
        col += 1
        sheet.write(3, col, 'Title of Field Service Task', cell)
        col += 1
        sheet.write(3, col, 'Customer', cell)
        col += 1
        sheet.write(3, col, 'Customer Location', cell)
        col += 1
        sheet.write(3, col, 'Branch', cell)
        col += 1
        sheet.write(3, col, 'Customer Vehicle', cell)
        col += 1
        sheet.write(3, col, 'Vehicle Model', cell)
        col += 1
        sheet.write(3, col, 'Start date', cell)
        col += 1
        sheet.write(3, col, 'End Date', cell)
        col += 1
        sheet.write(3, col, 'Title', cell)
        col += 1
        sheet.write(3, col, 'Title Tags', cell)

        row, col = 4, 0
        for line in data_dict:
            row += 1
            col = 0
            sheet.write(row, col, line['int_ref'] or '')
            col += 1
            sheet.write(row, col, line['product'] or '')
            col += 1
            sheet.write(row, col, line['sale_price'] or 0.0, currency_format)
            col += 1
            sheet.write(row, col, line['cost'] or 0.0, currency_format)
            col += 1
            sheet.write(row, col, line['qty'] or 0.0, currency_format)
            col += 1
            sheet.write(row, col, line['task_name'] or '')
            col += 1
            sheet.write(row, col, line['partner'] or '')
            col += 1
            sheet.write(row, col, line['customer_location'] or '')
            col += 1
            sheet.write(row, col, line['branch'] or '')
            col += 1
            sheet.write(row, col, line['vehicle_number'] or '')
            col += 1
            sheet.write(row, col, line['model_number'] or '')
            col += 1
            sheet.write(row, col, self.get_datetime_format(line['start_date']) or '')
            col += 1
            sheet.write(row, col, self.get_datetime_format(line['end_date']) or '')
            col += 1
            sheet.write(row, col, line['title'] or '')
            col += 1
            sheet.write(row, col, line['title_tags'] or '')

        workbook.close()
        file_base = base64.b64encode(output.getvalue())
        output.close()
        self.filename = file_base
        file_name = 'Consume Product Report.xlsx'

        return {
            'target': 'new',
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s/filename/%s?download=true' % (self._name, self.id, file_name),
        }
