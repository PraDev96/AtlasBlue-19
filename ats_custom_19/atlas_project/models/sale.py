# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_image = fields.Binary(string="Image", related="product_id.image_1920")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_image = fields.Boolean(string="Show Product Image in Print ?", tracking=True)
    is_subtotal = fields.Boolean(string="Show Subtotal in Print ?", tracking=True)
    title = fields.Char(string="Title")
    summary = fields.Html(string="Summary")
    day_ids = fields.Many2many('week.days', string="Days Of Visit", tracking=True, related="opportunity_id.day_ids")
    is_contract_signed = fields.Boolean(string="Contract Signed ?", tracking=True)
    contract_sign_user_id = fields.Many2one('res.users', string="Contract Signed By", tracking=True)
    contract_sign_dt = fields.Datetime(string="Contract Sign", tracking=True)
    number_of_days_per_week = fields.Integer(string="Number Of Visits Per Week", related="opportunity_id.number_of_days_per_week", tracking=True)

    def action_manual_sent(self):
        self.ensure_one()
        self.message_post(body="Manually Sent")
        self.write({'state': 'sent'})

    def action_sign_contract(self):
        self.ensure_one()
        attachments = self.env['ir.attachment'].sudo().search_count([('res_model', '=', 'sale.order'), ('res_id', '=', self.id)])
        if not attachments:
            raise UserError(_("Please upload the singed contract in attachments."))

        self.write({
            'is_contract_signed': True,
            'contract_sign_user_id': self.user_id.id,
            'contract_sign_dt': fields.Datetime.now()
        })

    def duplicate_me(self):
        self.ensure_one()
        new_order = self.copy({'order_line': False})
        new_order.write({
            'order_line': [(0, 0, {
                'name': line.name,
                'sequence': line.sequence,
                'discount': line.discount,
                'price_unit': line.price_unit,
                'product_uom': line.product_uom.id,
                'purchase_price': line.purchase_price,
                'product_uom_qty': line.product_uom_qty,
                'product_id': line.product_id.id or False,
                'display_type': line.display_type or False,
            }) for line in self.order_line]
        })
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['views'] = [(False, 'form')]
        action['res_id'] = new_order.id

        return action
