# -*- coding: utf-8 -*-

from odoo import models


class ExpenseSubmitWizard(models.TransientModel):
    _name = 'expense.submit.wizard'
    _description = "Expense Submit Wizard"

    def action_submit(self):
        self.ensure_one()
        expense_ids = self.env.context.get('active_ids')
        if expense_ids:
            expenses = self.env['hr.expense'].browse(expense_ids)
            for expense in expenses:
                sheet = expense._create_sheet_from_expenses()
                sheet.action_submit_sheet()

        return True
