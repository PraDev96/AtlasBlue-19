# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    name = fields.Char(tracking=True)
    partner_id = fields.Many2one(tracking=True)
    picking_type_id = fields.Many2one(tracking=True)
    location_id = fields.Many2one(tracking=True)
    location_dest_id = fields.Many2one(tracking=True)
    scheduled_date = fields.Datetime(tracking=True)
    origin = fields.Char(tracking=True)
    move_type = fields.Selection(tracking=True)
    user_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    note = fields.Text(tracking=True)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    team_id = fields.Many2one(tracking=True)
    user_id = fields.Many2one(tracking=True)
    ticket_type_id = fields.Many2one(tracking=True)
    priority = fields.Selection(tracking=True)
    tag_ids = fields.Many2many(tracking=True)
    partner_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    email_cc = fields.Char(tracking=True)
    campaign_id = fields.Many2one(tracking=True)
    medium_id = fields.Many2one(tracking=True)
    source_id = fields.Many2one(tracking=True)
    partner_name = fields.Char(tracking=True)
    partner_email = fields.Char(tracking=True)

    def unlink(self):
        if not self.user_has_groups('atlas_base.group_delete_helpdesk_ticket'):
            raise UserError(_('You cannot Delete the Helpdesk Ticket!!! Please Contact Administrator.'))

        return super(HelpdeskTicket, self).unlink()


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    name = fields.Char(tracking=True)
    expected_revenue = fields.Monetary(tracking=True)
    recurring_revenue = fields.Monetary(tracking=True)
    probability = fields.Float(tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
    email_from = fields.Char(tracking=True)
    email_cc = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    date_deadline = fields.Date(tracking=True)
    priority = fields.Selection(tracking=True)
    tag_ids = fields.Many2many(tracking=True)
    user_id = fields.Many2one(tracking=True)
    team_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    contact_name = fields.Char(tracking=True)
    partner_name = fields.Char(tracking=True)
    function = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    city = fields.Char(tracking=True)
    state_id = fields.Many2one(tracking=True)
    zip = fields.Char(tracking=True)
    website = fields.Char(tracking=True)
    lang_id = fields.Many2one('res.lang', tracking=True)
    country_id = fields.Many2one('res.country', tracking=True)
    day_open = fields.Float(tracking=True)
    day_close = fields.Float(tracking=True)
    referred = fields.Char(tracking=True)


class UtmSource(models.Model):
    _inherit = 'utm.source'

    active = fields.Boolean(string="Active", default=True)
