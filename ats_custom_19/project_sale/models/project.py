# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import AccessError


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'mail.activity.mixin']

    date_end = fields.Date(string="End Date", tracking=True)
    phone = fields.Char(related="partner_id.phone", tracking=True)
    mobile = fields.Char(related="partner_id.mobile", tracking=True)
    cust_invoice_ids = fields.One2many('account.move', 'project_id', string="Customer Invoices", domain=[('move_type', '=', 'out_invoice')], copy=False)
    cust_invoice_count = fields.Integer(string="Customer Invoice Count", compute="_compute_customer_invoice_count", store=True, copy=False)
    sup_invoice_ids = fields.One2many('account.move', 'project_id', string="Outsource Invoices", domain=[('move_type', '=', 'in_invoice')], copy=False)
    sup_invoice_count = fields.Integer(string="Outsource Invoice Count", compute="_compute_supplier_invoice_count", store=True, copy=False)

    so_ids = fields.One2many("sale.order", "project_id", string="Sale Orders", tracking=True)
    sale_order_count = fields.Integer(string="Sale Order Count", compute="_compute_sale_pur_count", tracking=True)
    po_ids = fields.One2many("purchase.order", "project_id", string="Purchase Orders", tracking=True)
    purchase_order_count = fields.Integer(string="Purchase Order Count", compute="_compute_sale_pur_count", tracking=True)
    product_ids = fields.One2many('product.order.line', 'project_id', string="Order Lines", copy=True, tracking=True)
    other_cost_lines = fields.One2many('product.order.line', 'other_cost_id', string="Other Cost", copy=True, tracking=True)
    employee_cost_lines = fields.One2many('employee.cost', 'project_id', string="Employee Cost", copy=True, tracking=True)
    team_id = fields.Many2one('crm.team', string="Project Team", tracking=True, domain=[('type_team', '=', 'project')])

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting for Civil work'),
        ('hold', 'On Hold'),
        ('started', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancel', 'Cancelled'),
        ('frozen', 'Frozen'),
    ], string="State", default='draft', required=True,store=False, tracking=True, copy=False)

    number = fields.Char(string="Project Code", copy=False, tracking=True)
    description = fields.Html()

    company_id = fields.Many2one('res.company', string="Company", tracking=True, default=lambda self: self.env['res.company']._company_default_get())
    project_type_id = fields.Many2one('project.type', string="Project Type", tracking=True)

    raw_materials_total = fields.Float(compute="_compute_raw_materials_total", string="Budget Material/Consumable Details", digits=(16, 3))
    machining_details = fields.Float(compute="_compute_machining_details", string="Budget Machining Details", digits=(16, 3))
    man_power_details = fields.Float(compute="_compute_man_power_details", string="Budget Man Power Details", digits=(16, 3))
    tot_actual_material_cost = fields.Float(string="Actual Material/Consumable Details", compute="_compute_tot_actual_material_cost", digits=(16, 3))
    total_of_vendor_bill = fields.Float(compute="compute_vendor_bill", string="Actual Man Power Details", digits=(16, 3))
    total_budget = fields.Float(compute="_compute_total_budget", digits=(16, 3))
    total_actual = fields.Float(compute="_compute_total_actual", digits=(16, 3))
    total_percen = fields.Float(compute="_compute_total_percen", digits=(16, 3))

    material_total_percen = fields.Float(compute="_compute_total_per", digits=(16, 3))
    manpower_total_percen = fields.Float(compute="_compute_manpower_total_percen", digits=(16, 3))

    timesheet_time_amount = fields.Float(compute='_compute_timesheet_time_amount', digits=(16, 3))
    timesheet_time_percen = fields.Float(compute="_compute_timesheet_total_percen", digits=(16, 3))

    professional_service_budget_amount = fields.Float(string="Professional Service Budget Amount", digits=(16, 3))
    expense_budget_amount = fields.Float(string="Expense Budget Amount", digits=(16, 3))

    picking_ids = fields.One2many('stock.picking', 'project_id', string="Pickings", tracking=True)
    delivery_order_count = fields.Integer(string="Picking Count", compute='_compute_delivery_order_count', tracking=True)

    expense_ids = fields.One2many('hr.expense', 'project_id', string="Expenses", tracking=True)
    expense_count = fields.Integer(string="Expenses Count", compute='_compute_expense_count', tracking=True)

    event_ids = fields.One2many("calendar.event", "project_id", string="Recurring Tasks", copy=True)
    event_count = fields.Integer(string="#Total Events", compute='_compute_event_count', tracking=True)

    salable_line_ids = fields.One2many("sale.order.line", "project_id", string="Salable Lines", tracking=True)

    def _compute_event_count(self):
        for rec in self:
            rec.event_count = len(rec.event_ids.ids)

    def compute_vendor_bill(self):
        for project in self:
            total_of_vendor_bill = 0
            for inv in project.sup_invoice_ids:
                if inv.state == 'posted':
                    for line in inv.invoice_line_ids:
                        total_of_vendor_bill += line.quantity * line.price_unit

            expense_amount = sum(project.expense_ids.mapped('total_amount'))
            project.total_of_vendor_bill = (total_of_vendor_bill + expense_amount)

    def _compute_total_budget(self):
        for rec in self:
            rec.total_budget += rec.raw_materials_total + rec.expense_budget_amount + rec.professional_service_budget_amount

    def _compute_total_actual(self):
        for rec in self:
            rec.total_actual += rec.tot_actual_material_cost + rec.total_of_vendor_bill + rec.timesheet_time_amount

    def _compute_total_per(self):
        for rec in self:
            rec.material_total_percen = (rec.tot_actual_material_cost * 100 / (rec.raw_materials_total or 1))

    def _compute_manpower_total_percen(self):
        for rec in self:
            rec.manpower_total_percen = rec.total_of_vendor_bill * 100 / (rec.expense_budget_amount or 1)

    def _compute_total_percen(self):
        for project in self:
            project.total_percen = project.total_actual * 100 / (project.total_budget or 1)

    def function_selling_price(self):
        sale_total = 0
        for rec in self:
            for so in rec.so_ids:
                sale_total += so.amount_total

        return sale_total

    @api.depends('expense_ids', 'expense_ids.project_id')
    def _compute_expense_count(self):
        for project in self:
            project.expense_count = len(project.expense_ids.ids)

    @api.depends("picking_ids", "picking_ids.project_id")
    def _compute_delivery_order_count(self):
        for rec in self:
            rec.delivery_order_count = len(rec.picking_ids.filtered(lambda p: p.picking_type_code in ('outgoing', 'incoming')).ids)

    @api.depends('timesheet_ids')
    def _compute_timesheet_time_amount(self):
        for project in self:
            project.timesheet_time_amount = 0
            # project.timesheet_time_amount = sum(project.employee_cost_lines.mapped('actual_subtotal'))
            # total_time = 0.0
            # for timesheet in project.timesheet_ids:
                # Timesheets may be stored in a different unit of measure, so first
                # we convert all of them to the reference unit
                # total_time += timesheet.unit_amount * timesheet.product_uom_id.factor_inv
            # Now convert to the proper unit of measure set in the settings
            # total_time *= project.timesheet_encode_uom_id.factor
            # project.timesheet_time_amount = abs(int(round(total_time)))

    def _compute_timesheet_total_percen(self):
        for rec in self:
            rec.timesheet_time_percen = rec.timesheet_time_amount * 100 / (rec.professional_service_budget_amount or 1)

    def _compute_tot_actual_material_cost(self):
        Layer = self.env['stock.valuation.layer']
        for rec in self:
            done_pickings = rec.picking_ids.filtered(lambda p: p.state == 'done' and p.picking_type_code == 'outgoing')
            all_layers = Layer.search([('stock_move_id', 'in', done_pickings.mapped('move_ids_without_package.id'))])
            total_cost = sum(all_layers.mapped('value'))
            rec.tot_actual_material_cost = abs(total_cost)

    def _compute_raw_materials_total(self):
        # total cost of item in delivery order as budget cost
        raw_materials_total = 0
        for project in self:
            # for picking in project.picking_ids:
            #     raw_materials_total += sum([move.product_id.standard_price * move.product_uom_qty for move in picking.move_lines])
            for line in project.salable_line_ids.filtered(lambda sol: sol.state == 'sale'):
                raw_materials_total += line.price_subtotal

            project.raw_materials_total = raw_materials_total

    def _compute_machining_details(self):
        machining_details = 0
        for project in self:
            for line in project.other_cost_lines:
                machining_details += line.price_subtotal

            project.machining_details = machining_details

    def _compute_man_power_details(self):
        man_power_details = 0
        for project in self:
            for line in project.employee_cost_lines:
                man_power_details += line.subtotal

            project.man_power_details = man_power_details

    def action_customer_view_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        action['domain'] = [('move_type', 'in', ('out_invoice', 'out_refund')), ('project_id', '=', self.id)]
        action['context'] = {
            'default_move_type': 'out_invoice',
            'move_type': 'out_invoice',
            'journal_type': 'sale',
            'default_company_id': self.company_id.id,
            'default_project_id': self.id,
            'default_partner_id': self.partner_id.id,
        }

        return action

    def action_bill_view_invoices(self):
        action = self.env.ref('account.action_move_in_invoice_type').sudo().read()[0]
        action['domain'] = [('move_type', 'in', ('in_invoice', 'in_refund')), ('project_id', '=', self.id)]
        action['context'] = {
            'default_move_type': 'in_invoice',
            'move_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_project_id': self.id,
            'default_partner_id': self.partner_id.id,
        }

        return action

    def action_view_sale_orders(self):
        action = self.env.ref('sale.action_orders').sudo().read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'default_company_id': self.company_id.id,
            'default_project_id': self.id,
            'default_partner_id': self.partner_id.id,
        }

        return action

    def action_view_events(self):
        action = self.env.ref('calendar.action_calendar_event').sudo().read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'default_company_id': self.company_id.id,
            'default_project_id': self.id,
            'default_team_id': self.team_id.id,
        }

        return action

    def action_view_purchase_orders(self):
        action = self.env.ref('purchase.purchase_form_action').sudo().read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'default_company_id': self.company_id.id,
            'default_project_id': self.id,
            'default_partner_id': self.partner_id.id,
        }

        return action

    def action_view_delivery_orders(self):
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        outgoing_type = self.env['stock.picking.type'].search([('code', 'in', ('outgoing', 'incoming')), ('company_id', '=', self.company_id.id)], limit=1)
        action['domain'] = [
            ('id', 'in', self.picking_ids.filtered(lambda p: p.picking_type_code in ('outgoing', 'incoming')).ids), ('picking_type_id.code', 'in', ('outgoing', 'incoming')),
        ]
        action['context'] = {
            'default_project_id': self.id,
            'search_default_picking_type': True,
            'default_partner_id': self.partner_id.id,
            'default_company_id': self.company_id.id,
            'default_picking_type_id': outgoing_type.id,
            'default_account_analytic_id': self.analytic_account_id.id,
        }

        return action

    @api.depends('cust_invoice_ids', 'cust_invoice_ids.project_id')
    def _compute_customer_invoice_count(self):
        for rec in self:
            rec.cust_invoice_count = len(rec.cust_invoice_ids.filtered(lambda i: i.move_type == 'out_invoice').ids)

    @api.depends('sup_invoice_ids', 'sup_invoice_ids.project_id')
    def _compute_supplier_invoice_count(self):
        for rec in self:
            rec.sup_invoice_count = len(rec.sup_invoice_ids.filtered(lambda i: i.move_type == 'in_invoice').ids)

    @api.depends("so_ids", "so_ids.project_id", "po_ids", "po_ids.project_id")
    def _compute_sale_pur_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.so_ids.ids)
            rec.purchase_order_count = len(rec.po_ids.ids)

    def open_related_ids(self):
        self.ensure_one()
        ctx = self.env.context
        if ctx.get('open_action') and ctx.get('open_domain'):
            action_data = self.env.ref(ctx['open_action']).sudo().read()
            if action_data:
                action_data['domain'] = ctx['open_domain'] + [('project_id', '=', self.id)]
                return action_data
            else:
                raise AccessError(_("Action Not Found"))


class ProductOrderLine(models.Model):
    _name = 'product.order.line'
    _description = "Product Order Line"
    _rec_name = 'product_id'

    project_id = fields.Many2one('project.project', string="Project", ondelete='cascade')
    other_cost_id = fields.Many2one('project.project', string="Other Cost Reference", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict')
    description = fields.Text(string="Description")
    date = fields.Date(string="Date")
    product_uom_qty = fields.Float(string="Ordered Quantity", digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string="Unit of Measure")
    price_unit = fields.Float(string="Unit Price", required=True, digits='Product Price', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string="Subtotal", readonly=True, store=True)
    currency_id = fields.Many2one(related='project_id.currency_id', depends=['project_id'], store=True, string="Currency", readonly=True)
    company_id = fields.Many2one(related='project_id.company_id', string="Company", store=True, readonly=True)

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.price_unit * line.product_uom_qty

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.description = self.product_id.name
        self.product_uom = self.product_id.uom_id.id
        self.price_unit = self.product_id.lst_price


class EmployeeCost(models.Model):
    _name = 'employee.cost'
    _description = "Employee Cost"
    _rec_name = "employee_id"

    project_id = fields.Many2one('project.project', string="Project", ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", change_default=True, ondelete='restrict')
    hours_spent = fields.Float(string="Total Hours", default=0.0)
    price_unit = fields.Float(string="Unit Price", required=True, digits='Product Price', default=0.0)
    subtotal = fields.Monetary(compute='_compute_amount', string="Subtotal", readonly=True, store=True)
    currency_id = fields.Many2one(related='project_id.currency_id', depends=['project_id'], store=True, string="Currency", readonly=True)
    company_id = fields.Many2one(related='project_id.company_id', string="Company", store=True, readonly=True)

    @api.depends('hours_spent', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.subtotal = line.price_unit * line.hours_spent


class ProjectType(models.Model):
    _name = 'project.type'
    _description = "Project Type"

    name = fields.Char('Name', required=True)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    team_id = fields.Many2one('crm.team', string="Project Team", tracking=True)
    user_id = fields.Many2one('res.users', string="Team Leader", tracking=True)

    def send_mail_to_assignee(self, vals):
        if vals.get('employee_id'):
            for task in self:
                body = "Task Assigned to %s" % (task.employee_id.name or '')
                partner_ids = []
                if task.employee_id.user_id.partner_id:
                    partner_ids.append(task.employee_id.user_id.partner_id.id)

                if task.team_id.team_members_ids:
                    partner_ids += task.team_id.team_members_ids.mapped('user_id.partner_id.id')

                task.message_post(body=body, partner_ids=partner_ids)

    @api.model_create_multi
    def create(self, vals_list):
        record = super(ProjectTask, self).create(vals_list)
        for vals in vals_list:
            record.send_mail_to_assignee(vals)

        return record

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        self.send_mail_to_assignee(vals)

        return res


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    team_id = fields.Many2one(related="project_id.team_id", store=True)
