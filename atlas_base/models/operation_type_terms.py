# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpportunityTypeTerms(models.Model):
    _name = 'opportunity.type.terms'
    _description = "Opportunity Type Terms"
    _rec_name = 'opportunity_type'

    opportunity_type = fields.Selection([
        ('project', 'Project'), ('service', 'Service'), ('maintenance', 'Maintenance'), ('renovation', 'Renovation'), ('retail_sale', 'Retail Sale')
    ], string="Opportunity Type", required=True, default="project")
    terms = fields.Text(string="Terms & Conditions")

    _sql_constraints = [('opportunity_type_unique', 'unique(opportunity_type)', 'The opportunity_type of the account must be unique per company !')]

    @api.model
    def get_opportunity_type_terms(self, o_type):
        return self.search([('opportunity_type', '=', o_type)], limit=1).terms
