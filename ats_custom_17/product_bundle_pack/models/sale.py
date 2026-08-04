# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################


from odoo import SUPERUSER_ID
from datetime import timedelta
from odoo import models, _, api
from collections import defaultdict
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()

        for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
            def check_product(x):
                for rec in line.product_id.pack_ids:
                    if x == rec.product_id:
                        return x

            if line.qty_delivered_method == 'stock_move':
                qty = 0.0
                flag = False
                count = 0
                done_list = []
                deliver_list = []
                move_list = []
                products = []
                filtered = []
                picking_ids = self.env['stock.picking'].search([('origin', '=', line.order_id.name)])
                for pick in picking_ids:
                    for move_is in pick.move_ids_without_package:
                        if move_is.product_id not in products:
                            products.append(move_is.product_id)

                pro = filter(check_product, products)
                for product in pro:
                    filtered.append(product)

                for pick in picking_ids:
                    for move_is in pick.move_ids_without_package:
                        if move_is.product_id in filtered:
                            if move_is.pack_id in line.product_id.pack_ids:
                                move_list.append(move_is.product_uom_qty)
                                done_list.append(move_is.quantity)

                stock_move = self.env['stock.move'].search([('origin', '=', line.order_id.name)])
                if line.product_id.is_pack == True:
                    list_of_sub_product = []
                    for product_item in line.product_id.pack_ids:
                        list_of_sub_product.append(product_item.product_id)
                    for move in stock_move:
                        if count == 0:
                            if move.state == 'done' and move.product_uom_qty == move.quantity:
                                flag = True
                                for picking in picking_ids:
                                    for move_is in picking.move_ids_without_package:
                                        if sum(move_list) == 0:
                                            pass
                                        else:
                                            deliver_qty = (line.product_uom_qty * sum(done_list)) / sum(move_list)
                                            line.qty_delivered = int(deliver_qty)
                                            deliver_list.append(line.qty_delivered)

                            elif move.state == 'confirmed':
                                flag = 'confirmed'
                                count = count + 1
                                done_list.append(move.quantity)
                                for picking in picking_ids:
                                    for move_is in picking.move_ids_without_package:
                                        if sum(move_list) == 0:
                                            pass
                                        else:
                                            deliver_qty = (line.product_uom_qty * sum(done_list)) / sum(move_list)
                                            line.qty_delivered = int(deliver_qty)
                                            deliver_list.append(line.qty_delivered)

                    print(line.qty_delivered)
                else:
                    outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
                    for move in outgoing_moves:
                        if move.state != 'done':
                            continue
                        qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')

                    for move in incoming_moves:
                        if move.state != 'done':
                            continue
                        qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')

                    line.qty_delivered = qty

    @api.onchange('product_id', 'product_uom_qty')
    def _compute_qty_to_deliver(self):
        res = super(SaleOrderLine, self)._compute_qty_to_deliver()
        for i in self:
            if i.product_id.is_pack:
                if i.product_id.type == 'product':
                    warning_mess = {}
                    for pack_product in i.product_id.pack_ids:
                        qty = i.product_uom_qty
                        if qty * pack_product.qty_uom > pack_product.product_id.virtual_available:
                            warning_mess = {
                                'title': _('Not enough inventory!'),
                                'message': ('You plan to sell %s but you only have %s %s available, and the total quantity to sell is %s !' % (
                                qty, pack_product.product_id.virtual_available, pack_product.product_id.name, qty * pack_product.qty_uom))
                            }
                            return {'warning': warning_mess}
            else:
                return res

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
            Launch procurement group run method with required/custom fields genrated by a
            sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
            depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        pro_values = {}
        from pprint import pprint

        for line in self:
            line = line.with_company(line.company_id)
            if line.state != 'sale' or line.product_id.type not in ('consu', 'product'):
                continue

            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            # values = line._prepare_procurement_values(group_id=group_id)
            # print ("___ line: ", line.product_id.id, line.product_uom_qty)
            if line.product_id.pack_ids:
                date_planned = line.order_id.date_order + timedelta(days=line.customer_lead or 0.0) - timedelta(days=line.order_id.company_id.security_lead)
                bundle_lines = line.get_recursive_items(line.product_id, date_planned, group_id, line.route_id.id, line.product_uom_qty)
                # return values
                for b_line in bundle_lines:
                    pid = b_line['product_id']
                    # product_qty = line.product_uom_qty - qty
                    product_qty = b_line['product_qty']

                    order = b_line.get('order')
                    product = b_line.get('product')
                    # location = b_line.pop('location')
                    line_uom = b_line.get('uom')

                    quant_uom = product.uom_id
                    _, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
                    # print("___ bline : ", product.id, product_qty)
                    b_line.update({'procurement_uom': procurement_uom})
                    # procurements.append(self.env['procurement.group'].Procurement(
                    #     product, product_qty, procurement_uom,
                    #     location,
                    #     order.origin, order.name, order.company_id, b_line))
                    if pid in pro_values.keys():
                        pro_values[pid]['product_qty'] += product_qty
                    else:
                        pro_values.update({pid: b_line})
            else:
                pid = line.product_id.id
                # values.update({
                #     'company_id': self.order_id.company_id,
                #     'group_id': group_id,
                #     'sale_line_id': self.id,
                #     'date_planned': date_planned,
                #     'route_ids': self.route_id,
                #     'warehouse_id': self.order_id.warehouse_id or False,
                #     'partner_dest_id': self.order_id.partner_shipping_id,
                #     'partner_id': self.order_id.partner_shipping_id.id,
                #     'company_id': self.order_id.company_id,
                # })
                product_qty = line.product_uom_qty - qty

                line_uom = line.product_uom
                quant_uom = line.product_id.uom_id
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
                if pid in pro_values.keys():
                    pro_values[pid]['product_qty'] += product_qty
                else:
                    values = line._prepare_procurement_values(group_id=group_id)
                    # pprint(values)
                    values.update({
                        'uom': line_uom,
                        'product_qty': product_qty,
                        'origin': line.order_id.name,
                        'product': line.product_id,
                        'location': line.order_id.partner_shipping_id.property_stock_customer,
                        'order': line.order_id,
                        'procurement_uom': procurement_uom,
                    })
                    pro_values.update({pid: values})
                # procurements.append(self.env['procurement.group'].Procurement(
                #     line.product_id, product_qty, procurement_uom,
                #     line.order_id.partner_shipping_id.property_stock_customer,
                #     line.name, line.order_id.name, line.order_id.company_id, values))
        # print ("___ procurements: ")
        for pid, value in pro_values.items():
            # pprint(value)
            # pid = pro.product_id.id
            # print ("__ pro : ", pid, pro.product_qty)
            # # new_procs.setdefault(pro.product_id.id, None)
            # if pid in new_procs.keys():
            #     new_procs[pid].product_qty += pro.product_qty
            # else:
            #     new_procs.update({pid: pro})
            procurements.append(self.env['procurement.group'].Procurement(
                value['product'], value['product_qty'], value['procurement_uom'],
                value['order'].partner_shipping_id.property_stock_customer,
                value['origin'], value['order'].name, value['order'].company_id, value))

        if procurements:
            self.env['procurement.group'].run(procurements)

        # procurement_jit
        orders = list(set(x.order_id for x in self))
        for order in orders:
            reassign = order.picking_ids.filtered(
                lambda x: x.state == 'confirmed' or (x.state in ['waiting', 'assigned'] and not x.printed))
            if reassign:
                # Trigger the Scheduler for Pickings
                reassign.action_confirm()
                reassign.action_assign()

        return True

    # def _action_launch_stock_rule(self, previous_product_uom_qty=False):
    #     """
    #     Launch procurement group run method with required/custom fields genrated by a
    #     sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
    #     depending on the sale order line product rule.
    #     """
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     procurements = []
    #     errors = []
    #     for line in self:
    #         if line.state != 'sale' or not line.product_id.type in ('consu','product'):
    #             continue
    #         qty = line._get_qty_procurement(previous_product_uom_qty)
    #         if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
    #             continue

    #         group_id = line._get_procurement_group()
    #         if not group_id:
    #             group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
    #             line.order_id.procurement_group_id = group_id
    #         else:
    #             # In case the procurement group is already created and the order was
    #             # cancelled, we need to update certain values of the group.
    #             if line.product_id.pack_ids:
    #                 values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
    #                 for val in values:
    #                     try:
    #                         pro_id = self.env['product.product'].browse(val.get('product_id'))
    #                         stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
    #                         product_uom_obj = self.env['uom.uom'].browse(val.get('product_uom'))
    #                         procurements.append(self.env['procurement.group'].Procurement(
    #                             pro_id, 0, product_uom_obj,
    #                             line.order_id.partner_shipping_id.property_stock_customer,
    #                             val.get('name'), val.get('origin'), line.order_id.company_id, val
    #                         ))
    #                     except UserError as error:
    #                         errors.append(error.name)
    #             else:
    #                 updated_vals = {}
    #                 if group_id.partner_id != line.order_id.partner_shipping_id:
    #                     updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
    #                 if group_id.move_type != line.order_id.picking_policy:
    #                     updated_vals.update({'move_type': line.order_id.picking_policy})
    #                 if updated_vals:
    #                     group_id.write(updated_vals)

    #         if line.product_id.pack_ids:
    #             values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
    #             for val in values:
    #                 try:
    #                     pro_id = self.env['product.product'].browse(val.get('product_id'))
    #                     stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
    #                     product_uom_obj = self.env['uom.uom'].browse(val.get('product_uom'))
    #                     procurements.append(self.env['procurement.group'].Procurement(
    #                         pro_id, val.get('product_qty'), product_uom_obj,
    #                         line.order_id.partner_shipping_id.property_stock_customer,
    #                         val.get('name'), val.get('origin'), line.order_id.company_id, val
    #                     ))
    #                 except UserError as error:
    #                     errors.append(error.name)
    #         else:
    #             values = line._prepare_procurement_values(group_id=group_id)
    #             product_qty = line.product_uom_qty - qty

    #             line_uom = line.product_uom
    #             quant_uom = line.product_id.uom_id
    #             product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
    #             procurements.append(self.env['procurement.group'].Procurement(
    #                 line.product_id, product_qty, procurement_uom,
    #                 line.order_id.partner_shipping_id.property_stock_customer,
    #                 line.name, line.order_id.name, line.order_id.company_id, values))
    #     if procurements:
    #         self.env['procurement.group'].run(procurements)
    #     module = self.env['ir.module.module'].sudo().search([('state', '=', 'installed'),('name', '=', 'procurement_jit')],limit=1)
    #     if module:
    #         orders = list(set(x.order_id for x in self))
    #         for order in orders:
    #             reassign = order.picking_ids.filtered(lambda x: x.state=='confirmed' or (x.state in ['waiting', 'assigned'] and not x.printed))
    #             if reassign:
    #                 reassign.action_assign()
    #     return True

    def get_recursive_items(self, product, date_planned, group_id, line_route_ids, pack_qty):
        values = []
        for item in product.pack_ids:
            if item.product_id.pack_ids:
                result = self.get_recursive_items(item.product_id, date_planned, group_id, line_route_ids, item.qty_uom * pack_qty)
                values += result
            else:
                values.append({
                    'name': item.product_id.name,
                    'origin': self.order_id.name,
                    'date_planned': date_planned,
                    'product_id': item.product_id.id,
                    'product_qty': item.qty_uom * pack_qty,
                    'product_uom': item.uom_id and item.uom_id.id,
                    'company_id': self.order_id.company_id,
                    'group_id': group_id,
                    'sale_line_id': self.id,
                    'warehouse_id': self.order_id.warehouse_id and self.order_id.warehouse_id,
                    'location_id': self.order_id.partner_shipping_id.property_stock_customer.id,
                    'route_ids': self.route_id and line_route_ids or [],
                    'partner_dest_id': self.order_id.partner_shipping_id,
                    'partner_id': self.order_id.partner_shipping_id.id,
                    'pack_id': item.id,

                    'uom': item.uom_id,
                    'product': item.product_id,
                    'location': self.order_id.partner_shipping_id.property_stock_customer,
                    'order': self.order_id,
                })

        return values

    # def _prepare_procurement_values(self, group_id):
    #     res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
    #     # values = []
    #     date_planned = self.order_id.date_order\
    #         + timedelta(days=self.customer_lead or 0.0) - timedelta(days=self.order_id.company_id.security_lead)
    #     if self.product_id.pack_ids:
    #         line_route_ids = self.env['stock.location.route'].browse(self.route_id.id)
    #         values = self.get_recursive_items(self.product_id, date_planned, group_id, line_route_ids, self.product_uom_qty or 1)
    #         return values
    #     else:
    #         res.update({
    #             'company_id': self.order_id.company_id,
    #             'group_id': group_id,
    #             'sale_line_id': self.id,
    #             'date_planned': date_planned,
    #             'route_ids': self.route_id,
    #             'warehouse_id': self.order_id.warehouse_id or False,
    #             'partner_dest_id': self.order_id.partner_shipping_id,
    #             'partner_id': self.order_id.partner_shipping_id.id,
    #             'company_id': self.order_id.company_id,
    #         })
    #     return res


class ProcurementRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_pull(self, procurements):
        moves_values_by_company = defaultdict(list)
        mtso_products_by_locations = defaultdict(list)

        # To handle the `mts_else_mto` procure method, we do a preliminary loop to
        # isolate the products we would need to read the forecasted quantity,
        # in order to to batch the read. We also make a sanitary check on the
        # `location_src_id` field.
        for procurement, rule in procurements:
            if not rule.location_src_id:
                msg = _('No source location defined on stock rule: %s!') % (rule.name,)
                raise UserError(msg)

            if rule.procure_method == 'mts_else_mto':
                mtso_products_by_locations[rule.location_src_id].append(procurement.product_id.id)

        # Get the forecasted quantity for the `mts_else_mto` procurement.
        forecasted_qties_by_loc = {}
        for location, product_ids in mtso_products_by_locations.items():
            products = self.env['product.product'].browse(product_ids).with_context(location=location.id)
            forecasted_qties_by_loc[location] = {product.id: product.free_qty for product in products}

        # Prepare the move values, adapt the `procure_method` if needed.
        for procurement, rule in procurements:
            procure_method = rule.procure_method
            if rule.procure_method == 'mts_else_mto':
                qty_needed = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_id)
                qty_available = forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id]
                if float_compare(qty_needed, qty_available, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:
                    procure_method = 'make_to_stock'
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
                else:
                    procure_method = 'make_to_order'

            move_values = rule._get_stock_move_values(*procurement)
            if procurement[-1].get('pack_id'):
                move_values.update({'pack_id': procurement[-1].get('pack_id')})

            move_values['procure_method'] = procure_method
            moves_values_by_company[procurement.company_id.id].append(move_values)

        for company_id, moves_values in moves_values_by_company.items():
            from pprint import pprint
            # pprint(moves_values)
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            moves = self.env['stock.move'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(moves_values)
            # Since action_confirm launch following procurement_group we should activate it.
            moves._action_confirm()

        return True

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        if product_id.pack_ids:
            for item in product_id.pack_ids:
                result.update({
                    'product_id': item.product_id.id,
                    'product_uom': item.uom_id and item.uom_id.id,
                    'product_uom_qty': item.qty_uom,
                    'origin': origin,
                    'pack_id': item.id,
                })

        return result
