# -*- coding: utf-8 -*-

from pytz import UTC
from datetime import datetime
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class Move(models.Model):
    _inherit = 'stock.move'

    project_id = fields.Many2one("project.project", string="Project")
    is_equiped = fields.Boolean(related="product_id.is_equipment", store="True")


class Project(models.Model):
    _inherit = 'project.project'

    opportunity_type = fields.Selection([
        ('project', 'Project'),
        ('service', 'Service'),
        ('maintenance', 'Maintenance'),
        ('renovation', 'Renovation'),
        ('retail_sale', 'Retail Sale')], string="Opportunity Type", tracking=True)

    facility_ids = fields.One2many('facility.facility', 'facility_project_id', string="Facility", tracking=True)
    facility_type_id = fields.Many2one(related="facility_ids.facility_type_id")
    follow_up_date = fields.Date(string="Follow Up Date", tracking=True)
    lead_time_id = fields.Many2one('lead.time', tracking=True)
    package_facility_ids = fields.Many2many('package.config', string="Facilities", tracking=True)
    is_project_template = fields.Boolean(tracking=True)
    delivery_move_ids = fields.One2many("stock.move", "project_id", string="Delivery Moves", tracking=True)
    state_id = fields.Many2one('project.task.state', string="Task State", tracking=True)
    contract_start_date = fields.Date(string="Contract Start Date", tracking=True)
    contract_end_date = fields.Date(string="Contract End Date", tracking=True)
    payment_type = fields.Selection([('free', 'Free'), ('paid', 'Paid')], tracking=True)
    hold_start_date = fields.Date(string="Hold Start Date", tracking=True)
    hold_end_date = fields.Date(string="Hold End Date", tracking=True)
    label_task = fields.Char(tracking=True)
    partner_id = fields.Many2one(tracking=True)
    is_maintenance_project = fields.Boolean(string="Is Maintenance Project?", tracking=True)
    equipment_ids = fields.One2many('atlas.maintenance.equipment', 'project_id', string="Maintenance Equipment", tracking=True)
    total_hold_days = fields.Integer(compute='_compute_total_hold_days', tracking=True)
    total_delivery = fields.Float(string="Delivered Amount", compute="_compute_total_delivery", tracking=True)
    total_so_amount = fields.Float(compute="_compute_total_sale", string="Sale Amount", tracking=True)
    total_completion_percent = fields.Float(string="Total Completion (%)", compute="_compute_tot_completion", compute_sudo=True, copy=False, tracking=True, store=True, digits=(16, 2))
    total_completion_text = fields.Html(string="Total Completion By Stage", compute="_compute_tot_completion", compute_sudo=True, store=True)
    project_progress = fields.Float(string="Project Progress", compute="_compute_project_progress", store=True)
    project_adress = fields.Many2one('res.partner', string="Project Address", tracking=True)
    project_city = fields.Many2one('res.city.area', string="Project Area", store=True, readonly=False, tracking=True)
    facility_id = fields.Many2one('package.config', string="Import Facility")
    day_ids = fields.Many2many('week.days', string="Days Of Visit", tracking=True)
    config_facility_ids = fields.Many2many('package.config', 'package_config_project_rel', string="Project Facilities", compute="set_values_to")
    number_of_days_per_week = fields.Integer(string="Number Of Visits Per Week", tracking=True)
    is_under_warranty = fields.Boolean(string="Is Under Warranty ?")
    door_type = fields.Selection([('indoor', 'Indoor'), ('outdoor', 'Outdoor')], string="Door")
    service_type = fields.Selection([('chemicals', 'Chemicals'), ('without_chemicals', 'Without Chemicals'), ('water_test', 'Water Test')], string="Service Test")
    project_type_detail_id = fields.Many2one('project.type.detail', tracking=True, string="Project Type Detail")
    governorate_id = fields.Many2one(related='project_adress.governorate_id', store=True)

    warranty_completed_date = fields.Date(string="Warranty Completed Date", store=True, readonly=True, help="Date will be auto set while the task-state is set as Warranty")
    cancelled_date = fields.Date(string="Cancelled Date", store=True, readonly=True)

    @api.onchange('project_adress')
    def onchange_project_address(self):
        for project in self:
            if project.project_adress and project.project_adress.area_id:
                project.project_city = project.project_adress.area_id.id
            else:
                project.project_city = False

    def update_total_completion_percentage(self):
        """
            This is for updating the total completion percentage by code.
            Need to create a server action for this from front-end.
        """
        today = datetime.now()
        start_date = datetime(today.year, today.month, 1, 0, 0, 0)
        start_date_utc = UTC.localize(start_date)
        project_messages = self.env['mail.message'].search([('model', '=', 'project.task'), ('create_date', '>=', start_date_utc)], order='create_date desc')
        project_tasks = self.env['project.task'].sudo().browse(project_messages.mapped('res_id'))
        projects = project_tasks.mapped('project_id')
        for project in projects:
            project._compute_tot_completion()

    @api.depends('partner_id.phone', 'user_id')
    def _compute_partner_phone(self):
        for project in self:
            project.partner_phone = project.user_id.phone

    def _inverse_partner_phone(self):
        for project in self:
            project.sudo().user_id.phone = project.partner_phone

    @api.onchange('partner_id')
    def set_values_to(self):
        for project in self:
            temp = project.partner_id.facility_ids.mapped('facility_id').ids
            project.config_facility_ids = temp

    @api.depends('total_completion_percent')
    def _compute_project_progress(self):
        for rec in self:
            if rec.total_completion_percent:
                rec.project_progress = rec.total_completion_percent
            else:
                rec.project_progress = 0.0

    @api.depends('task_ids', 'type_ids', 'type_ids.weightage', 'type_ids.total_weightage')
    def _compute_tot_completion(self):
        for rec in self:
            percent = 0
            stage_str = '<table class="table table-bordered w-100">'
            stage_str += '\n<thead><tr>'
            stage_str += '<th>Stage</th>'
            stage_str += '<th>Weightage (%)</th>'
            stage_str += '<th>Completion (%)</th>'
            stage_str += '</tr></thead><tbody>'
            for stage in rec.type_ids:
                percent += round(stage.weightage * stage.total_weightage / 100, 2)
                stage_str += '\n<tr>'
                stage_str += '<th>' + stage.display_name + '</th>'
                stage_str += '<td>' + str(stage.weightage) + '</td>'
                stage_str += '<td>' + str(stage.total_weightage) + '</td>'
                stage_str += '</tr>'

            stage_str += '\n<tr>'
            stage_str += '<th>Total Completion(%)</th>'
            stage_str += '<th>' + str(percent) + '</th>'
            stage_str += '<th> </th>'
            stage_str += '</tr>'
            stage_str += '</tbody></table>'
            rec.total_completion_percent = round(percent, 2)
            rec.total_completion_text = stage_str

    def _compute_total_delivery(self):
        Layer = self.env['stock.valuation.layer']
        for rec in self:
            done_pickings = rec.picking_ids.filtered(lambda p: p.state == 'done' and p.picking_type_code == 'outgoing')
            all_layers = Layer.search([('stock_move_id', 'in', done_pickings.mapped('move_ids_without_package.id'))])
            total_cost = sum(all_layers.mapped('value'))
            rec.total_delivery = abs(total_cost)

    @api.depends('so_ids', 'so_ids.state', 'so_ids.amount_total')
    def _compute_total_sale(self):
        for project in self:
            sales = project.so_ids.filtered(lambda s: s.state in ('sale', 'done'))
            project.total_so_amount = sum(sales.mapped('amount_total'))

    def _compute_total_hold_days(self):
        for record in self:
            if record.hold_start_date:
                if record.hold_end_date:
                    record.total_hold_days = (record.hold_end_date - record.hold_start_date).days
                else:
                    record.total_hold_days = (fields.Date.today() - record.hold_start_date).days
            else:
                record.total_hold_days = 0

    @api.onchange('is_project_template')
    def onchange_is_project_template(self):
        self.active = False if self.is_project_template else True

    def write(self, vals):
        prev_stage = self.state_id
        res = super(Project, self).write(vals)
        if vals.get('state_id') and self.state_id.is_hold_stage:
            self.write({'hold_start_date': fields.Date.today()})
            self.write({'hold_end_date': False})
        if vals.get('state_id') and prev_stage.is_hold_stage and not self.state_id.is_hold_stage:
            self.write({'hold_end_date': fields.Date.today()})
            for record in self.filtered('date_end'):
                diff = fields.Date.today() - record.hold_start_date
                if diff.days:
                    record.date_end = record.date_end + relativedelta(days=diff.days)

        if vals.get('state_id'):
            """
                This is for Warranty and Cancelled State Date setting for Project Count miss-match issue.
            """
            task_state = self.env['project.task.state'].sudo().browse(vals.get('state_id'))
            if task_state and task_state.name == 'Warrenty':
                self.write({'warranty_completed_date': fields.Date.today()})
            if task_state and task_state.name == 'Cancelled':
                self.write({'cancelled_date': fields.Date.today()})

            if prev_stage.name == 'Warrenty' and self.state_id.name != 'Warrenty' and self.warranty_completed_date:
                self.warranty_completed_date = False
            if prev_stage.name == 'Cancelled' and self.state_id.name != 'Cancelled' and self.cancelled_date:
                self.cancelled_date = False

        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('opportunity_type') and not vals.get('number'):
                code = 'project.%s' % vals.get('opportunity_type')
                vals['number'] = self.env['ir.sequence'].next_by_code(code)

        return super(Project, self).create(vals_list)

    @api.constrains("project_progress")
    def _check_weightage(self):
        for rec in self:
            if rec.project_progress > 100 or rec.project_progress < 0:
                raise UserError(_("Total percentage of all stages of the project must be under 0 to 100.\nCurrent sum is %s") % (rec.project_progress))


class Calendar(models.Model):
    _inherit = 'calendar.event'

    state_id = fields.Many2one(related='project_id.state_id', store=True)

    @api.model
    def _get_public_fields(self):
        afields = super()._get_public_fields()
        return set(list(afields) + ['state_id'])


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    facility_id = fields.Many2one('package.config', string="Facility", domain="[('is_facility', '=', True)]")
    total_weightage = fields.Float(string="Total Weightage (%)", compute="_compute_weightage", digits=(16, 2))
    weightage = fields.Float(string="Weightage (%)", copy=True, store=True, digits=(16, 2))

    @api.constrains("weightage", "project_ids")
    def _check_weightage(self):
        for rec in self:
            for proj in rec.project_ids.with_context(active_test=False):
                proj_stages = proj.type_ids
                total_weightage = round(sum(proj_stages.mapped('weightage')), 2)
                if total_weightage > 100 or total_weightage < 0:
                    raise UserError(_("Total percentage of all stages of the project must be under 0 to 100.\nCurrent sum is %s") % (total_weightage))

    @api.onchange('task_progress_percentage')
    def _compute_weightage(self):
        for stage in self:
            all_weightage = 0.0
            for project in stage.project_ids:
                all_tasks = project.task_ids.filtered(lambda t: t.stage_id.id == stage.id and t.task_progress_percentage > 0 and t.weightage > 0)
                for record in all_tasks:
                    all_weightage += round((record.weightage * record.task_progress_percentage) / 100, 3)

            stage.total_weightage = all_weightage

    @api.depends('facility_id')
    def _compute_display_name(self):
        for record in self:
            name = record.name
            if record.facility_id:
                name = record.facility_id.name + ' : ' + record.name
                if record.total_weightage > 0:
                    name = name + ' (' + str(record.total_weightage) + '%)'

            record.display_name = name

    def name_get(self):
        result = []
        for record in self:
            if record.facility_id:
                name = record.facility_id.name + ' : ' + record.name
                if record.total_weightage > 0:
                    name = name + ' (' + str(record.total_weightage) + '%)'
            else:
                name = record.name
            result.append((record.id, name))

        return result


class ProductOrderLine(models.Model):
    _inherit = 'product.order.line'

    task_id = fields.Many2one('project.task', ondelete='cascade')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_progress = fields.Float(compute='_compute_task_progress', store=True)
    product_ids = fields.One2many('product.order.line', 'task_id', string="Order Lines", copy=True)
    facility_id = fields.Many2one('package.config', string="Facility", domain="[('is_facility', '=', True)]")
    # state_id = fields.Many2one('project.task.state')
    equipment_id = fields.Many2one('atlas.maintenance.equipment')
    planned_date_begin = fields.Datetime(tracking=True)
    parent_id = fields.Many2one(tracking=True)
    partner_id = fields.Many2one(tracking=True)
    partner_phone = fields.Char(tracking=True)
    tag_ids = fields.Many2many('project.tags', tracking=True)
    is_maintenance_project = fields.Boolean(related='project_id.is_maintenance_project', store=True)
    task_progress_percentage = fields.Integer(string="Progress (%)", tracking=True)
    opportunity_type = fields.Selection(related='project_id.opportunity_type', tracking=True, readonly=True, store=True)
    project_type_id = fields.Many2one(related='project_id.project_type_id', string="Project Type", tracking=True, readonly=False, store=True)
    weightage = fields.Float(string="Weightage (%)", store=True, copy=False, tracking=True)
    sale_line_id = fields.Many2one('sale.order.line', tracking=True)

    @api.constrains('weightage', 'stage_id', 'project_id', "task_progress_percentage")
    def _compute_task_progress(self):
        for task in self.filtered('project_id'):
            if task.weightage < 0 or task.weightage > 100:
                raise UserError(_("Weightage can be under 0 to 100."))

            project = task.project_id
            stage = task.stage_id
            if stage:
                current_stage_tasks = project.task_ids.filtered(lambda t: t.stage_id.id == stage.id)
                tot_percent = round(sum(current_stage_tasks.mapped('weightage')), 2)
                if tot_percent < 0 or tot_percent > 100:
                    raise UserError(_("Total percentage of all tasks of this project and stage must be under 0 to 100.\nCurrent sum is %s") % (tot_percent))

            if task.task_progress_percentage < 0 or task.task_progress_percentage > 100:
                raise UserError(_("Total Progress (%)  must be under 0 to 100"))

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if vals.get('state'):
            self._update_progress_percentage()

        if vals.get('task_progress_percentage'):
            self.project_id._compute_tot_completion()

        if vals.get('weightage') and self.stage_id.weightage:
            self.stage_id._compute_weightage()
            if vals.get('task_progress_percentage') or self.task_progress_percentage:
                self.project_id._compute_tot_completion()

        return res

    def _update_progress_percentage(self):
        progress_done = 100.0
        progress_not_done = 0.0
        for task in self:
            if task.state == '1_done':
                task.task_progress_percentage = progress_done
            else:
                task.task_progress_percentage = progress_not_done

            task.project_id._compute_tot_completion()

    @property
    def OPEN_STATES(self):
        """
            Replaced for adding or for recalculate the total weightage of stages.
            getting all the states for it not removing the closing states.

            Return a list of the technical names complementing the CLOSED_STATES, a.k.a the open states.
        """
        return list(set(self._fields['state'].get_values(self.env)))


class ProjectTaskState(models.Model):
    _name = "project.task.state"
    _description = "project.task.state"

    name = fields.Char(required=True)
    is_hold_stage = fields.Boolean(string="Is Hold Stage?")


class PackageConfig(models.Model):
    _inherit = 'package.config'

    project_id = fields.Many2one('project.project', domain="[('active', '=', False)]")


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    project_tmp_id = fields.Many2one('project.project', string="Project Template", domain="[('active', '=', False)]")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    facility_ids = fields.One2many('facility.facility', 'sale_order_id', string="Facility")
    start_date = fields.Date(required=False)
    end_date = fields.Date(required=False)
    project_tmp_id = fields.Many2one('project.project', string="Project Template", domain="[('active', '=', False)]", tracking=True)
    project_type_detail_id = fields.Many2one('project.type.detail', tracking=True, string="Project Type Detail", required=True)

    def action_confirm(self):
        if self.opportunity_id:
            stage = self.env['crm.stage'].search([('code', '=', 'CLOSE')], limit=1)
            if stage:
                self.opportunity_id.stage_id = stage.id

        res = super(SaleOrder, self).action_confirm()
        if self.root_facility_ids or self.project_tmp_id:
            self.facility_ids.write({'partner_id': self.partner_id.id})
            if not self.project_id:
                if self.root_facility_ids:
                    tmpl_project_ids = self.root_facility_ids.mapped('project_id')
                elif self.project_tmp_id:
                    tmpl_project_ids = self.project_tmp_id

                for tmpl_project_id in tmpl_project_ids:
                    root_facility_ids = self.root_facility_ids.filtered(lambda f: f.project_id == tmpl_project_id)
                    proj_name = self.name
                    day_id = self.day_ids
                    number_of_days_per_week = self.number_of_days_per_week
                    if self.opportunity_id:
                        # opportunity_id.stage_id.name == 'Closed'
                        proj_name = proj_name + ' : ' + self.opportunity_id.name

                    project_id = tmpl_project_id.with_context({'copy_task': False}).copy({
                        'sale_order_id': self.id,
                        'name': proj_name,
                        'package_facility_ids': [(6, 0, root_facility_ids.ids)],
                        'type_ids': False,
                        'task_ids': False,
                        'partner_id': self.partner_id.id,
                        'project_adress': self.partner_shipping_id.id or self.partner_id.id,
                        'project_city': self.partner_shipping_id.area_id.id if self.partner_shipping_id.area_id else False,
                        'date_start': self.start_date,
                        'date_end': self.end_date,
                        'opportunity_type': self.opportunity_type,
                        'day_ids': day_id,
                        'number_of_days_per_week': number_of_days_per_week,
                        'is_project_template': True,
                        'project_type_detail_id': self.project_type_detail_id.id,
                        'active': True,
                    })

                    attachments = self.env['ir.attachment'].search([('res_model', '=', 'sale.order'), ('res_id', '=', self.id)])
                    if self.opportunity_id:
                        attachments |= self.env['ir.attachment'].search([('res_model', '=', 'crm.lead'), ('res_id', '=', self.opportunity_id.id)])
                    for attach in attachments:
                        attach.copy(default={'res_model': 'project.project', 'res_id': project_id.id})

                    self.project_id = project_id.id
                    self.facility_ids.write({'facility_project_id': project_id.id})
                    for root_facility_id in root_facility_ids:
                        task_type_list = []
                        for type_id in tmpl_project_id.type_ids:
                            TaskType = self.env['project.task.type'].sudo().create({
                                'name': type_id.name,
                                'fold': type_id.fold,
                                'sequence': type_id.sequence,
                                'weightage': type_id.weightage,
                                'facility_id': root_facility_id.id,
                                'sms_template_id': type_id.sms_template_id,
                                'mail_template_id': type_id.mail_template_id,
                            })
                            task_type_list.append(TaskType.id)

                        if task_type_list and project_id:
                            project_id.sudo().write({
                                'type_ids': [(6, 0, task_type_list)]
                            })
                        for tmpl_project_task in self.env['project.task'].search([('project_id', '=', tmpl_project_id.id), ('active', '=', False)]):
                            stage = project_id.type_ids.filtered(lambda t: t.name == tmpl_project_task.stage_id.name and t.facility_id == root_facility_id)
                            tmpl_project_task.copy({
                                'name': tmpl_project_task.name,
                                'active': True,
                                'project_id': project_id.id,
                                'facility_id': root_facility_id.id,
                                'stage_id':  stage.id,
                                'weightage': tmpl_project_task.weightage,
                            })

                    if not root_facility_ids:
                        task_type_list = []
                        for type_id in tmpl_project_id.type_ids:
                            TaskType = self.env['project.task.type'].sudo().create({
                                'name': type_id.name,
                                'fold': type_id.fold,
                                'sequence': type_id.sequence,
                                'weightage': type_id.weightage,
                                'sms_template_id': type_id.sms_template_id,
                                'mail_template_id': type_id.mail_template_id,
                            })
                            task_type_list.append(TaskType.id)

                        if task_type_list and project_id:
                            project_id.sudo().write({
                                'type_ids': [(6, 0, task_type_list)]
                            })
                        for tmpl_project_task in self.env['project.task'].search([('project_id', '=', tmpl_project_id.id), ('active', '=', False)]):
                            stage = project_id.type_ids.filtered(lambda t: t.name == tmpl_project_task.stage_id.name)
                            tmpl_project_task.copy({
                                'name': tmpl_project_task.name,
                                'active': True,
                                'project_id': project_id.id,
                                'stage_id': stage and stage[0].id,
                                'weightage': tmpl_project_task.weightage,
                            })

        if self.project_id:
            self.order_line.write({'project_id': self.project_id.id})

        if self.picking_ids and self.project_id:
            vals = {'project_id': self.project_id.id}
            if self.analytic_account_id:
                vals.update({'account_analytic_id': self.analytic_account_id.id})
            self.picking_ids.write(vals)

            moves = self.picking_ids.move_ids_without_package
            if moves:
                moves.write({"project_id": self.project_id.id})

        return res

    @api.onchange("sale_order_template_id")
    def onchange_is_project_tmp(self):
        if self.sale_order_template_id:
            self.project_tmp_id = self.sale_order_template_id.project_tmp_id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    hide_price = fields.Boolean(related='product_template_id.hide_price')


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    team_id = fields.Many2one(related="project_id.team_id", store=True)
    date_end = fields.Datetime(related='task_id.date_end', store=True)
    stage_id = fields.Many2one(related='task_id.stage_id', store=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_equipment = fields.Boolean(string="Is Equipment?", tracking=True)
    phase = fields.Selection([('one', '1'), ('three', '3')])
    electrical_load = fields.Float(string="Electrical Load(KW)")
    hide_price = fields.Boolean(string="Hide Price from Sales Order/Invoice/Invoices without Payment and Atlas Invoice reports.")

    @api.onchange("is_equipment", "is_pack")
    def onchange_is_equipment(self):
        if self.is_equipment:
            self.is_pack = False

        if self.is_pack:
            self.is_equipment = False


class AtlasMaintenanceEquipment(models.Model):
    _name = 'atlas.maintenance.equipment'
    _description = "Atlas Maintenance Equipment"

    sr_number = fields.Char(store=True)
    product_id = fields.Many2one("product.product", string="Product", domain="[('is_equipment', '=', True)]")
    name = fields.Char(related='product_id.name', required=True, translate=True)
    compute_sr_number = fields.Integer(string="Invisible Field")
    description = fields.Text(store=True)
    source = fields.Selection([('internal', 'Internal'), ('external', 'External')])
    installation_date = fields.Date()
    warranty_start_date = fields.Date()
    warranty_end_date = fields.Date()
    contract_number = fields.Char()
    issue_number = fields.Date()
    status = fields.Selection([
        ('new', 'New'), ('installed', 'Installed'), ('has_issue', 'Has Issue'), ('repaired', 'Repaired'), ('scrapped', 'Scrapped')
    ], default='new', string="Status", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer Address")
    project_id = fields.Many2one('project.project')
    package_facility_ids = fields.Many2many('package.config', string="Facilities", domain="[('is_facility', '=', True)]")
    facility_id = fields.Many2one('facility.facility', string="Facility", readonly=False)
    quant_done = fields.Float(string="Quantity")
    phase = fields.Selection([('one', '1'), ('three', '3')])
    electrical_load = fields.Float(string="Electrical Load(KW)")

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.description = rec.product_id.display_name
