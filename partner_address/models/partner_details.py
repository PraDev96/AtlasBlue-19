# -*- coding: UTF-8 -*-

from odoo import models, fields, api


class Governorate(models.Model):
    _name = 'res.governorate'
    _description = "City Area"

    name = fields.Char(required=True)
    is_published = fields.Boolean(string="Is Published ?", default=True)


class Area(models.Model):
    _name = 'res.city.area'
    _description = "City Area"

    name = fields.Char(required=True)
    is_published = fields.Boolean(string="Is Published ?", default=True)
    governorate_id = fields.Many2one("res.governorate", string="Governorate")


class Partner(models.Model):
    _inherit = 'res.partner'

    area = fields.Char(string="Area")
    area_id = fields.Many2one("res.city.area", string="City Area")
    block = fields.Char(string="Block")
    avenue = fields.Char(string="Avenue")
    house = fields.Char(string="House")
    floor = fields.Char(string="Floor")
    governorate_id = fields.Many2one("res.governorate", string="Governorate")
    apartment_no = fields.Char(string="Apartment No")
    civil_code = fields.Char(string="Civil ID")
    paci_number = fields.Text(string="Paci Number")

    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        existing_fields = super()._address_fields()

        return ['block', 'avenue', 'house', 'floor', 'apartment_no'] + existing_fields
