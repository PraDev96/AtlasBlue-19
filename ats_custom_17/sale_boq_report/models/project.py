# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    service_installation_detail_ids = fields.One2many('installation.completion.detail', 'project_id', string="Project Service Installations Details")

    def get_electrical_product_details(self):
        """Compute electrical load for all products in the sale order, including nested packages."""

        def collect_products(product, qty, collected_data):
            """Recursively collect all products and their quantities, calculating their electrical loads."""
            if not product:
                return

            # Add the product to the collected data or update its quantity and electric load
            if product.id in collected_data:
                collected_data[product.id]['product_uom_qty'] += qty
                # collected_data[product.id]['electrical_load'] += product.electrical_load * qty
            else:
                product_name = product.name
                if product.phase == 'one':
                    product_name += ' - 1 Ph'
                elif product.phase == 'three':
                    product_name += ' - 3 Ph'
                collected_data[product.id] = {
                    'product_id': product.id,
                    'name': product_name,
                    'product_uom_qty': qty,
                    'electrical_load': product.electrical_load,
                }

            # Traverse package lines for nested products
            for package_line in product.pack_ids:
                collect_products(package_line.product_id, package_line.qty_uom * qty, collected_data)

        # Dictionary to collect data
        collected_data = {}

        # Process each product in the sale order lines
        so_orders = self.env['sale.order'].search([('project_id', '=', self.id), ('state', '=', 'sale')])
        sale_order_lines = so_orders.mapped('order_line').filtered(lambda sol: sol.product_uom_qty != 0)
        for line in sale_order_lines:
            collect_products(line.product_id, line.product_uom_qty, collected_data)

        # Convert collected data to a list of dictionaries for report compatibility
        return [el_line for el_line in list(collected_data.values()) if el_line['electrical_load']] if list(collected_data.values()) else []

    def get_filtered_order_lines(self):
        merged_order_lines = {}
        merged_products = {}
        so_orders = self.env['sale.order'].search(
            [('project_id', '=', self.id), ('state', 'in', ['sale', 'done'])]).filtered(lambda x: sum([y.product_uom_qty for y in x.order_line]) != 0)
        so_lines = so_orders.mapped('order_line')
        for line in so_lines:
            product_id = line.product_id.id
            if line.product_id.is_pack:
                for pack_line in line.product_id.pack_ids:
                    product_id = pack_line.product_id
                    if product_id.electrical_load > 0:
                        product_name = pack_line.product_id.name
                        if product_id.phase == 'one':
                            product_name += ' - 1 Ph'
                        elif product_id.phase == 'three':
                            product_name += ' - 3 Ph'
                        if product_id in merged_order_lines:
                            merged_order_lines[product_id]['product_uom_qty'] += (pack_line.qty_uom * line.product_uom_qty)
                        else:
                            merged_order_lines[product_id] = {
                                'product_id': product_id.id,
                                'name': product_name,
                                'product_uom_qty': pack_line.qty_uom * line.product_uom_qty,
                                'electrical_load': product_id.electrical_load
                            }
            elif not line.product_id.is_pack and line.product_id.electrical_load > 0:
                product_name = line.product_id.name
                if line.product_id.phase == 'one':
                    product_name += ' - 1 Ph'
                elif line.product_id.phase == 'three':
                    product_name += ' - 3 Ph'
                if product_id in merged_order_lines:
                    merged_order_lines[product_id]['product_uom_qty'] += line.product_uom_qty
                else:
                    merged_order_lines[product_id] = {
                        'product_id': product_id,
                        'name': product_name,
                        'product_uom_qty': line.product_uom_qty,
                        'electrical_load': line.product_id.electrical_load
                    }

        merged_so_line = list(merged_order_lines.values())
        for Product in merged_so_line:
            product_id = Product['product_id']
            quantity = Product['product_uom_qty']
            electrical_load = Product['electrical_load']
            product_name = Product['name']
            if product_id in merged_products:
                merged_products[product_id]['product_uom_qty'] += quantity
            else:
                merged_products[product_id] = {
                    'product_id': product_id,
                    'name': product_name,
                    'product_uom_qty': quantity,
                    'electrical_load': electrical_load
                }

        final_products = []
        for product in merged_products.values():
            if product['product_uom_qty'] > 0:
                final_products.append(product)

        return sorted(final_products, key=lambda x: x['product_id'])

    def update_installation_details(self):
        projects = self.env['project.project'].sudo().search([('id', 'in', self.env.context.get('active_ids', []))])
        service_list = ['Embedded Pipe Installation', 'Waterproof Installation', 'Tile Installation', 'Equipment Installation']
        for project in projects.filtered(lambda p: p.opportunity_type in ('project', 'renovation')):
            if not project.service_installation_detail_ids:
                project.write({
                    'service_installation_detail_ids': [(0, 0, {'name': service}) for service in service_list]
                })

    @api.model_create_multi
    def create(self, vals_list):
        result = super(Project, self).create(vals_list)
        for vals in vals_list:
            if result.opportunity_type in ('project', 'renovation') or vals.get('opportunity_type') in ('project', 'renovation'):
                service_list = ['Embedded Pipe Installation', 'Waterproof Installation', 'Tile Installation', 'Equipment Installation']
                result['service_installation_detail_ids'] = [(0, 0, {'name': service}) for service in service_list]

        return result


class ProjectInstallationCompletionDetail(models.Model):
    _name = 'installation.completion.detail'
    _description = "Project Installation Completion Detail"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('project.project', string="Project")
    project_name = fields.Char(related='project_id.name', string="Project Name", readonly=True, translate=True)
    name = fields.Char(string="Service Name", required=True)
    expected_start_date = fields.Date(string="Expected / Start Date")
    installation_completion_date = fields.Date(string="Installation Completion Date")
    warranty_end_date = fields.Date(string="Warranty End Date")
    is_goods_ordered = fields.Boolean(string="Is Ordered")

    def action_view_project(self):
        action = self.env['ir.actions.actions']._for_xml_id('project.open_view_project_all_config')
        if self.project_id:
            form_view = [(self.env.ref('project.edit_project').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.project_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
