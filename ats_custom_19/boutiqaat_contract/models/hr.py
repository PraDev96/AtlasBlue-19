# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Contract(models.Model):
    _inherit = "hr.contract"

    housing_allowance = fields.Monetary(string="Housing / Accommodation Allowance")
    transport_allowance = fields.Monetary(string="Transport Allowance")
    mobile_allowance = fields.Monetary(string="Mobile Allowance")
    meal_allowance = fields.Monetary(string="Meal Allowance")
    motor_vehicle_allowance = fields.Monetary(string="Motor Vehicle Allowance")
    driver_fuel_allowance = fields.Monetary(string="Driver & Fuel Allowance")
    books_allowance = fields.Monetary(string="Books Allowance")
    special_other_allowance = fields.Monetary(string="Special / Other Allowance")
    commission = fields.Monetary(string="Commission")
    staff_discount = fields.Float(string="Staff Discount (%)", default=0.4)
    staff_max_discount = fields.Monetary(string="Staff Max Discount", default=60)
    pf_allowance = fields.Monetary(string="PF Allowances")
    night_shift_allowance = fields.Monetary(string="Night Shift Allowance")

    month_days = fields.Float(related="resource_calendar_id.month_days")
    rot_rate = fields.Float(related="resource_calendar_id.rot_rate")
    wot_rate = fields.Float(related="resource_calendar_id.wot_rate")
    pot_rate = fields.Float(related="resource_calendar_id.pot_rate")
    tot_monthly_hours = fields.Float(string="Total Monthly Hours", compute="_compute_tot_monthly_hours", store=True)
    total_salary = fields.Float(string="Total Salary", compute="_compute_tot_salary", store=True)
    total_leave_salary = fields.Float(string="Total Leave Salary", compute="_compute_tot_salary", store=True)
    per_hour_wage = fields.Float(compute="_compute_per_hour_wage")

    # Updated Salary
    next_contract_id = fields.Many2one('hr.contract', string="Next Contract")
    prev_contract_id = fields.Many2one('hr.contract', string="Prev. Contract")
    state = fields.Selection(selection_add=[('upd', 'Updated')])
    tot_monthly_leave_hours = fields.Float(string="Total Leave Monthly Hours", compute="_compute_tot_monthly_leave_hours", store=True)
    leave_month_days = fields.Float(related="resource_calendar_id.leave_month_days")

    def _compute_per_hour_wage(self):
        for rec in self:
            rec.per_hour_wage = rec.get_per_hour_salary()

    @api.depends("hours_per_day", "leave_month_days")
    def _compute_tot_monthly_leave_hours(self):
        for rec in self:
            tot_monthly_hours = 0
            if rec.resource_calendar_id:
                tot_monthly_hours = (rec.hours_per_day or 8) * (rec.leave_month_days or 30)

            rec.tot_monthly_hours = tot_monthly_hours

    def action_update_contract(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window'].sudo()._for_xml_id('boutiqaat_contract.action_upd_contract_wizard')
        ctx = self.env.context.copy()
        ctx.update({
            'default_contract_id': self.id,
            'default_wage': self.wage,
            'default_name': self.name,
        })
        action.update({'context': ctx})

        return action

    @api.depends("hours_per_day", "month_days")
    def _compute_tot_monthly_hours(self):
        for rec in self:
            if rec.resource_calendar_id:
                rec.tot_monthly_hours = (rec.hours_per_day or 8) * (rec.month_days or 26)

    def get_all_allowance(self, with_alw=True, with_wage=True):
        tot = 0
        if with_alw:
            tot += self.housing_allowance + \
                        self.transport_allowance + \
                        self.mobile_allowance +\
                        self.meal_allowance +\
                        self.motor_vehicle_allowance +\
                        self.driver_fuel_allowance +\
                        self.books_allowance +\
                        self.special_other_allowance +\
                        self.commission +\
                        self.pf_allowance +\
                        self.night_shift_allowance
        if with_wage:
            tot += self.wage

        return tot

    @api.depends('housing_allowance', 'transport_allowance', 'mobile_allowance', 'meal_allowance', 'motor_vehicle_allowance',
                 'driver_fuel_allowance', 'books_allowance', 'special_other_allowance', 'commission', 'pf_allowance', 'night_shift_allowance')
    def _compute_tot_salary(self):
        for rec in self:
            rec.total_salary = rec.get_all_allowance()
            rec.total_leave_salary = rec.get_leave_salary()

    def get_per_day_salary(self, with_alw=True, with_wage=True):
        salary = self.total_leave_salary
        return salary / (self.month_days or 26)

    def get_per_hour_salary(self, with_alw=True, with_wage=True):
        salary = self.get_per_day_salary(with_alw, with_wage)
        return salary / (self.hours_per_day or 8)

    def get_leave_salary(self, with_alw=True, with_wage=True):
        salary = self.get_all_allowance(with_alw, with_wage)
        return salary

    def get_per_day_leave_salary(self, with_alw=True, with_wage=True):
        salary = self.get_leave_salary(with_alw, with_wage)
        leave_month_days = self.employee_id.resource_calendar_id.leave_month_days or 26
        return salary / leave_month_days
