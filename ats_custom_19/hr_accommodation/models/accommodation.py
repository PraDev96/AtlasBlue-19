# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, _, api


class Building(models.Model):
    _name = 'hr.building'
    _description = "Building"

    name = fields.Char(string="Building", required=True)
    number = fields.Char(string="Number")
    bed_total_count = fields.Integer(string="Total Bed Count", compute="_compute_bed_count")
    bed_available_count = fields.Integer(string="Purchase Order Count", compute="_compute_bed_count")
    street = fields.Char(string="Street")
    area = fields.Char(string="Area")
    block = fields.Char(string="Block")
    capacity = fields.Integer(string="Building Capacity", required=True, default=0)

    def _compute_bed_count(self):
        Accommodation = self.env['hr.accommodation']
        for building in self:
            accommodations = Accommodation.search([('building_id', '=', building.id)])
            total_available_beds = len(accommodations)
            building.bed_total_count = building.capacity
            building.bed_available_count = (building.capacity - total_available_beds)

    # def action_view_bed(self):
    #     self.ensure_one()
    #     Bed = self.env['hr.bed']
    #     total_beds = Bed.search([('building_id', '=', self.id)])
    #     action = self.env.ref('hr_accommodation.action_hr_bed').read()[0]
    #     action['domain'] = [
    #         ('id', 'in', total_beds.ids),
    #     ]
    #     return action

    def action_view_available_bed(self):
        self.ensure_one()
        Accommodation = self.env['hr.accommodation']
        accommodations = Accommodation.search([('building_id', '=', self.id)])
        action = self.env.ref('hr_accommodation.action_hr_accommodation').sudo().read()[0]
        action['domain'] = [('id', 'in', accommodations.ids)]

        return action


class Flat(models.Model):
    _name = 'hr.flat'
    _description = "Flat"

    building_id = fields.Many2one('hr.building', string="Building", required=True)
    name = fields.Char(string="Flat", required=True)


class Floor(models.Model):
    _name = 'hr.floor'
    _description = "Floor"

    building_id = fields.Many2one('hr.building', string="Building", required=True)
    flat_id = fields.Many2one('hr.flat', string="Flat", required=True)
    name = fields.Char(string="Floor", required=True)


class Room(models.Model):
    _name = 'hr.room'
    _description = "Room"

    building_id = fields.Many2one('hr.building', string="Building", required=True)
    flat_id = fields.Many2one('hr.flat', string="Flat", required=True)
    name = fields.Char(string="Room", required=True)


class Bed(models.Model):
    _name = 'hr.bed'
    _description = "Bed"

    def _compute_bed_log(self):
        BedLog = self.env['hr.bed.log']
        for rec in self:
            bedlogs = BedLog.search([('bed_id', '=', rec.id)])
            rec.bed_log_count = len(bedlogs)

    building_id = fields.Many2one('hr.building', string="Building", required=True)
    flat_id = fields.Many2one('hr.flat', string="Flat", required=True)
    room_id = fields.Many2one('hr.room', string="Room")
    floor_id = fields.Many2one('hr.floor', string="Floor", required=True)
    name = fields.Char(string="Bed No", required=True)
    bed_log_count = fields.Integer(string="Bed Log Count", compute='_compute_bed_log')

    def open_bed_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bed Logs',
            'view_mode': 'tree',
            'res_model': 'hr.bed.log',
            'domain': [('bed_id', '=', self.id)],
            'context': {'default_bed_id': self.id}
        }


class BedLog(models.Model):
    _name = 'hr.bed.log'
    _description = "Bed Log"

    bed_id = fields.Many2one('hr.bed', string="Bed ID")
    bed = fields.Char(string="Bed Name")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    employee_id = fields.Many2one('hr.employee', string="Employee")


class Accommodation(models.Model):
    _name = 'hr.accommodation'
    _description = "Accommodation"

    def _default_employee(self):
        return self.env.user.employee_id

    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    building_id = fields.Many2one('hr.building', string="Building", required=True)

    flat_id = fields.Many2one('hr.flat', string="Flat")
    flat = fields.Char(string="Flat Name")

    room_id = fields.Many2one('hr.room', string="Room")
    room = fields.Char(string="Room Name")

    floor_id = fields.Many2one('hr.floor', string="Floor")
    floor = fields.Char(string="Floor Name")

    bed_id = fields.Many2one('hr.bed', string="Bed No")
    bed = fields.Char(string="Bed Name")

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    street = fields.Char(string="Street")
    area = fields.Char(string="Area")
    block = fields.Char(string="Block")
    start_date = fields.Date(string="Start Date", default=fields.Date.context_today)
    end_date = fields.Date(string="End Date")

    total_bed = fields.Integer('Total Bed', default=1)

    @api.constrains('total_bed', 'building_id')
    def check_accommodation_capacity(self):
        for accomodation in self:
            if accomodation.building_id.bed_available_count < 0:
                raise UserError(_("Building does not have available Bed!"))

    # @api.constrains('bed_id')
    # def _check_bed_id(self):
    #     for record in self:
    #         accommodations = self.search([
    #             ('bed_id', '=', record.bed_id.id),
    #             ('id', '!=', record.id),
    #         ])
    #         if accommodations:
    #             raise ValidationError(_("This room already allocated to some other employee!"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({'name': self.env['ir.sequence'].next_by_code('hr.accommodation') or '/'})

        return super(Accommodation, self).create(vals_list)

    # def write(self, vals):
    #     for rec in self:
    #         if 'employee_id' in vals and vals['employee_id']:
    #             employee_id = vals['employee_id']
    #             if employee_id != rec.employee_id.id:
    #                 self.create_bed_history(rec.bed_id.id, employee_id)
    #                 self.close_bed_history(rec.bed_id.id, rec.employee_id.id)
    #     return super(Accommodation, self).write(vals)

    def create_bed_history(self, bed_id, employee_id):
        self.env['hr.bed.log'].create({
            'employee_id': employee_id,
            'bed_id': bed_id,
            'start_date': fields.Date.today(),
        })

    def close_bed_history(self, bed_id, employee_id):
        bed_logs = self.env['hr.bed.log'].search([('employee_id', '=', employee_id), ('bed_id', '=', bed_id)])
        bed_logs.write({'end_date': fields.Date.today()})

    def calculate_address(self):
        for accomm in self:
            address = ''
            if accomm.area:
                address += 'Area: ' + accomm.area + ', '
            if accomm.block:
                address += 'Block: ' + accomm.block + ', '
            if accomm.street:
                address += 'Street: ' + accomm.street + ', '
            if accomm.building_id:
                address += 'Building: ' + accomm.building_id.name + ', '

            if accomm.flat:
                address += 'Flat: ' + accomm.flat + ', '
            if accomm.floor:
                address += 'Floor: ' + accomm.floor + ', '
            if accomm.bed:
                address += 'Bed: ' + accomm.bed + ', '
            if address:
                accomm.employee_id.write({'employee_address': address})

    @api.onchange('building_id')
    def _onchange_building_id(self):
        self.area = False
        self.block = False
        self.street = False
        if self.building_id:
            self.area = self.building_id.area
            self.block = self.building_id.block
            self.street = self.building_id.street


class Employee(models.Model):
    _inherit = 'hr.employee'

    def _compute_employee_accommodation(self):
        Accommodation = self.env['hr.accommodation']
        for rec in self:
            accommodations = Accommodation.search([('employee_id', '=', rec.id)])
            rec.accommodation_count = len(accommodations)

    accommodation_ids = fields.One2many('hr.accommodation', 'employee_id', string="Accommodations")
    accommodation_count = fields.Integer(string="Accommodation Count", compute='_compute_employee_accommodation')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", compute="_compute_vehicle")
    emp_license_plate = fields.Char(string="Employee License Plate", compute="_compute_emp_license_plate", store=True)

    def _compute_emp_license_plate(self):
        for employee in self:
            fleet_vehicle = self.env['fleet.vehicle'].search([('emp_driver_id', '=', employee.id)])
            if fleet_vehicle:
                for fleet in fleet_vehicle:
                    temp = fleet.license_plate
                    employee.emp_license_plate = temp
            else:
                employee.emp_license_plate = False

    def _compute_vehicle(self):
        for employee in self:
            fleet_vehicle = self.env['fleet.vehicle'].search([('emp_driver_id', '=', employee.id)])
            if fleet_vehicle:
                for fleet in fleet_vehicle:
                    temp = fleet.id
                    employee.vehicle_id = temp
            else:
                employee.vehicle_id = False

    def action_hr_employee_accommodation(self):
        self.ensure_one()
        action = self.env.ref('hr_accommodation.action_hr_accommodation').sudo().read()[0]
        action.update({
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id}
        })

        return action


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    accommodation_ids = fields.One2many('hr.accommodation', 'employee_id', string="Accommodations")
    accommodation_count = fields.Integer(string="Accommodation Count", compute='_compute_employee_accommodation')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", compute="_compute_vehicle")
    emp_license_plate = fields.Char(string="Employee License Plate", compute="_compute_emp_license_plate", store=True)
