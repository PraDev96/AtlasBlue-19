# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, time, date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

TERMINATE_REASON = [
    ("terminate", "Terminate"),
    ("resign", "Resign"),
    ('dismissed', 'Dismissed'),
    ("other", "Other")
]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    civil_id = fields.Char(string="Civil ID")
    civil_start_date = fields.Date(string="Civil Start Date")
    civil_end_date = fields.Date(string="Civil End Date")
    # social_sec_date = fields.Datetime("Start Date")
    # social_sec_code = fields.Char("Social Security Code")
    work_permit_expiry = fields.Date(string="Work Permit Expiry")

    passport_start_date = fields.Date(string="Passport Start Date")
    passport_end_date = fields.Date(string="Passport End Date")
    passport_country_id = fields.Many2one('res.country', string="Passport Country")
    passport_type = fields.Char(string="Passport Type", default='Normal')
    sponsorship_id = fields.Many2one('res.partner', string="Sponsorship")
    iban_no = fields.Char(string="IBAN / Bank Account")

    # religion = fields.Char('Religion')
    religion = fields.Selection([('muslim', 'Muslim'), ('non_muslim', 'Non Muslim')], string="Religion In", default='muslim')
    date_joining = fields.Date(string="Joining Date")
    date_job_end = fields.Date(string="Job End Date")
    job_end_reason = fields.Selection(TERMINATE_REASON, string="Job End Reason")
    job_end_desc = fields.Text(string="Job End Description")

    file_civil_id = fields.Binary(string="Civil Code Copy")
    file_driving_lic = fields.Binary(string="Driving License Copy")
    file_passport = fields.Binary(string="Passport Copy")

    article_type_id = fields.Many2one('article.type', string="Attachment Type")
    file_attachment = fields.Binary(string="Other Doc")

    residency_expiry_date = fields.Date(string="Residency Expiry Date")
    residency_number = fields.Char(string="Residency Number")
    work_permit_marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('not_specific', 'Not Specific'), ('divorced', 'Divorced')],
                                                  string="Work Permit Marital Status")
    work_start_issue_date = fields.Date(string="Work Start Issued Date/ Joining Date")

    @api.constrains('passport_start_date', 'passport_end_date')
    def _check_passport_start_end_date(self):
        for employee in self:
            if employee.passport_start_date and employee.passport_end_date and employee.passport_end_date < employee.passport_start_date:
                raise ValidationError(
                    _('Ending date cannot be greater than starting date.') + "\n" +
                    _("Passport Of '%s' starts '%s' and ends '%s'") % (employee.name, employee.passport_start_date, employee.passport_end_date)
                )

    @api.constrains('civil_start_date', 'civil_end_date')
    def _check_civil_start_end_date(self):
        for employee in self:
            if employee.civil_start_date and employee.civil_end_date and employee.civil_end_date < employee.civil_start_date:
                raise ValidationError(
                    _('Ending date cannot greater than starting date.') + "\n" +
                    _("Civil Of '%s' starts '%s' and ends '%s'") % (employee.name, employee.civil_start_date, employee.civil_end_date)
                )

    def _get_date_start_work(self):
        if self.date_joining:
            return datetime.combine(self.date_joining, time.min)

        return self.create_date


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    civil_id = fields.Char(readonly=True)
    civil_start_date = fields.Date(readonly=True)
    civil_end_date = fields.Date(readonly=True)
    # social_sec_date = fields.Datetreadonly=True)
    # social_sec_code = fields.Char("Social Security Code")
    work_permit_expiry = fields.Date(readonly=True)
    passport_start_date = fields.Date(readonly=True)
    passport_end_date = fields.Date(readonly=True)
    iban_no = fields.Char(string="IBAN / Bank Account")

    passport_type = fields.Char(readonly=True)
    religion = fields.Selection([('muslim', 'Muslim'), ('non_muslim', 'Non Muslim')], readonly=True)
    date_joining = fields.Date(readonly=True)
    date_job_end = fields.Date(readonly=True)
    job_end_reason = fields.Selection(TERMINATE_REASON, readonly=True)
    job_end_desc = fields.Text(readonly=True)
    # file_civil_id = fields.Binary(readonly=True)
    # file_driving_lic = fields.Binary(readonly=True)
    # file_passport = fields.Binary(readonly=True)
    article_type_id = fields.Many2one('article.type', readonly=True)
    # file_attachment = fields.Binary(readonly=True)
    passport_country_id = fields.Many2one('res.country', string="Passport Country", readonly=True)
    sponsorship_id = fields.Many2one('res.partner', string="Sponsorship", readonly=True)
    residency_expiry_date = fields.Date(string="Residency Expiry Date")
    residency_number = fields.Char(string="Residency Number")
    work_permit_marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('not_specific', 'Not Specific'), ('divorced', 'Divorced')],
                                                  string="Work Permit Marital Status")
    work_start_issue_date = fields.Date(string="Work Start Issued Date/ Joining Date")


class Contract(models.Model):
    _inherit = 'hr.contract'

    month_days = fields.Float(related="resource_calendar_id.month_days")
    leave_month_days = fields.Float(related="resource_calendar_id.leave_month_days")
    hours_per_day = fields.Float(related="resource_calendar_id.hours_per_day")
    prob_period_days = fields.Integer(related="resource_calendar_id.prob_period_days")
    prob_exclude_off = fields.Boolean(related="resource_calendar_id.prob_exclude_off")
    contract_type = fields.Char(string="Employee Contract Type")
    permit_wage = fields.Monetary(string="Work Permit Salary")

    @api.onchange('resource_calendar_id', 'month_days', 'date_start')
    def onchange_probation(self):
        self.date_end = False
        if self.date_start and self.prob_period_days and self.employee_id:
            dt = fields.Datetime.from_string("%s 00:00:00" % self.date_start).astimezone()
            if self.prob_exclude_off:
                calendar = self.resource_calendar_id
                date_end = calendar.plan_days(self.prob_period_days, dt, True)
            else:
                date_end = dt + relativedelta(days=self.prob_period_days)

            self.trial_date_end = date_end

    def write(self, vals):
        """
            If Contract Archive
            -> Set Contract End Date
            -> Set Contract as Expired

            If This Contract is linked in Employee
            -> Set another contract based on Date Else None
        """
        today = fields.Date.today()
        if 'active' in vals and vals['active'] == False:
            if not vals.get('date_end'):
                vals['date_end'] = today

            if not vals.get('state'):
                vals['state'] = 'close'

        res = super(Contract, self).write(vals)

        if ('active' in vals and vals['active'] == False) or (vals.get('date_end')):
            Employee = self.env['hr.employee']
            for contract in self:
                emps = Employee.search([('contract_id', '=', contract.id)])
                if emps:
                    emps.write({'contract_id': False})

        return res

    def get_all_allowance(self, with_alw=True, with_wage=True):
        tot = 0
        if with_wage:
            tot += self.wage

        return tot

    def get_leave_deduction(self):
        return 0

    def get_per_month_leave_salary(self, with_alw=True, with_wage=True):
        salary = self.get_all_allowance(with_alw, with_wage)
        salary = salary - self.get_leave_deduction()
        return salary

    def get_per_day_leave_salary(self, with_alw=True, with_wage=True):
        salary = self.get_per_month_leave_salary(with_alw, with_wage)
        return salary / (self.leave_month_days or self.month_days or 26)

    def get_per_day_salary(self, with_alw=True, with_wage=True):
        salary = self.get_all_allowance(with_alw, with_wage)
        return salary / (self.month_days or 26)

    def get_per_hour_salary(self, with_alw=True, with_wage=True):
        salary = self.get_per_day_salary(with_alw, with_wage)
        return salary / (self.hours_per_day or 8)

    @api.model
    def update_state(self):
        """
            Remove Visa Expiry for Contract Auto Expiry
        """
        contracts = self.search([
            ('state', '=', 'open'), ('kanban_state', '!=', 'blocked'),
            ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=7))),
            ('date_end', '>=', fields.Date.to_string(date.today() + relativedelta(days=1))),
        ])

        for contract in contracts:
            contract.activity_schedule(
                'mail.mail_activity_data_todo',
                contract.date_end,
                _("The contract of %s is about to expire.", contract.employee_id.name),
                user_id=contract.hr_responsible_id.id or self.env.uid
            )

        contracts.write({'kanban_state': 'blocked'})

        self.search([('state', '=', 'open'), ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=1)))]).write({
            'state': 'close'
        })

        self.search([('state', '=', 'draft'), ('kanban_state', '=', 'done'), ('date_start', '<=', fields.Date.to_string(date.today()))]).write({
            'state': 'open'
        })

        contract_ids = self.search([('date_end', '=', False), ('state', '=', 'close'), ('employee_id', '!=', False)])
        # Ensure all closed contract followed by a new contract have a end date.
        # If closed contract has no closed date, the work entries will be generated for an unlimited period.
        for contract in contract_ids:
            next_contract = self.search([
                ('employee_id', '=', contract.employee_id.id),
                ('state', 'not in', ['cancel', 'new']),
                ('date_start', '>', contract.date_start)
            ], order="date_start asc", limit=1)
            if next_contract:
                contract.date_end = next_contract.date_start - relativedelta(days=1)
                continue

            next_contract = self.search([
                ('employee_id', '=', contract.employee_id.id),
                ('date_start', '>', contract.date_start)
            ], order="date_start asc", limit=1)

            if next_contract:
                contract.date_end = next_contract.date_start - relativedelta(days=1)

        return True
