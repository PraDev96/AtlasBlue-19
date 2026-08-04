# -*- coding: utf-8 -*-

from odoo import models, fields


class Employee(models.Model):
    _inherit = 'hr.employee'

    penalty_count = fields.Integer(string="Penalty Count", compute='_compute_employee_penalty')
    penalty_ids = fields.One2many('hr.penalty', 'employee_id', string="Penalties")

    def _compute_employee_penalty(self):
        for rec in self:
            penaltys = self.env['hr.penalty'].sudo().search([('employee_id', '=', rec.id)])
            rec.penalty_count = len(penaltys)

    def action_hr_employee_penalty(self):
        self.ensure_one()
        action = self.env.ref('hr_penalty.action_hr_penalty').sudo().read()[0]
        action.update({
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        })

        return action

    # def get_penalty_deduction(self, date_from, date_to):
    #     sql = """
    #     SELECT sum(amount)
    #     FROM hr_penalty
    #     WHERE employee_id = %s AND date_penalty BETWEEN %s AND %s
    #     """
    #     self.env.cr.execute(sql, (self.id, date_from, date_to))
    #     result = self.env.cr.fetchone()
    #     return result and result[0] or 0

    # def get_date_penalty_amount(self, payslip):
    #     return self.get_penalty_deduction(payslip.date_from, payslip.date_to)

    def get_penalty_line_deduction(self, date_from, date_to):
        sql = """
            SELECT sum(line.amount)
            FROM hr_penalty_installment_line AS line LEFT JOIN
                hr_penalty AS penalty ON penalty.id = line.penalty_id
            WHERE penalty.employee_id = %s AND line.date BETWEEN %s AND %s
        """
        self.env.cr.execute(sql, (self.id, date_from, date_to))
        result = self.env.cr.fetchone()
        return result and result[0] or 0

    def get_date_penalty_amount(self, payslip):
        return self.get_penalty_deduction(payslip.date_from, payslip.date_to)

    def get_penalty_deduction(self, payslip):
        return self.get_penalty_line_deduction(payslip.date_from, payslip.date_to)
