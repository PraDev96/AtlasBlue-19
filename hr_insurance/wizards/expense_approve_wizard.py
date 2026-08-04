# -*- coding: utf-8 -*-

from odoo import models


class ExpenseApproveWizard(models.TransientModel):
    _name = 'expense.approve.wizard'
    _description = "Expense Approve Wizard"

    def action_approve(self):
        self.ensure_one()
        expense_ids = self.env.context.get('active_ids')
        if expense_ids:
            expenses = self.env['hr.expense'].sudo().browse(expense_ids)
            for expense in expenses:
                expense.sheet_id.approve_expense_sheets()

        return True
