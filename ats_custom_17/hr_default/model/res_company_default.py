# coding: utf-8

from odoo import models, fields


class Company(models.Model):
    _inherit = "res.company"

    license_ed = fields.Date(string="Company License Expiration Date")
    ministry_auth_sign_ed = fields.Date(string="Ministry Authorization Signature Expiration Date")
    gov_sal_cert_ed = fields.Date(string="Governmental Salary Certificate Expiration Date")
    gov_med_license_cert_ed = fields.Date(string="Governmental Medical License Certificate Expiration Date")


class Calendar(models.Model):
    _inherit = 'resource.calendar'

    month_days = fields.Float(string="Month Days", default=26)
    leave_month_days = fields.Float(string="Leave Month Days")
    prob_period_days = fields.Integer(string="Probation Days", default=100)
    prob_exclude_off = fields.Boolean(string="Probation period exclude Off Days ?")
