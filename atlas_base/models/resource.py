# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], string="Exceptional Day", default='1')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    day_count = fields.Integer(string="Exceptional Day", compute="_compute_day_count")

    @api.depends('date_to', 'date_from', 'employee_id')
    def _compute_day_count(self):
        for rec in self:
            d1 = rec.date_from
            d2 = rec.date_to
            count = 0
            day_of_week = rec.employee_id.resource_calendar_id.day_of_week
            for d_ord in range(d1.toordinal(), d2.toordinal()):
                d = date.fromordinal(d_ord)
                if d.weekday() == int(day_of_week):
                    count += 1

            rec.day_count = count
