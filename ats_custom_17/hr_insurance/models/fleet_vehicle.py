# -*- coding: utf-8 -*-

from odoo import models, fields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    insurance_ids = fields.One2many('hr.insurance', 'fleet_vehicle_id', string="Insurance")
    insurance_count = fields.Integer(string="Insurance Count", compute='_compute_fleet_insurance')

    insurance_company_id = fields.Many2one('res.partner', compute='_get_insurance_company', string="Insurance Company")
    policy_number_id = fields.Char(compute='_get_insurance_policy_number', string="Policy Number")
    odoo_ins_number_id = fields.Many2one('hr.insurance', compute='_get_insurance_odoo_ins_number', string="Odoo INS Number")
    start_date = fields.Date(compute='_get_insurance_start_date', string="Start Date")
    end_date = fields.Date(compute='_get_insurance_end_date', string="End Date")

    def get_hr_insurance(self):
        for record in self:
            insurance = self.env['hr.insurance'].search([('fleet_vehicle_id', '=', record.id)], limit=1, order='id desc')
            return insurance

    def _get_insurance_odoo_ins_number(self):
        for record in self:
            insurance = record.get_hr_insurance()
            record.odoo_ins_number_id = insurance.id if insurance else False

    def _get_insurance_company(self):
        for record in self:
            insurance = record.get_hr_insurance()
            record.insurance_company_id = insurance.insurance_company_id.id if insurance and insurance.insurance_company_id else False

    def _get_insurance_policy_number(self):
        for record in self:
            insurance = record.get_hr_insurance()
            record.policy_number_id = insurance.policy_number if insurance and insurance.policy_number else False

    def _get_insurance_odoo_ins_number(self):
        for record in self:
            insurance = record.get_hr_insurance()
            record.odoo_ins_number_id = insurance.id if insurance else False

    def _get_insurance_start_date(self):
        for record in self:
            insurance = record.get_hr_insurance()
            record.start_date = insurance.start_date if insurance and insurance.start_date else False

    def _get_insurance_end_date(self):
        for record in self:
            insurance = record.get_hr_insurance()
            record.end_date = insurance.end_date if insurance and insurance.end_date else False

    def _compute_fleet_insurance(self):
        Insurance = self.env['hr.insurance']
        for rec in self:
            insurances = Insurance.search([('fleet_vehicle_id', '=', rec.id)])
            rec.insurance_count = len(insurances)

    def action_fleet_insurance(self):
        self.ensure_one()
        action = self.env.ref('hr_insurance.action_hr_insurance').sudo().read()[0]
        action['domain'] = [('fleet_vehicle_id', '=', self.id), ('insurance_type', '=', 'fleet_vehicle')]
        action['context'] = {
            'default_fleet_vehicle_id': self.id,
            'default_insurance_type': 'fleet_vehicle'
        }

        return action
