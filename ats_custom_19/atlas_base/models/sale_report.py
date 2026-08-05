# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleReport(models.Model):
    _inherit = 'sale.report'

    opportunity_type = fields.Selection([
        ('project', 'Project'), ('service', 'Service'), ('maintenance', 'Maintenance'), ('renovation', 'Renovation'), ('retail_sale', 'Retail Sale')
    ], string="Opportunity Type", required=True, default="project", store=True)

    def _select_sale(self):
        select_ = super(SaleReport, self)._select_sale()
        select_ += """ , s.opportunity_type as opportunity_type"""

        return select_

    def _group_by_sale(self):
        groupby_ = super(SaleReport, self)._group_by_sale()
        groupby_ += ", s.opportunity_type"

        return groupby_
