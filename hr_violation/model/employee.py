# -*- coding: utf-8 -*-

from odoo import models, fields


class Employee(models.Model):
    _inherit = 'hr.employee'

    violation_count = fields.Integer(string="Violation Count", compute='_compute_employee_violation')
    violation_ids = fields.One2many('hr.violation', 'employee_id', string="Violations")

    def _compute_employee_violation(self):
        Violation = self.env['hr.violation']
        for rec in self:
            violations = Violation.search([('employee_id', '=', rec.id)])
            rec.violation_count = len(violations)

    def action_hr_employee_violation(self):
        self.ensure_one()
        action = self.env.ref('hr_violation.action_hr_violation').sudo().read()[0]
        action.update({
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        })

        return action

    # def get_violation_deduction(self, date_from, date_to):
    #     sql = """
    #     SELECT sum(amount)
    #     FROM hr_violation
    #     WHERE employee_id = %s AND payslip_date BETWEEN %s AND %s
    #     """
    #     self.env.cr.execute(sql, (self.id, date_from, date_to))
    #     result = self.env.cr.fetchone()
    #     return result and result[0] or 0

    # def get_violation_amount(self, payslip):
    #     return self.get_violation_deduction(payslip.date_from, payslip.date_to)

    def get_violation_line_deduction(self, date_from, date_to):
        sql = """
            SELECT sum(line.amount)
            FROM hr_violation_installment_line AS line LEFT JOIN
                hr_violation AS violation ON violation.id = line.violation_id
            WHERE violation.employee_id = %s AND line.date BETWEEN %s AND %s
        """
        self.env.cr.execute(sql, (self.id, date_from, date_to))
        result = self.env.cr.fetchone()

        return result and result[0] or 0

    def get_date_violation_amount(self, payslip):
        return self.get_violation_deduction(payslip.date_from, payslip.date_to)

    def get_violation_amount(self, payslip):
        return self.get_violation_line_deduction(payslip.date_from, payslip.date_to)
