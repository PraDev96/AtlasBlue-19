# -*- coding: utf-8 -*-

from odoo import models, fields


class HrTimesheetOvertimeConfirmWizard(models.TransientModel):
    _name = 'timesheet.overtime.confirm.wizard'
    _description = "HR Timesheet Overtime Confirm Wizard"

    analytic_line_id = fields.Many2one('account.analytic.line', string="Timesheet Entry", required=True)
    overtime_hours = fields.Float(string="Overtime Spent Hours", required=True)

    def action_confirm_overtime(self):
        self.ensure_one()
        if self.analytic_line_id:
            self.analytic_line_id.with_context(skip_timesheet_limit_check=True).write({
                'is_overtime_added': True,
                'overtime_approved_manager_id': self.env.uid,
                'overtime_approved_amount': self.overtime_hours,
                'unit_amount': self.analytic_line_id.unit_amount + self.overtime_hours,
            })

        return {'type': 'ir.actions.act_window_close'}
