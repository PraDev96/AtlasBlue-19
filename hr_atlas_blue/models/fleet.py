# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class FleetDivision(models.Model):
    _name = 'fleet.division'
    _description = "Fleet Division"

    name = fields.Char(string="Name", required=True)
    fleet_vehicle_count = fields.Integer(compute='_compute_fleet_vehicle_count', string="Fleet Vehicle Count")
    fleet_vehilce_ids = fields.One2many('fleet.vehicle', 'fleet_division_id', string="Fleet Vehicles")

    @api.depends('fleet_vehilce_ids')
    def _compute_fleet_vehicle_count(self):
        for rec in self:
            rec.fleet_vehicle_count = len(rec.fleet_vehilce_ids.ids)

    def action_view_fleet_vehicle(self):
        action = self.env.ref('fleet.fleet_vehicle_action').sudo().read()[0]
        action['domain'] = [('fleet_division_id', '=', self.id)]
        action['context'] = {'default_fleet_division_id': self.id}

        return action


class FleetLocation(models.Model):
    _name = 'fleet.location'
    _description = "Fleet Location"

    name = fields.Char(string="Name", required=True)
    fleet_vehicle_count = fields.Integer(compute='_compute_fleet_vehicle_count', string="Fleet Vehicle Count")
    fleet_vehilce_ids = fields.One2many('fleet.vehicle', 'location_id', string="Fleet Vehicles")

    @api.depends('fleet_vehilce_ids')
    def _compute_fleet_vehicle_count(self):
        for rec in self:
            rec.fleet_vehicle_count = len(rec.fleet_vehilce_ids.ids)

    def action_view_fleet_vehicle(self):
        action = self.env.ref('fleet.fleet_vehicle_action').sudo().read()[0]
        action['domain'] = [('location_id', '=', self.id)]
        action['context'] = {'default_location_id': self.id}

        return action


class FleetGPS(models.Model):
    _name = 'fleet.gps'
    _description = "GPS"

    name = fields.Char(string="IMEI Number", required=True)
    sim_ser_number = fields.Char(string="Sim Serial Number", required=True)
    sim_phone_number = fields.Integer(string="Sim Phone Number", required=True)
    install_date = fields.Date(string="Installation Date", required=True)


class FleetCondition(models.Model):
    _name = 'fleet.condition'
    _description = "Fleet Condition"

    name = fields.Char(string="Name", required=True)
    fleet_vehicle_count = fields.Integer(compute='_compute_fleet_vehicle_count', string="Fleet Vehicle Count")
    fleet_vehilce_ids = fields.One2many('fleet.vehicle', 'condition_id', string="Fleet Vehicles")

    @api.depends('fleet_vehilce_ids')
    def _compute_fleet_vehicle_count(self):
        for rec in self:
            rec.fleet_vehicle_count = len(rec.fleet_vehilce_ids.ids)

    def action_view_fleet_vehicle(self):
        action = self.env.ref('fleet.fleet_vehicle_action').sudo().read()[0]
        action['domain'] = [('condition_id', '=', self.id)]
        action['context'] = {'default_condition_id': self.id}

        return action


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    fleet_logo = fields.Binary(string="Fleet Image")
    product_id = fields.Many2one('product.product', string="Product")
    project_id = fields.Many2one('project.project', string="Project")
    # project_type_id = fields.Many2one('project.type', related='project_id.project_type_id', store=True)
    file_ids = fields.One2many('employee.document', 'fleet_vehicle_id', string="Files")
    file_count = fields.Integer(string="Total Files", compute="_compute_file_count")
    histroy_fleet_employee_ids = fields.One2many('history.project.fleet', 'fleet_vehicle_id', string="History Fleet")
    state = fields.Selection([
        ('parking', 'Parking'),
        ('project', 'Project'),
        ('custody', 'Custody'),
        ('stolen', 'Stolen'),
        ('accident', 'Accident')], string="Status", default='parking', readonly=True)
    move_ids = fields.One2many('stock.move', 'fleet_vehicle_id', string="Moves")
    cubic_capacity = fields.Char(string="Cubic Capacity")
    internal_reference = fields.Char(string="Internal Reference")
    fuel_type = fields.Selection(selection_add=[('red_full', 'Red Full ( Premier )')])
    condition = fields.Char(string="Old Condition")
    condition_id = fields.Many2one('fleet.condition', string="Condition")
    partner_id = fields.Many2one('res.partner', string="Partner")
    fleet_division_id = fields.Many2one('fleet.division', string="Division")
    sponser_id = fields.Many2one('fleet.sponser', string="Sponsor")
    acquisition_date = fields.Date(default=fields.Date.today())
    location_id = fields.Many2one('fleet.location', string="Location")
    location = fields.Char(string="Old Location")

    fleet_movement_ids = fields.One2many('fleet.vehicle.movement', 'fleet_id', string="Fleet Movement")

    driver_history_count = fields.Integer(compute='_compute_driver_history', string="Driver History Count")
    driver_vehicle_history_ids = fields.One2many('driver.vehicle.history', 'fleet_id', string="Driver Vehicle History")

    register_expiry_date = fields.Date(string="Register Expiry Date")

    employee_vehicle_history_count = fields.Integer(compute='_compute_employee_vehicle_history', string="Employee Vehicle History Count")
    gps_id = fields.Many2one('fleet.gps', string="GPS")

    sim_ser_number = fields.Char(related='gps_id.sim_ser_number')
    sim_phone_number = fields.Integer(related='gps_id.sim_phone_number')
    install_date = fields.Date(related='gps_id.install_date')

    def _compute_employee_vehicle_history(self):
        HistoryEmployeeVehicle = self.env['history.employee.vehicle']
        for rec in self:
            employee_vehicles = HistoryEmployeeVehicle.search([('employee_id', '=', rec.emp_driver_id.id)])
            rec.employee_vehicle_history_count = len(employee_vehicles.ids)

    def action_employee_vehicle_history(self):
        self.ensure_one()
        action = self.env.ref('hr_atlas_blue.action_history_employee_vehicle').sudo().read()[0]
        action['domain'] = [('employee_id', '=', self.emp_driver_id.id)]
        action['context'] = {
            'default_employee_id': self.emp_driver_id.id,
            'search_default_employee_id': self.emp_driver_id.id
        }

        return action

    def _compute_driver_history(self):
        for rec in self:
            rec.driver_history_count = len(rec.emp_driver_id.histroy_project_employee_ids.ids)

    def action_driver_history(self):
        self.ensure_one()
        action = self.env.ref('hr_atlas_blue.history_project_employee_action').sudo().read()[0]
        action['domain'] = [('employee_id', '=', self.emp_driver_id.id)]
        action['context'] = {
            'default_employee_id': self.emp_driver_id.id,
            'search_default_employee_id': self.emp_driver_id.id
        }

        return action

    def _compute_file_count(self):
        for rec in self:
            rec.file_count = len(rec.file_ids.ids)

    def action_project(self):
        self.write({'state': 'project'})

    def action_stolen(self):
        self.write({'state': 'stolen'})

    def action_custody(self):
        self.write({'state': 'custody'})

    def action_accident(self):
        self.write({'state': 'accident'})

    def action_parking(self):
        self.write({'state': 'parking'})

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        Project = self.env['project.project']
        project_id = self.env.context.get('from_project_id')
        if project_id:
            project = Project.browse(project_id)
            args += [('id', 'in', project.fleet_ids.ids)]

        if self.env.context.get('fleet_ids'):
            fleet_ids = self.env.context['fleet_ids']
            if fleet_ids and fleet_ids[0] and fleet_ids[0][2]:
                args += [('id', 'in', fleet_ids[0][2])]
            else:
                args += [('id', 'in', [])]

        return super(FleetVehicle, self).name_search(name=name, args=args, operator=operator, limit=limit)

    def unlink(self):
        HistoryProjectFleet = self.env['history.project.fleet']
        for vehicle in self:
            historys = HistoryProjectFleet.search([('fleet_vehicle_id', '=', vehicle.id)])
            if historys:
                raise ValidationError(_("You can not delete fleet %s which have Project History!") % (vehicle.license_plate,))

        return super(FleetVehicle, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        Product = self.env['product.product'].sudo()
        DriverVehicleHistory = self.env['driver.vehicle.history']
        EmployeeVehicleHistory = self.env['history.employee.vehicle']
        fleet_vehicle = super(FleetVehicle, self).create(vals_list)
        for vals in vals_list:
            if not self.env.context.get('from_product', False):
                Product.with_context(from_fleet=True).create({
                    'name': vals.get('license_plate'),
                    'categ_id': 1,
                    'vehicle_ok': True,
                    'model_id': vals.get('model_id'),
                    'license_plate': vals.get('license_plate'),
                    'vehicle_id': fleet_vehicle.id,
                    'company_id': fleet_vehicle.company_id.id,
                    'type': 'product',
                })

            if vals.get('emp_driver_id'):
                DriverVehicleHistory.create({
                    'to_employee_id': vals['emp_driver_id'],
                    'fleet_id': fleet_vehicle.id,
                    'date': fields.Datetime.now(),
                })

                EmployeeVehicleHistory.create({
                    'employee_id': vals['emp_driver_id'],
                    'fleet_id': fleet_vehicle.id,
                    'from_date': fields.Datetime.now(),

                })

        return fleet_vehicle

    def write(self, vals):
        FleetMovement = self.env['fleet.vehicle.movement']
        DriverVehicleHistory = self.env['driver.vehicle.history']
        EmployeeVehicleHistory = self.env['history.employee.vehicle']
        for fleet in self:
            if vals.get('state'):
                new_vals = {
                    'date_state': fields.Datetime.now(),
                    'from_state': fleet.state,
                    'to_state': vals['state'],
                    'fleet_id': fleet.id,
                }
                if 'project_id' in vals:
                    new_vals.update({
                        'from_project_id': fleet.project_id.id,
                        'to_project_id': vals['project_id'],
                    })

                if self.env.context.get('start_date'):
                    new_vals['date_state'] = self.env.context['start_date']

                FleetMovement.create(new_vals)

            if 'project_id' in vals and not vals.get('state'):
                new_vals = {
                    'date_state': fields.Date.today(),
                    'from_state': fleet.state,
                    'to_state': fleet.state,
                    'fleet_id': fleet.id,
                    'from_project_id': fleet.project_id.id,
                    'to_project_id': vals['project_id'],
                }

                if self.env.context.get('start_date'):
                    new_vals['date_state'] = self.env.context['start_date']

                FleetMovement.create(new_vals)

            if 'emp_driver_id' in vals and vals.get('emp_driver_id'):
                DriverVehicleHistory.create({
                    'from_employee_id': fleet.emp_driver_id.id,
                    'to_employee_id': vals['emp_driver_id'],
                    'fleet_id': fleet.id,
                    'date': fields.Datetime.now(),
                })

                employee_history = EmployeeVehicleHistory.search([('employee_id', '=', fleet.emp_driver_id.id), ('to_date', '=', False)])
                employee_history.write({'to_date': fields.Datetime.now()})

                EmployeeVehicleHistory.create({
                    'employee_id': vals['emp_driver_id'],
                    'fleet_id': fleet.id,
                    'from_date': fields.Datetime.now(),
                })

            if 'emp_driver_id' in vals and not vals.get('emp_driver_id'):
                employee_history = EmployeeVehicleHistory.search([('employee_id', '=', fleet.emp_driver_id.id), ('to_date', '=', False)])
                employee_history.write({'to_date': fields.Datetime.now()})
                if not employee_history:
                    EmployeeVehicleHistory.create({
                        'employee_id': fleet.emp_driver_id.id,
                        'fleet_id': fleet.id,
                        'to_date': fields.Datetime.now(),
                    })

        return super(FleetVehicle, self).write(vals)

    def action_fleet_document(self):
        self.ensure_one()
        action = self.env.ref('boutiqaat_hr_base.emp_document_action').sudo().read()[0]
        action['domain'] = [('fleet_vehicle_id', '=', self.id)]
        action['context'] = {'default_fleet_vehicle_id': self.id}

        return action

    def action_add_product(self):
        view_id = self.env.ref('delivery.choose_delivery_carrier_view_form').id
        return {
            'name': 'Add Accessory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
        }

    def action_manage_product(self):
        view_id = self.env.ref('delivery.choose_delivery_carrier_view_form').id
        return {
            'name': 'Manage Accessory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
        }


class EmployeeDocument(models.Model):
    _inherit = 'employee.document'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet Vehicle")


class HistoryProjectFleet(models.Model):
    _name = 'history.project.fleet'
    _description = "History Project Fleet"

    project_id = fields.Many2one('project.project', string="Project")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet Vehicle")


class FleetVehicleAssignationLog(models.Model):
    _inherit = "fleet.vehicle.assignation.log"

    # driver_id = fields.Many2one('hr.employee')
    driver_id = fields.Many2one('res.partner', string="Driver", required=True)


class FleetVehicleLogServices(models.Model):
    _name = 'fleet.vehicle.log.services'
    _inherit = ['fleet.vehicle.log.services', 'mail.thread', 'mail.activity.mixin']

    invoice_id = fields.Many2one('account.move', string="Invoice")
    services_line_ids = fields.One2many('fleet.vehicle.log.services.line', 'log_service_line_id', string="Services Lines")
    move_ids = fields.One2many('stock.move', 'fleet_log_services_id', string="Moves")
    is_consumed = fields.Boolean(string="Is Consumed?")
    fleet_amount = fields.Float(string="Amount")
    # compute='_compute_amount', inverse='_inverse_amount', store=True
    fleet_amount_back = fields.Float(string="Fleet Amount")
    gps_id = fields.Many2one('fleet.gps', string="GPS", related='vehicle_id.gps_id', store=True, readonly=True)
    # purchaser_id = fields.Many2one('hr.employee', string="Purchaser")

    @api.onchange('invoice_id', 'services_line_ids')
    def onchange_fleet_amount(self):
        self.amount = 0.0
        if self.invoice_id:
            self.amount = self.invoice_id.amount_total
        else:
            self.amount = sum(self.services_line_ids.mapped('total_sale_price'))

    # def _inverse_amount(self):
    #     for rec in self:
    #         rec.fleet_amount_back = rec.fleet_amount

    def action_consume(self):
        StockMove = self.env['stock.move']
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
        location_id = warehouse.lot_stock_id
        location_dest_id = self.env.ref('hr_atlas_blue.stock_fleet_locations_partner')

        stock_moves = self.env['stock.move']
        for rec in self:
            for line in rec.services_line_ids:
                stock_move = StockMove.sudo().create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.uom_id.id,
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'quantity': line.quantity,
                    'origin': line.log_service_line_id.vehicle_id.name,
                    'fleet_log_services_id': rec.id,
                })
                stock_moves += stock_move

            rec.write({'is_consumed': True})
            stock_moves._action_done()


class FleetVehicleLogServicesLine(models.Model):
    _name = 'fleet.vehicle.log.services.line'
    _description = "Fleet Vehicle Log Services Line"

    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string="UoM", required=True)
    cost_price = fields.Float(string="Cost Price", required=True)
    log_service_line_id = fields.Many2one('fleet.vehicle.log.services', string="Service Line")
    # sub_total = fields.Float(compute='_compute_price', string='Subtotal', store=True)
    sale_price = fields.Float(string="Sale Price", required=True)

    total_cost_price = fields.Float(compute='_compute_price', string="Total Cost Price", store=True)
    total_sale_price = fields.Float(compute='_compute_price', string="Total Sale Price", store=True)

    @api.depends('quantity', 'product_id')
    def _compute_price(self):
        for rec in self:
            # rec.sub_total = rec.cost_price * rec.quantity
            rec.total_sale_price = rec.product_id.lst_price * rec.quantity
            rec.total_cost_price = rec.product_id.standard_price * rec.quantity

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.uom_id = False
        self.cost_price = 0.0
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            self.cost_price = self.product_id.standard_price
            self.sale_price = self.product_id.lst_price


class FleetVehicleMovement(models.Model):
    _name = 'fleet.vehicle.movement'
    _description = "Fleet Movement"
    _order = 'date_state desc'
    _rec_name = 'date_state'

    fleet_id = fields.Many2one('fleet.vehicle', string="Fleet")
    date_state = fields.Date(string="State Date")
    from_state = fields.Selection([
        ('parking', 'Parking'),
        ('project', 'Project'),
        ('custody', 'Custody'),
        ('stolen', 'Stolen'),
        ('accident', 'Accident')], string="From Status")
    to_state = fields.Selection([
        ('parking', 'Parking'),
        ('project', 'Project'),
        ('custody', 'Custody'),
        ('stolen', 'Stolen'),
        ('accident', 'Accident')], string="To Status")
    from_project_id = fields.Many2one('project.project', string="From Project")
    to_project_id = fields.Many2one('project.project', string="To Project")


class DriverVehicleHistory(models.Model):
    _name = 'driver.vehicle.history'
    _description = "Driver Vehicle History"
    _order = 'date desc'
    _rec_name = 'date'

    fleet_id = fields.Many2one('fleet.vehicle', string="Fleet")
    date = fields.Datetime(string="Date")
    from_employee_id = fields.Many2one('hr.employee', string="From Employee")
    to_employee_id = fields.Many2one('hr.employee', string="To Employee")
