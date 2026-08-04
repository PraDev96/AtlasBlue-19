# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vehicle_ok = fields.Boolean(string="Can be Vehicle?")
    accessory_ok = fields.Boolean(string="Can be Accessory?")
    plate_number = fields.Char(string="Plate Number", related='product_variant_ids.plate_number', readonly=False)


class Product(models.Model):
    _inherit = 'product.product'

    def _compute_fleet(self):
        Fleet = self.env['fleet.vehicle']
        for rec in self:
            fleets = Fleet.search([('product_id', '=', rec.id)])
            rec.fleet_count = len(fleets)

    model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    license_plate = fields.Char(string="License Plate")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    fleet_count = fields.Integer(string="Fleet Count", compute='_compute_fleet')
    plate_number = fields.Char(string="Plate Number")

    @api.model_create_multi
    def create(self, vals_list):
        FleetVehicle = self.env['fleet.vehicle']
        products = super(Product, self).create(vals_list)
        for product in products:
            if product.vehicle_ok and not self.env.context.get('from_fleet', False):
                vehicle = FleetVehicle.with_context(from_product=True).create({
                    'name': product.name,
                    'product_id': product.id,
                    'model_id': product.model_id.id,
                    'license_plate': product.license_plate,
                })
                product.write({'vehicle_id': vehicle.id})

        return products

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        FleetVehicle = self.env['fleet.vehicle']
        fleet_vehicle_id = self.env.context.get('from_fleet_vehicle_id')
        if fleet_vehicle_id:
            fleetvehicle = FleetVehicle.browse(fleet_vehicle_id)
            product_ids = fleetvehicle.move_ids.mapped('product_id').ids
            args += [('id', 'in', product_ids)]

        if self.env.context.get('from_service_line'):
            args += [('type', '=', 'product'), ('free_qty', '>', 0.0)]

        return super(Product, self).name_search(name=name, args=args, operator=operator, limit=limit)

    def action_fleet(self):
        self.ensure_one()
        action = self.env.ref('fleet.fleet_vehicle_action').sudo().read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        action['context'] = {'default_product_id': self.id}

        return action
