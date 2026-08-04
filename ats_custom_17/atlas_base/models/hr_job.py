# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrJob(models.Model):
    _inherit = "hr.job"

    def _get_default_cc(self):
        return 'mae@atlasblue.me'

    cc = fields.Char(string="Email CC", readonly=True, default=_get_default_cc)


class Encashment(models.Model):
    _inherit = 'emp.leave.encashment'

    public_leave_amount = fields.Float(string="Public Leave Amount", compute="_compute_tot_amount", tracking=100)

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        super(Encashment, self)._onchange_contract_id()
        contract = self.contract_id
        if contract:
            monthly_salary = contract.total_leave_salary
            self.price_unit = self.currency_id.round(monthly_salary / (contract.month_days or 1))

    @api.depends("contract_id", "paid_leave_days", 'public_days')
    def _compute_tot_amount(self):
        for rec in self:
            price_unit = rec.price_unit
            cur_round = rec.currency_id.round
            cur_month_leave_amount = cur_round(price_unit * (rec.leave_days - rec.paid_leave_days))
            adv_leave_amount = cur_round(price_unit * rec.paid_leave_days)
            public_days_amount = cur_round(price_unit * rec.public_days)
            rec.cur_month_leave_amount = cur_month_leave_amount
            rec.adv_leave_amount = adv_leave_amount
            rec.public_leave_amount = public_days_amount
            rec.tot_amount = cur_round(cur_month_leave_amount + adv_leave_amount + public_days_amount)


class EmployeeAccuralBalanceWizard(models.TransientModel):
    _inherit = 'employee.accural.balance.wizard'

    def get_eos_balance(self, emp):
        self.ensure_one()
        eos_amount = 0
        contract = emp.contract_id

        if contract:
            tot_year_days = tot_days = tdiff_year = 0
            date_joining = emp.date_joining or emp.work_start_issue_date
            if date_joining:
                # Unpaid Leave
                unpaid_status = self.env.ref('hr_holidays.holiday_status_unpaid')
                holidays = self.env['hr.leave'].search([('employee_id', '=', emp.id), ('state', '=', 'validate'), ('holiday_status_id', '=', unpaid_status.id)])
                tot_leaves = sum(holidays.mapped('number_of_days'))
                end_date = self.date or fields.Date.today()

                diff_days = end_date - date_joining
                tot_year_days = diff_days.days
                tot_days = tot_year_days - tot_leaves
                tdiff_year = tot_days / 365

                eos_deserved = emp.get_eos_deserved(contract, tdiff_year, 'terminate')
                monthly_salary = contract.get_eos_allowance()
                eos_amount = min(eos_deserved * monthly_salary / (contract.month_days or 26), monthly_salary * 18)

        return round(eos_amount, 4)
