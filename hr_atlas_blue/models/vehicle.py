# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class VehicleMake(models.Model):
    _name = 'vehicle.make'
    _description = 'Vehicle Make'

    name = fields.Char(string="Name", required=True)
    image = fields.Binary(string="Image")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []

        domain = []
        if self.env.context.get('owner_id'):
            vehicles = self.env['motor.vehicle'].search([('owner_id', '=', self.env.context['owner_id'])], limit=limit)
            make_ids = vehicles.mapped('make_id')
            domain.append(('id', 'in', make_ids.ids))

        return super(VehicleMake, self).name_search(name, args + domain, operator, limit)


class VehicleModel(models.Model):
    _name = 'vehicle.model'
    _description = 'Vehicle Model'

    name = fields.Char(string="Model", required=True)
    model_year = fields.Char(string="Model Year")
    make_id = fields.Many2one('vehicle.make', string="Make")


class MotorBodyStyle(models.Model):
    _name = 'vehicle.bodystyle'
    _description = "Vehicle Body-Style"

    name = fields.Char(string="Name", required=True)
    make_id = fields.Many2one('vehicle.make', string="Make")


class MotorVehicle(models.Model):
    _name = 'motor.vehicle'
    _description = "Motor Vehicle"

    def get_year(self):
        return [(str(a), a) for a in list(range(1980, 2100))]

    partner_id = fields.Many2one('res.partner', string="Partner")
    name = fields.Char(string="Plate No")
    make_id = fields.Many2one('vehicle.make', string="Make")
    model_id = fields.Many2one('vehicle.model', string="Model")
    vin = fields.Char(string="VIN")
    chasis_no = fields.Char(string="Chassis No")
    manufacture_year = fields.Selection(selection=get_year, string="Manufacture Year")
    bodystyle_id = fields.Many2one('vehicle.bodystyle', string="Body Style")
    image = fields.Binary(string="Image", attachment=True)
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet Vehicle")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [('code_plate_No', 'unique (name)', 'The code of the account must be unique per company !')]

    # @api.constrains('vin', 'name')
    # def _validate_formula(self):
    #     for vehicle in self:
    #         if not vehicle.vin and not vehicle.name:
    #             raise ValidationError(_("You have to give either Plat No or VIN!"))

    @api.constrains('chasis_no', 'name')
    def _validate_chassis_no(self):
        for vehicle in self:
            if not vehicle.chasis_no:
                raise ValidationError(_("You must have to give Chassis No!"))

    @api.constrains('name')
    def _check_plate_no(self):
        for rec in self:
            if rec.name:
                already_recs = self.search([('name', '=', rec.name), ('id', '!=', rec.id)])
                if already_recs:
                    raise ValidationError(_('Plate Number already exits!'))

    @api.onchange('make_id')
    def _onchange_make_id(self):
        image = ''
        if self.make_id:
            image = self.make_id.image

        self.image = image

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []

        domain = []
        if self.env.context.get('partner_id'):
            vehicles = self.search([('partner_id', '=', self.env.context['partner_id'])], limit=limit)
            domain.append(('id', 'in', vehicles.ids))

        return super(MotorVehicle, self).name_search(name, args + domain, operator, limit)
