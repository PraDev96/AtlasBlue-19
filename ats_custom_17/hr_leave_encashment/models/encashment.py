# -*- coding: utf-8 -*-

import logging
from odoo.exceptions import UserError
from odoo import models, fields, _, api
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta


class Encashment(models.Model):
    _name = 'emp.leave.encashment'
    _description = "Employee Leave Encashement"
    _inherit = ['mail.thread']
    _order = "date_payslip desc"

    def _employee_leave_ecncasement(self):
        return ['|', ('company_id', '=', False), ('company_id', '=', self.env.company.id)]

    name = fields.Char(string="Description", required=True, tracking=100)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True, index=True, domain=_employee_leave_ecncasement, tracking=100)
    contract_id = fields.Many2one("hr.contract", string="Contract", index=True, domain="[('employee_id', '=', employee_id)]", tracking=100)
    holiday_status_id = fields.Many2one("hr.leave.type", string="Leave Type", domain=[('allow_encashment', '=', True)], required=True)
    date_payslip = fields.Date(string="Payslip Date", required=True, tracking=100)
    monthly_salary = fields.Float(string="Current Monthly Salary", readonly=True, tracking=100)

    department_id = fields.Many2one("hr.department", string="Department", tracking=100)
    mobile = fields.Char(string="Mobile", tracking=100)
    phone = fields.Char(string="Phone", tracking=100)
    identification_id = fields.Char(string="Employee Number", tracking=100)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', string="Company", readonly=True, copy=False, required=True, default=lambda self: self.env.company, tracking=100)
    state = fields.Selection([("draft", "Draft"), ("confirm", "Confirmed"), ("paid", "Paid"), ("cancel", "Cancelled")],
                             string="State", default="draft", required=True, tracking=100)

    tot_amount = fields.Float(string="Total Amount", compute="_compute_tot_amount", tracking=100)
    cur_month_leave_amount = fields.Float(string="Current Month Leave Amount", compute="_compute_tot_amount", tracking=100)
    adv_leave_amount = fields.Float(string="Adv. Leave Amount", compute="_compute_tot_amount", tracking=100)
    price_unit = fields.Float(string="Per Leave Amount", copy=False, tracking=100)

    tot_leave_count = fields.Float(string="Total Leave Days", compute="_compute_on_employee", store=True, tracking=100)
    tot_leave_encashed = fields.Float(string="Already Encashed", compute="_compute_on_employee", store=True, tracking=100)
    tot_leave_balance = fields.Float(string="Balance", compute="_compute_on_employee", store=True, tracking=100)
    payable_leave_count = fields.Float(string="Payable Leaves", default=1, copy=False, tracking=100)
    pay_by_payslip = fields.Boolean(string="Pay By Payslip", default=True)
    holiday_id = fields.Many2one('hr.leave', string="Leave", required=True)
    request_date_from = fields.Date(string="From", related="holiday_id.request_date_from")
    request_date_to = fields.Date(string="To", related="holiday_id.request_date_to")

    accured_balance = fields.Float(string="Accured Balance", compute='_compute_balance_days', store=True)
    # balance_leave_days = fields.Float('Leave Balance', compute='_compute_balance_days', store=True)
    working_days_balance = fields.Float(compute='_compute_balance_days', string="Working Days Balance", store=True)
    leave_days = fields.Float(string="Leave Days", compute='_compute_balance_days', store=True)
    paid_leave_days = fields.Float(string="Adv. Leave Payment")
    unpaid_leave_days = fields.Float(string="Unpaid Leaves", compute='_compute_balance_days', store=True)
    public_days = fields.Float(string="Public Days", compute='_compute_balance_days', store=True)

    leave_report_ids = fields.Many2many('hr.leave.report', 'hr_leave_report_encashment_rel', 'encashment_id', 'leave_report_id', string="Leave Analysis")
    emp_input_id = fields.Many2one("emp.inputs", string="Employee Input", tracking=100)

    @api.onchange('holiday_id')
    def onchange_holiday_id(self):
        if self.holiday_id:
            self.holiday_status_id = self.holiday_id.holiday_status_id
            r1, r2, paid_leave_days = self._get_plus_mins_result(False)
            self.paid_leave_days = paid_leave_days

    @api.depends('holiday_id')
    def _compute_balance_days(self):
        for rec in self:
            # result = rec.holiday_id.get_employee_accured_date()
            rec.accured_balance = rec.holiday_id.total_accured_balance
            # rec.balance_leave_days = rec.holiday_id.total_accured_balance - rec.h
            rec.leave_days = rec.holiday_id.leave_paid_days
            rec.unpaid_leave_days = rec.holiday_id.leave_unpaid_days
            rec.public_days = rec.holiday_id.public_days
            rec.working_days_balance = rec.holiday_id.working_days_balance

    @api.onchange('employee_id', 'holiday_status_id')
    def _onchange_employee(self):
        emp = self.employee_id
        if emp:
            self.department_id = emp.department_id
            self.mobile = emp.mobile_phone
            self.phone = emp.phone
            self.identification_id = emp.identification_id
            self.contract_id = emp.contract_id

            # LeaveReport = self.env['hr.leave.report']
            # self.leave_report_ids = False
            # all_leave_reports = LeaveReport.search([
            #     ('employee_id', '=', emp.id),
            #     ('holiday_status_id', '=', self.holiday_status_id.id),
            #     ('state', '=', 'validate')
            # ])
            # if all_leave_reports:
            #     self.leave_report_ids = all_leave_reports

    # @api.constrains("employee_id", "payable_leave_count")
    # def _check_payable_leave_count(self):
    #     for rec in self:
    #         if rec.payable_leave_count <= 0:
    #             raise UserError(_("Only positive number of leave days allowed to encash."))
    #         if rec.tot_leave_balance < rec.payable_leave_count:
    #             raise UserError(_("You cannot encash more than leave balance."))

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        contract = self.contract_id
        if contract:
            self.monthly_salary = contract.get_per_month_leave_salary()
            self.price_unit = contract.get_per_day_leave_salary()

    @api.depends('employee_id', 'holiday_status_id')
    def _compute_on_employee(self):
        for rec in self:
            emp = rec.employee_id
            leave_encashed = tot_avail = 0
            if emp and rec.holiday_status_id:
                leaves = emp._get_encashment_remaining_leaves(rec.holiday_status_id.id)
                tot_avail = leaves.get(emp.id) or 0
                leave_encashed = emp.leave_encashed

            rec.tot_leave_encashed = leave_encashed
            rec.tot_leave_count = tot_avail
            rec.tot_leave_balance = tot_avail - leave_encashed

    # @api.depends("price_unit", "payable_leave_count")
    # def _compute_tot_amount(self):
    #     for rec in self:
    #         rec.tot_amount = rec.currency_id.round(rec.price_unit * rec.payable_leave_count)

    @api.depends("contract_id", "paid_leave_days")
    def _compute_tot_amount(self):
        for rec in self:
            price_unit = rec.price_unit
            cur_round = rec.currency_id.round
            cur_month_leave_amount = cur_round(price_unit * (rec.leave_days - rec.paid_leave_days))
            adv_leave_amount = cur_round(price_unit * rec.paid_leave_days)
            rec.cur_month_leave_amount = cur_month_leave_amount
            rec.adv_leave_amount = adv_leave_amount
            rec.tot_amount = cur_round(cur_month_leave_amount + adv_leave_amount)

    def _get_plus_mins_result(self, raise_error=True):
        result = {}
        tot_next_month_working_days = 0
        minsu_result = {}
        if self.holiday_id:
            end_date_plus_one = self.holiday_id.request_date_to.replace(day=self.holiday_id.request_date_from.day)  # + relativedelta(days=+1)
            start_date_plus_one = self.holiday_id.request_date_from  # + relativedelta(days=-1)

            months = [dt for dt in rrule(MONTHLY, dtstart=start_date_plus_one, until=end_date_plus_one)]
            if len(months) <= 1:
                if raise_error:
                    raise UserError(_('Paid Leaves will be paid in Payslip if its start date and end date in same month.'))
                else:
                    return {}, {}, 0

            resource_calendar = self.employee_id.resource_calendar_id
            per_day_salary = self.price_unit

            # 21 March
            first_month_start_date = months.pop(0)
            # 21 May
            last_month_last_date = months.pop(-1).replace(day=self.holiday_id.request_date_to.day, hour=23, minute=59)

            # 1 April
            next_month_start_date = first_month_start_date + relativedelta(day=1, months=+1)
            worked = resource_calendar.get_work_duration_data(next_month_start_date, last_month_last_date)
            working_pos_allowance = (per_day_salary * worked['days'])

            result.update({
                first_month_start_date: working_pos_allowance,
            })

            for month in months:
                month_start_date = month.replace(day=1)
                month_end_date = month + relativedelta(day=1, months=+1)
                # Mid Month Days should be considered End Date

                month_worked = resource_calendar.get_work_duration_data(month_start_date, month_end_date)
                month_total = (per_day_salary * month_worked['days'])

                tot_next_month_working_days += month_worked['days']

                minsu_result.update({
                    month_start_date.strftime('%Y-%m-%d'): month_total
                })

            # for last month calculation
            last_month_start_date = last_month_last_date.replace(day=1, hour=00, minute=00)
            # To Include last day in Working Duration, Added Hours and Minutes
            logging.info("__ Start, End : %s - %s", last_month_start_date, last_month_last_date)

            last_month_work = resource_calendar.get_work_duration_data(last_month_start_date, last_month_last_date)
            last_month_total = (per_day_salary * last_month_work['days'])
            tot_next_month_working_days += last_month_work['days']

            minsu_result.update({
                last_month_start_date: last_month_total
            })

        return result, minsu_result, tot_next_month_working_days

    def action_confirm(self):
        self.ensure_one()
        if self.pay_by_payslip:
            result, minsu_result, tot_working_days = self._get_plus_mins_result()
            lines = []
            for key, value in result.items():
                if value > 0.0:
                    lines.append((0, 0, {
                        'payslip_date': key,
                        'amount': value
                    }))

            for key, value in minsu_result.items():
                if value > 0.0:
                    lines.append((0, 0, {
                        'payslip_date': key,
                        'amount': -1 * value
                    }))

            EmpInput = self.env['emp.inputs']
            if self.emp_input_id:
                self.emp_input_id.action_cancel()

            new_emp_input = EmpInput.new({
                'name': _("Auto Added From Encashment : %s") % (self.name),
                'employee_id': self.employee_id.id,
                'input_type': 'alw',
                'tot_amount': self.adv_leave_amount,
                'no_of_installment': 1,
                'start_date': self.date_payslip,
                'input_line_ids': lines,
            })
            new_emp_input._onchange_employee()
            emp_input_vals = new_emp_input._convert_to_write(new_emp_input._cache)
            emp_input = EmpInput.create(emp_input_vals)
            emp_input.with_context(no_regular_installment=True).action_confirm()
            self.emp_input_id = emp_input.id
            self.holiday_id.write({'already_encashed': True})

        self.write({"state": "confirm"})

    def action_cancel(self):
        if self.emp_input_id:
            self.emp_input_id.action_cancel()
        if self.holiday_id:
            self.holiday_id.write({'already_encashed': False})

        self.write({"state": 'cancel'})

    def action_paid(self):
        self.write({"state": "paid"})

    def action_reset(self):
        self.write({"state": "draft"})


class EmpInput(models.Model):
    _inherit = 'emp.inputs'

    encashment_ids = fields.One2many("emp.leave.encashment", "emp_input_id", string="Encashments")

    def action_paid(self):
        super(EmpInput, self).action_paid()
        self.mapped('encashment_ids').action_paid()


class Contract(models.Model):
    _inherit = "hr.contract"

    leave_allocation = fields.Float(string="Leave Allocation")
    allocation_type = fields.Selection([('day', 'Day'), ('week', 'Week'), ('month', 'Month')], string="Allocation Type", default='month')


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_cancel(self):
        EmpInputLine = self.env['emp.input.line']
        super(Payslip, self).action_payslip_cancel()
        for payslip in self:
            emp_input_lines = EmpInputLine.search([('payslip_id', '=', payslip.id)])
            emp_input_lines.write({'payslip_id': False, 'state': 'due'})
