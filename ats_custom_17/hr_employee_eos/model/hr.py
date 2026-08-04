# -*- coding: utf-8 -*-

import calendar
from odoo.exceptions import UserError
from odoo import models, fields, _, api
from odoo.tools.date_utils import get_month
from dateutil.relativedelta import relativedelta


class HREmployeeEOS(models.Model):
    _name = "hr.employee.eos"
    _description = "HR Employee EOS"

    employee_id = fields.Many2one('hr.employee', string="Employee")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip")
    eos_days_in_month = fields.Float(string="EOS Allowance")
    allocated_for_month = fields.Date(string="EOS for Month")
    eos_amount = fields.Float(string="EOS Amount", help='End Of Service Amount')


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    opening_balance = fields.Float(string="EOS Opening Balance", digits=(16, 4))
    eos_type = fields.Selection([("bal", "Add Balance"), ("calc", "Calculate from Joining")], string="EOS Type")
    eos_ids = fields.One2many('hr.employee.eos', 'employee_id')
    eos_balance = fields.Float(compute='_compute_eos_balance', digits=(16, 4), string="EOS Balance")
    eos_deserved = fields.Float(compute='_compute_eos_deserved_amount', digits=(16, 4), string="EOS Deserved")
    eos_amount = fields.Float(compute='_compute_eos_deserved_amount', digits=(16, 4), string="EOS Amount")
    eos_deduction_amount = fields.Float(string="EOS Deduction Amount", digits=(16, 4))
    # eos_calculated_on = fields.Char(compute='_compute_eos_deserved_amount', string='EOS Calculated On')

    eos_tot_year_days = fields.Float(string="EOS Total Days", compute='_compute_eos_days')
    eos_tot_leaves = fields.Float(string="EOS Total Unpaid Leaves", compute='_compute_eos_days')
    eos_net_days = fields.Float(string="EOS Net Days", compute='_compute_eos_days', help="Total Days - Unpaid Leaves")
    eos_net_year = fields.Float(string="EOS Net Year", digits=(16, 4), compute='_compute_eos_days', help="(Total Days - Unpaid Leaves) / 365")
    eos_additional_work = fields.Float(string="Additional Work", digits=(16, 4))

    def _compute_eos_balance(self):
        for employee in self:
            employee.eos_balance = sum(employee.eos_ids.mapped('eos_amount'))

    def print_eos_entries(self):
        self.ensure_one()
        if not self.date_job_end:
            raise UserError(_("You can not print report without Job End Date!"))

        return self.env.ref('hr_employee_eos.action_hr_employee_eos_report').report_action(self)

    def _compute_eos_days(self):
        for rec in self:
            holidays = self.env['hr.leave'].search([('employee_id', '=', rec.id), ('state', '=', 'validate'), ('holiday_status_id.include_in_eos', '=', False)])
            rec.eos_tot_leaves = tot_leaves = sum(holidays.mapped('number_of_days'))
            tot_year_days = tot_days = tdiff_year = 0
            if rec.date_joining:
                end_date = rec.date_job_end or fields.Date.today()
                diff_days = end_date - rec.date_joining
                tot_year_days = diff_days.days
                tot_days = tot_year_days - tot_leaves
                tdiff_year = tot_days / 365

            rec.eos_tot_year_days = tot_year_days
            rec.eos_net_days = tot_days
            rec.eos_net_year = tdiff_year

    def generate_eos_entries(self):
        self.ensure_one()
        # contracts = self.env['hr.contract'].search([('employee_id', '=', self.id)])
        contract = self.contract_id
        if not contract:
            raise UserError(_("Current Contract Not Found."))

        if not self.date_joining:
            raise UserError(_("Joining Date Missing."))

        curr_date = self.date_joining
        end_date = self.date_job_end or fields.Date.today()

        while curr_date < end_date:
            contract.generate_month_eos(curr_date, True, False)
            curr_date = curr_date + relativedelta(months=1)

    @api.depends('date_job_end', 'job_end_reason', 'date_joining')
    def _compute_eos_deserved_amount(self):
        for emp in self:
            eos_deserved = eos_amount = 0
            if all([self.date_job_end, self.date_joining, self.job_end_reason]) or self.job_end_reason in ('resign', 'dismissed', 'terminate'):
                eos_deserved, eos_amount = emp._calculate_eos_amount()

            emp.eos_deserved = eos_deserved
            emp.eos_amount = eos_amount

    def get_eos_deserved(self, contract, tdiff_year):
        eos_deserved = final_eos = 0
        after_5 = contract.eos_after_5_year_days * 12
        before_5 = contract.eos_bf_5_year_days * 12
        if tdiff_year >= 5:
            after5_year = tdiff_year - 5
            eos_deserved = (after_5 * after5_year) + (before_5 * 5)
        elif tdiff_year >= 0:
            eos_deserved = before_5 * tdiff_year

        if self.job_end_reason in ['resign', 'dismissed']:
            if tdiff_year >= 10:
                final_eos = eos_deserved
            elif tdiff_year >= 5:
                final_eos = eos_deserved * 0.6667
            elif tdiff_year >= 3:
                final_eos = eos_deserved * 0.5
        elif self.job_end_reason == 'terminate':
            final_eos = eos_deserved

        return final_eos

    def _calculate_eos_amount(self):
        self.ensure_one()
        eos_amount = eos_deserved = 0
        contract = self.contract_id
        if contract:
            monthly_salary = contract.get_all_allowance()
            eos_deserved = self.get_eos_deserved(contract, self.eos_net_year)
            eos_amount = min(eos_deserved * monthly_salary / (contract.month_days or 26), monthly_salary * 18)

        return eos_deserved, eos_amount

    def get_eos_report_details(self):
        Leave = self.env['hr.leave.report']
        LeaveType = self.env['hr.leave.type']
        holiday_status = LeaveType.search([('code', '=', 'ANNUAL')])
        diff_period = relativedelta(self.date_job_end, self.date_joining)
        annual_leaves = Leave.search([('employee_id', '=', self.id), ('holiday_status_id', 'in', holiday_status.ids), ('state', '=', 'validate')])
        annual_bal = sum(annual_leaves.mapped('number_of_days'))

        today = fields.Date.today()
        if self.date_job_end:
            worked_days = (self.date_job_end - today).days
            if worked_days <= 0.0:
                worked_days = 0.0

            if self.contract_id:
                working_days = 0.0
                allocation_value = self.contract_id.leave_allocation
                allocation_type = self.contract_id.allocation_type
                if allocation_type == 'month':
                    month_days = calendar.monthrange(self.date_job_end.year, self.date_job_end.month)[1]
                    working_days = worked_days / month_days
                elif allocation_type == 'week':
                    working_days = worked_days / 7
                elif allocation_type == 'day':
                    working_days = worked_days

                working_days_balance = allocation_value * working_days
                annual_bal += working_days_balance

        loans = self.env['hr.loan'].sudo().search([('employee_id', '=', self.id)])
        loan_balance = round(sum(loans.mapped('balance_amount')), 4)
        return {
            'diff_period': diff_period,
            'leave_bal': round(annual_bal, 2),
            'loan_balance': loan_balance if loan_balance else 0,
        }


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    opening_balance = fields.Float(string="EOS Opening Balance", readonly=True)
    eos_type = fields.Selection([("bal", "Add Balance"), ("calc", "Calculate from Joining")], string="EOS Type")
    eos_additional_work = fields.Float(string="Additional Work", digits=(16, 4))
    eos_deduction_amount = fields.Float(string="EOS Deduction Amount", digits=(16, 4))


class HRContract(models.Model):
    _inherit = 'hr.contract'

    eos_bf_5_year_days = fields.Float(string="EOS Before 5 Years")
    eos_after_5_year_days = fields.Float(string="EOS After 5 Years")

    def generate_month_eos(self, month_date=False, force_generate=False, filter_contracts=True, payslip_id=None):
        month_date = month_date or fields.Date.today()
        for contract in self:
            if not contract.eos_bf_5_year_days or not contract.eos_after_5_year_days:
                raise UserError(_("EOS Days not configured in the contract."))

            month_first_day, month_last_day = get_month(month_date)
            no_of_leave_alloc_reqs = self.env['hr.employee.eos'].search_count([
                ('employee_id', '=', contract.employee_id.id), ('allocated_for_month', '>=', month_first_day), ('allocated_for_month', '<=', month_last_day),
            ])

            if not no_of_leave_alloc_reqs:
                contract._allocate_month_eos(month_date, payslip_id=payslip_id)

    def _allocate_month_eos(self, month_date, payslip_id=None):
        self.ensure_one()
        emp = self.employee_id
        eos = EndOfService = self.env['hr.employee.eos']
        if emp.date_joining:
            eos_net_year = ((month_date - emp.date_joining).days - emp.eos_tot_leaves) / 365
            eos_days = self.eos_after_5_year_days if eos_net_year > 5 else self.eos_bf_5_year_days
            eos = EndOfService.create({
                'employee_id': emp.id,
                'eos_days_in_month': eos_days,
                'allocated_for_month': month_date,
                'eos_amount': self.get_per_day_salary() * eos_days,
                'payslip_id': payslip_id,
            })

        return eos


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HRPayslip, self).action_payslip_done()
        for slip in self:
            slip.contract_id.generate_month_eos(slip.date_from, force_generate=True, payslip_id=slip.id)

        return res


class LeaveReport(models.Model):
    _inherit = "hr.leave.employee.type.report"

    @api.model
    def action_time_off_analysis(self):
        print("action_time_off_analysis")
        result = super().action_time_off_analysis()
        result['view_mode'] = 'tree,pivot,form'

        return result
