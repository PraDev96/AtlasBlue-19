# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(tracking=True)
    ar_name = fields.Char(string="Arabic Name", tracking=True)
    nick_name = fields.Char(string="Nick Name", tracking=True)
    passport_no = fields.Char(string="Partner Passport No", tracking=True)
    home_phone = fields.Char(string="Home Phone", tracking=True)
    fax = fields.Char(string="Fax", tracking=True)
    rating = fields.Selection([('1_star', '1 star'), ('2_star', '2 star'), ('3_star', '3 star'), ('4_star', '4 star'), ('5_star', '5 star')])
    client_type = fields.Selection([('commercial', 'Commercial'), ('residential', 'Residential')], required=False)
    project_id = fields.Many2one('project.project')
    client_type_id = fields.Many2one('client.type', string="Client Type Specification", tracking=True)
    project_count = fields.Integer(string="Project Count", compute="_compute_project_count", tracking=True)
    facility_ids = fields.One2many('facility.facility', 'partner_id', string="Facility")
    is_active = fields.Boolean(string="Is Active", default=True)
    stock_move_ids = fields.One2many("stock.move", "partner_id", string="Transfers", domain=[('state', '=', 'done')])
    equipment_ids = fields.One2many('atlas.maintenance.equipment', 'partner_id', string="Maintenance Equipment", tracking=True)
    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    city = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    website = fields.Char(tracking=True)
    block = fields.Char(tracking=True)
    avenue = fields.Char(tracking=True)
    house = fields.Char(tracking=True)
    floor = fields.Char(tracking=True)
    civil_code = fields.Char(tracking=True)
    default_supplierinfo_discount = fields.Float(tracking=True)
    state_id = fields.Many2one('res.country.state', tracking=True)
    country_id = fields.Many2one('res.country', tracking=True)
    governorate_id = fields.Many2one("res.governorate", string="Governorate")
    area_id = fields.Many2one("res.city.area", tracking=True)
    user_id = fields.Many2one('res.users', tracking=True)
    property_supplier_payment_term_id = fields.Many2one('account.payment.term', tracking=True)
    team_id = fields.Many2one('crm.team', tracking=True)
    property_payment_term_id = fields.Many2one('account.payment.term', tracking=True)
    assigned_partner_id = fields.Many2one('res.partner', tracking=True)
    property_product_pricelist = fields.Many2one('product.pricelist', tracking=True)
    property_purchase_currency_id = fields.Many2one('res.currency', tracking=True)
    property_account_position_id = fields.Many2one('account.fiscal.position', tracking=True)
    compny_id = fields.Many2one('res.company', tracking=True)
    property_stock_customer = fields.Many2one('stock.location', tracking=True)
    property_stock_supplier = fields.Many2one('stock.location', tracking=True)
    property_account_receivable_id = fields.Many2one('account.account', tracking=True)
    property_account_payable_id = fields.Many2one('account.account', tracking=True)
    grade_id = fields.Many2one('res.partner.grade', tracking=True)
    activation = fields.Many2one('res.partner.activation', tracking=True)
    is_employee = fields.Boolean(tracking=True)
    ref = fields.Char(tracking=True)
    date_review = fields.Date(tracking=True)
    date_review_next = fields.Date(tracking=True)
    date_partnership = fields.Date(tracking=True)
    partner_weight = fields.Integer(tracking=True)
    description_text = fields.Text("Content", tracking=True)

    def _compute_project_count(self):
        Project = self.env['project.project']
        for rec in self:
            rec.project_count = Project.search_count([('partner_id', '=', rec.id)])


class AccountMove(models.Model):
    _inherit = 'account.move'

    project_opportunity_type = fields.Selection(string="Opportunity Type", related='project_id.opportunity_type', store=True)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    hide_price = fields.Boolean(related='product_id.product_tmpl_id.hide_price')

    def reconcile(self):
        line_not_project = self.filtered(lambda l: not l.move_id.project_id)
        line_project = self.filtered(lambda l: l.move_id.project_id)
        project_id = False
        if line_project:
            project_id = line_project[0].move_id.project_id.id
            for line in line_not_project:
                line.move_id.write({
                    'project_id': project_id
                })
        return super(AccountMoveLine, self).reconcile()


class Company(models.Model):
    _inherit = "res.company"

    reg_no = fields.Char(tracking=True, string="Corp.reg.no")
    fax = fields.Char(tracking=True, string="Fax")
