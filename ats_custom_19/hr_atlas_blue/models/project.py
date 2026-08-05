# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, _, api, tools


class Project(models.Model):
    _inherit = 'project.project'

    def _compute_attendance(self):
        Attendance = self.env['hr.attendance']
        for rec in self:
            attendances = Attendance.search([('project_id', '=', rec.id)])
            rec.attendance_count = len(attendances)

    employee_ids = fields.Many2many('hr.employee', string="Employees", readonly=True, tracking=True)

    restaurant_line_ids = fields.One2many('project.restaurant.line', 'project_id', string="Restaurant Lines", tracking=True)

    restaurant_ids = fields.One2many('fleet.restaurant', 'project_id', string="Restaurants", tracking=True)

    vehicle_line_ids = fields.One2many('project.vehicle.line', 'project_id', string="Vehicles", tracking=True)

    number = fields.Char(string="Project Code", copy=False, tracking=True)
    project_months = fields.Integer(string="Project Months", tracking=True)
    partner_fees = fields.Float(string="Partner Fees", tracking=True)
    hours_count = fields.Float(string="Actual Hours", tracking=True)
    res_allocation_by = fields.Selection([('complete', 'Complete Project'), ('monthly', 'Monthly')], string="Resource Cost By", default="complete", tracking=True)
    sale_cost_total = fields.Float(compute='_compute_cost_sale', string="Total Sale Cost", store=True, tracking=True)
    cost_total = fields.Float(compute='_compute_cost_sale', string="Total Cost", store=True, tracking=True)
    margin_total = fields.Float(compute='_compute_cost_sale', string="Margin Diff", store=True, tracking=True)
    attendance_ids = fields.One2many('hr.attendance', 'project_id', string="Attendance", tracking=True)
    invoice_id = fields.Many2one('account.move', string="Invoice", tracking=True)
    attendance_count = fields.Integer(string="Attendance Count", compute='_compute_attendance', tracking=True)
    month_attedance_ids = fields.One2many('hr.attendance.month.line', 'project_id', string="Monthly Attendances", tracking=True)
    fleet_ids = fields.Many2many('fleet.vehicle', string="Fleets", readonly=True, tracking=True)
    fleet_history_ids = fields.One2many('history.project.fleet', 'project_id', string="Fleet History", tracking=True)
    date_start = fields.Date(string="Start Date", store=True, tracking=True)
    end_date = fields.Date(string="Project End Date", tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', tracking=True)
    privacy_visibility = fields.Selection(tracking=True)
    allowed_internal_user_ids = fields.Many2many('res.users', tracking=True)
    company_id = fields.Many2one('res.company', tracking=True)
    allow_timesheets = fields.Boolean(tracking=True)
    allow_timesheet_timer = fields.Boolean(tracking=True)
    allow_billable = fields.Boolean(tracking=True)
    allow_material = fields.Boolean(tracking=True)
    is_fsm = fields.Boolean(tracking=True)
    allow_worksheets = fields.Boolean(tracking=True)
    allow_forecast = fields.Boolean(tracking=True)
    allow_subtasks = fields.Boolean(tracking=True)

    project_value = fields.Float(string="Project Value", tracking=True)
    project_cost = fields.Float(string="Project Cost", tracking=True)
    is_project_value_can_update = fields.Boolean(string="Is Project Values Update", compute='_compute_project_values_update',
                                                 help="It is used make the above fields readonly or editable according to the group 'group_update_project_value_cost'")

    def _compute_project_values_update(self):
        for rec in self:
            if not self.env.user.has_group('hr_atlas_blue.group_update_project_value_cost'):
                rec.is_project_value_can_update = False
            else:
                rec.is_project_value_can_update = True

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            args += ['|', '|', ('number', 'ilike', name), ('name', 'ilike', name)]

        return super(Project, self).name_search(name=name, args=args, operator=operator, limit=limit)

    def _compute_month_attendance(self):
        # HrAttendance = self.env['hr.attendance']
        for rec in self:
            record_list = []
            sql_query = '''
                SELECT
                    TO_CHAR(ha.check_in, 'YYYY/Month') AS month,
                    ha.employee_id AS employee_id,
                    sum(ha.worked_hours)
                FROM
                    hr_attendance ha
                    LEFT JOIN hr_employee he ON he.id=ha.employee_id
                WHERE
                    ha.project_id = %s
                GROUP BY ha.check_in, ha.employee_id
            '''
            self.env.cr.execute(sql_query, (rec.id,))
            # res = self.env.cr.fetchall()
            for row in self.env.cr.fetchall():
                record_list.append((0, 0, {
                    'name': row[0],
                    'employee_id': row[1],
                    'worked_hours': row[2],
                }))

            rec.month_attedance_ids = record_list

    def action_view_attedance(self):
        self.ensure_one()
        action = self.env.ref('hr_attendance.hr_attendance_action').sudo().read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {'default_project_id': self.id}

        return action

    @api.depends('employee_cost_lines')
    def _compute_cost_sale(self):
        for rec in self:
            total_cost = sum([line.planned_cost_hours for line in rec.employee_cost_lines])
            total_sale_cost = sum([line.sale_cost_hours for line in rec.employee_cost_lines])
            rec.sale_cost_total = total_sale_cost
            rec.cost_total = total_cost
            rec.margin_total = (total_sale_cost - total_cost)

    def action_create_invoice(self):
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(_("You have to select Customer before create Invoice!"))

        invoice_line_ids = []

        if self.partner_fees > 0.0:
            invoice_line_ids.append((0, 0, {
                'name': 'Partner Fees',
                'quantity': 1,
                'price_unit': self.partner_fees,
            }))

        for emp_cost in self.employee_cost_lines:
            invoice_line_ids.append((0, 0, {
                'name': emp_cost.employee_id.name,
                'quantity': 1,
                'price_unit': emp_cost.sale_cost_hours,
            }))

        for other_cost in self.other_cost_lines:
            name = other_cost.product_id.get_product_multiline_description_sale()
            invoice_line_ids.append((0, 0, {
                'product_id': other_cost.product_id.id,
                'name': name,
                'quantity': other_cost.product_uom_qty,
                'price_unit': other_cost.price_unit,
            }))

        vals = {
            'type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'invoice_origin': self.number,
            'invoice_payment_term_id': self.partner_id.property_payment_term_id.id,
            'project_id': self.id,
            'invoice_line_ids': invoice_line_ids,
        }
        move = self.env['account.move'].create(vals)
        self.write({'invoice_id': move.id})

        return True

    def action_view_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = self.invoice_id.id
        action['context'] = {'default_type': 'out_invoice'}

        return action

    def button_update(self):
        ProjectRestaurantLine = self.env['project.restaurant.line']
        ProjectVehicleLine = self.env['project.vehicle.line']
        for rec in self:
            employee_ids = rec.employee_cost_lines.mapped('employee_id').ids
            vehicle_ids = rec.employee_cost_lines.mapped('vehicle_id').ids
            restaurant_ids = rec.employee_cost_lines.mapped('restaurant_id').ids
            line_restaurant_ids = rec.restaurant_line_ids.mapped('restaurant_id').ids
            line_vehicle_ids = rec.vehicle_line_ids.mapped('vehicle_id').ids
            for restaurant_id in restaurant_ids:
                if restaurant_id not in line_restaurant_ids:
                    ProjectRestaurantLine.create({
                        'restaurant_id': restaurant_id,
                        'cost_price': 0.0,
                        'sale_price': 0.0,
                        'project_id': rec.id
                    })

            for vehicle_id in vehicle_ids:
                if vehicle_id not in line_vehicle_ids:
                    ProjectVehicleLine.create({
                        'vehicle_id': vehicle_id,
                        'cost_price': 0.0,
                        'sale_price': 0.0,
                        'project_id': rec.id
                    })

            restaurant_lines = rec.restaurant_line_ids.filtered(lambda x: x.restaurant_id.id not in restaurant_ids)
            restaurant_lines.unlink()

            vehicle_lines = rec.vehicle_line_ids.filtered(lambda x: x.vehicle_id.id not in vehicle_ids)
            vehicle_lines.unlink()

            rec.write({'employee_ids': [(6, 0, employee_ids)]})


class ProjectTask(models.Model):
    _inherit = 'project.task'

    date_start = fields.Date(string="Date Start", tracking=True)
    task_end_date = fields.Date(string="Task End Date", store=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", tracking=True)
    restaurant_id = fields.Many2one('fleet.restaurant', string="Restaurant")
    project_id = fields.Many2one('project.project', string="Project", tracking=True)
    number = fields.Char(string="Number", readonly=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['number'] = self.env['ir.sequence'].next_by_code('project.task')

            if vals.get('date_deadline'):
                dt = fields.Datetime.to_datetime(vals['date_deadline'])
                vals['task_end_date'] = dt.date()

        return super(ProjectTask, self).create(vals_list)

    def write(self, vals):
        task = super(ProjectTask, self).write(vals)
        if vals.get('date_deadline'):
            self.task_end_date = self.date_deadline.date()

        return task


class ProjectRestaurantLine(models.Model):
    _name = 'project.restaurant.line'
    _description = "Project Restaurant Line"

    restaurant_id = fields.Many2one('fleet.restaurant', string="Restaurant")
    cost_price = fields.Float(string="Cost Price", required=True)
    sale_price = fields.Float(string="Sale Price", required=True)
    project_id = fields.Many2one('project.project', string="Project")


class ProjectVehicleLine(models.Model):
    _name = 'project.vehicle.line'
    _description = "Project Vehicle Line"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)
    cost_price = fields.Float(string="Cost Price", required=True)
    sale_price = fields.Float(string="Sale Price", required=True)
    project_id = fields.Many2one('project.project', string="Project")


class HrAttendanceMonthView(models.Model):
    _name = 'hr.attendance.month.line'
    _description = "Attendance Month"
    _auto = False

    name = fields.Char(string="Month")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    working_hours = fields.Float(string="Working Hours")
    project_id = fields.Many2one('project.project', string="Project")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'hr_attendance_month_line')
        self.env.cr.execute("""
            CREATE or REPLACE VIEW hr_attendance_month_line as (
            SELECT
                    min(ha.id) as id,
                    TO_CHAR(ha.check_in, 'YYYY/Month') AS name,
                    ha.employee_id AS employee_id,
                    sum(ha.worked_hours) AS working_hours,
                    ha.project_id AS project_id
                FROM
                    hr_attendance ha
                GROUP BY name, ha.employee_id, ha.project_id
            )
        """)


class EmployeeCost(models.Model):
    _inherit = 'employee.cost'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicles")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    restaurant_id = fields.Many2one('fleet.restaurant', string="Restaurant")

    hour_cost = fields.Float(string="Cost/Hour")
    planned_hours = fields.Float(string="Planned Hours")
    sale_hour_cost = fields.Float(string="Sale Cost/Hour")

    planned_cost_hours = fields.Float(string="Planned Hours Cost", compute='_compute_cost_hours')
    sale_cost_hours = fields.Float(string="Sale Hours Cost", compute='_compute_cost_hours')

    # price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    # actual_hours = fields.Float(string='Total Actual Hours', compute="_compute_actual_hours")
    # monthly_hours = fields.Float(string='This Month Hours', compute="_compute_actual_hours")

    regular_ot = fields.Float(string="Regular OT")
    week_ot = fields.Float(string="Week OT")
    holiday_ot = fields.Float(string="Holiday OT")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.hour_cost = 0.0
        if self.employee_id:
            self.hour_cost = self.employee_id.contract_id.cost_per_hour
            self.vehicle_id = self.employee_id.vehicle_id.id

    @api.depends('hour_cost', 'sale_hour_cost', 'planned_hours')
    def _compute_cost_hours(self):
        for rec in self:
            rec.planned_cost_hours = rec.hour_cost * rec.planned_hours
            rec.sale_cost_hours = rec.sale_hour_cost * rec.planned_hours

    # def _compute_actual_hours(self):
    #     AnalyticalLine = self.env['account.analytic.line']
    #     today = datetime.today()
    #     first_day = today.replace(day=1)
    #     last_day = first_day + relativedelta(months=1)
    #     str_dt_start = fields.Date.to_string(first_day)
    #     str_dt_end = fields.Date.to_string(last_day)
    #     for rec in self:
    #         dom = [
    #             ('project_id', '=', rec.project_id.id),
    #             ('user_id.partner_id', '=', rec.partner_id.id),
    #         ]
    #         lines = AnalyticalLine.search(dom)
    #         rec.actual_hours = sum(lines.filtered(lambda r: r.unit_amount > 0).mapped('unit_amount'))

    #         dom += [('date', '>=', str_dt_start), ('date', '<', str_dt_end)]
    #         lines = AnalyticalLine.search(dom)
    #         rec.monthly_hours = sum(lines.filtered(lambda r: r.unit_amount > 0).mapped('unit_amount'))

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     if self.partner_id:
    #         self.hour_cost = self.partner_id.hour_cost

    # @api.depends('planned_hours', 'hour_cost')
    # def _compute_amount(self):
    #     for rec in self:
    #         rec.price_subtotal = rec.planned_hours * rec.hour_cost
