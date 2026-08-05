# -*- coding: utf-8 -*-

from odoo import models, fields, _


class Encasement(models.Model):
    _inherit = 'emp.leave.encashment'

    payment_type = fields.Selection([
        ('payslip', 'Add advance payable days in payslip'), ('full_encashment', 'Create Full Leave Payment')], string="Payment Type", required=True)

    def action_confirm(self):
        self.ensure_one()
        # total_unit =0.0
        if self.payment_type == 'full_encashment':
            result, minsu_result, tot_working_days = self._get_plus_mins_result()
            lines = []
            total_unit = self.paid_leave_days - self.holiday_id.number_of_days
            for key, value in result.items():
                if value > 0.0:
                    lines.append((0, 0, {
                        'payslip_date': key,
                        'amount': total_unit * self.price_unit
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
                'name': _("Auto Added From Encasement : %s") % (self.name),
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
        elif self.payment_type == 'payslip':
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
                'name': _("Auto Added From Encasement : %s") % (self.name),
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
