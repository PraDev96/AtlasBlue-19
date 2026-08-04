# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleSubscriptionPlan(models.Model):
    _inherit = 'sale.subscription.plan'

    is_dont_auto_post_invoice = fields.Boolean(string="Don't Auto Post Invoice", store=True)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _process_auto_invoice(self, invoice):
        """
            Replaced this method to achieve the invoice draft or to avoid the posting invoice.
            Hook for extension, to support different invoice states.
        """
        if self.plan_id and not self.plan_id.is_dont_auto_post_invoice:
            invoice.action_post()

        return
