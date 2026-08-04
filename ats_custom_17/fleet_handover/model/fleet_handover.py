# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class FleetHandOver(models.Model):
    _name = 'fleet.handover'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HandOver"

    name = fields.Char(string="Ref", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", tracking=True)
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True, tracking=True)
    model_id = fields.Many2one('fleet.vehicle.model', string="Model", store=True, tracking=True, related="fleet_vehicle_id.model_id")
    state = fields.Selection([('draft', 'Draft'), ('assign', 'Assign Driver'), ('released', 'Released Driver')], string="State", default='draft', required=True, tracking=True)
    assign_employee_id = fields.Many2one('hr.employee', tracking=True, string="Driver", store=True, required=True)
    license_plate = fields.Char(string="License Plate", related="fleet_vehicle_id.license_plate", tracking=True, required=True, store=True)
    start_date = fields.Datetime(string="Start Date", tracking=True)
    end_date = fields.Datetime(string="End Date", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.handover')

        return super(FleetHandOver, self).create(vals_list)

    def action_assign_driver(self):
        FleetVehicle = self.env['fleet.vehicle']
        for handover in self:
            driver_assi = FleetVehicle.search([('driver_id', '=', handover.assign_employee_id.id)], limit=1)
            self.env.cr.execute("SELECT id, name FROM fleet_vehicle WHERE model_id=%s and driver_id is not null", (handover.model_id.id,))
            vehicle_model = self.env.cr.fetchall()

            self.env.cr.execute("SELECT id, name FROM fleet_vehicle WHERE driver_id=%s", (handover.assign_employee_id.id,))
            res = self.env.cr.fetchall()
            if res:
                raise ValidationError(_('For Driver %s already allocated vehicle %s!.') % (handover.assign_employee_id.name, driver_assi.name,))
            elif vehicle_model:
                raise ValidationError(_('For Vehicle %s already allocated Driver %s!.') % (handover.model_id.name, handover.fleet_vehicle_id.driver_id.name,))
            else:
                handover.fleet_vehicle_id.write({'driver_id': handover.assign_employee_id.id, 'model_id': handover.model_id.id})
                start_dt = fields.Datetime.now()
                handover.write({'state': 'assign'})
                if not handover.start_date:
                    handover.start_date = start_dt

    def action_released_driver(self):
        for handover in self:
            end_dt = fields.Datetime.now()
            handover.write({'state': 'released'})
            if not handover.end_date:
                handover.end_date = end_dt

            handover.fleet_vehicle_id.driver_id = False


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    fleet_handover_ids = fields.One2many('fleet.handover', 'fleet_vehicle_id', string="Fleet Handover")
    fleet_handover_count = fields.Integer(string="Total Handover Files", compute="_compute_handover_count")

    def _compute_handover_count(self):
        for rec in self:
            rec.fleet_handover_count = len(rec.fleet_handover_ids.ids)

    def action_fleet_handover_view(self):
        self.ensure_one()
        action = self.env.ref('fleet_handover.action_fleet_handover').read()[0]
        action.update({
            'domain': [('fleet_vehicle_id', '=', self.id)],
            'context': {'default_fleet_vehicle_id': self.id},
        })

        return action
