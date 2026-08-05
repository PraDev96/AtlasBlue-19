# -*- coding: utf-8 -*-

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        invoice_line = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        account_obj = self.env['account.account']
        if self.order_id.opportunity_type and self.display_type not in ('line_section', 'line_note'):
            if self.order_id.opportunity_type == 'project':
                account_opportunity_id = account_obj.search([
                    ('project_opportunity_type', '=', 'project'), ('internal_group', '=', 'liability'), ('account_type', '=', 'liability_current')], order='id DESC', limit=1)
            else:
                account_opportunity_id = account_obj.search([
                    ('project_opportunity_type', '=', self.order_id.opportunity_type), ('internal_group', '=', 'income')], order='id DESC', limit=1)

            if account_opportunity_id:
                invoice_line['account_id'] = account_opportunity_id.id

        return invoice_line
