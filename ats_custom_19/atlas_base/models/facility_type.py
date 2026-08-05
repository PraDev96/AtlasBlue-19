# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FacilityType(models.Model):
    _name = 'facility.type'
    _description = "Facility Type"

    name = fields.Char(string="Facility Type Name", required=True)


class PackageConfig(models.Model):
    _inherit = 'package.config'

    facility_type_id = fields.Many2one('facility.type')


class Facility(models.Model):
    _name = 'facility.facility'
    _description = "Facility"

    name = fields.Char(string="Name", required=True)
    location_id = fields.Many2one('res.partner', string="Facility Location")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    facility_type = fields.Selection([
        ('swimming_pool', 'Swimming Pool'),
        ('spa', 'Spa'),
        ('water_feature', 'Water Feature'),
        ('sauna', 'Sauna'),
        ('steam_room', 'Steam Room')], string="Facility Types")
    system_type = fields.Selection([('skimmer', 'Skimmer'), ('overflow', 'Overflow')], string="System Type")
    water_surface = fields.Float(string="Water Surface (m²)", store=True)
    volume = fields.Float(string="Volume (m³)", store=True)

    partner_id = fields.Many2one('res.partner', string="Partner")
    facility_project_id = fields.Many2one('project.project', string="Project")
    crm_lead_id = fields.Many2one("crm.lead", string="Lead/Opportunity")
    facility_id = fields.Many2one('package.config', string="Facility config", domain="[('is_facility', '=', True)]")
    facility_type_id = fields.Many2one('facility.type')

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = list(domain or [])
        if name:
            domain += ['|', ('name', operator, name), ('facility_id', operator, name)]

        return self._search(domain, limit=limit, order=order)

    def name_get(self):
        data = super(Facility, self).name_get()
        res = []
        for rec in data:
            prod = self.browse(rec[0])
            if prod.facility_id:
                res.append((rec[0], "[" + prod.facility_id.name + "] " + rec[1]))
            else:
                res.append(rec)

        return res

    @api.onchange('facility_project_id')
    def onchange_facility_project_id(self):
        if self.facility_project_id:
            self.partner_id = self.facility_project_id.partner_id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            return {"domain": {'partner_id': [('id', 'child_of', self.partner_id.id)]}}

    @api.onchange('facility_id')
    def onchange_facility_id(self):
        if self.facility_id:
            self.facility_type_id = self.facility_id.facility_type_id
