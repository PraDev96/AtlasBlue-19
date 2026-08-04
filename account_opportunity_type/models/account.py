# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    project_opportunity_type = fields.Selection([
        ('project', 'Project'),
        ('service', 'Service'),
        ('maintenance', 'Maintenance'),
        ('renovation', 'Renovation'),
        ('retail_sale', 'Retail Sale')], string="Opportunity Type")
