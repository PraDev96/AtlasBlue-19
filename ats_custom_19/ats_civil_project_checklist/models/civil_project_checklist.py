# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class CivilProjectChecklist(models.Model):
    _inherit = 'project.checklist'
    _order = 'create_date desc'

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id)
    checklist_type = fields.Selection([
        ('concrete', 'Concrete'),
        ('embedded_piping', 'Embedded Piping'),
        ('work_before_waterproofing', 'Work Before Waterproofing'),
        ('waterproofing', 'Waterproofing'),
        ('acrylic', 'Acrylic'),
        ('tiling', 'Tiling'),
        ('eqsi', 'EQSI'),
        ('commissioning', 'Commissioning'),
        ('service', 'Service'),
    ], string="Checklist Type", required=True, default='service', tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Approved')], string="Status", required=True, default='draft', tracking=True)
    validated_user_id = fields.Many2one('res.users', string="Approved By", tracking=True)

    # __________________________________________________ Concrete __________________________________________________
    visit_site_and_finish_floor_level = fields.Boolean(string="Concrete Visit Site", help="Concrete Visit Site and Finish Floor Level (By Client)", tracking=True)
    excavation_and_compaction = fields.Boolean(string="Excavation and Compaction", help="Concrete Excavation and Compaction", tracking=True)
    cement_block_for_pool_layout = fields.Boolean(string="Cement Block for Pool Layout", help="Cement Block for Pool Layout", tracking=True)
    casting_clearance_concrete = fields.Boolean(string="Casting the Clearance Concrete", help="Casting the Clearance Concrete", tracking=True)
    external_waterproofing = fields.Boolean(string="External Waterproofing & Protection Mortar", help="External Waterproofing and Protection Mortar", tracking=True)
    steel_reinforcement_for_floor = fields.Boolean(string="Steel Reinforcement for the Floor", help="Steel Reinforcement for the Floor", tracking=True)
    steel_reinforcement_for_walls = fields.Boolean(string="Steel Reinforcement for the Walls", help="Steel Reinforcement for the Walls", tracking=True)
    casting_reinforcement_concrete_floor = fields.Boolean(string="Casting Reinforcement for the Floor", help="Casting Reinforcement for the Floor", tracking=True)
    form_work_for_walls = fields.Boolean(string="Form Work for the Walls", help="Form Work for the Walls", tracking=True)
    casting_reinforcement_concrete_walls = fields.Boolean(string="Casting Reinforcement for the Walls", help="Casting Reinforcement for the Walls", tracking=True)
    remove_framework_and_clean = fields.Boolean(string="Remove Framework and Clean", help="Remove Framework and Clean the Site", tracking=True)
    curing_with_water = fields.Boolean(string="Curing with Water (By Client)", help="Curing with Water (By Client)", tracking=True)
    # __________________________________________________ Concrete END__________________________________________________

    # __________________________________________________ Embedded Piping __________________________________________________
    emp_floor_inlets = fields.Float(string="Floor Inlets", help="Floor Inlets", tracking=True)
    emp_vacuum_point = fields.Float(string="Vacuum Point", help="Vacuum Point", tracking=True)
    emp_main_drain = fields.Float(string="Main Drain", help="Main Drain", tracking=True)
    emp_tank_suction = fields.Float(string="Tank Suction", help="Tank Suction", tracking=True)
    emp_wall_suction = fields.Float(string="Wall Suction", help="Wall Suction", tracking=True)
    emp_filling_lines = fields.Float(string="Filling Lines", help="Filling Lines", tracking=True)
    emp_electrical_supply = fields.Float(string="Electrical Supply", help="Electrical Supply", tracking=True)
    emp_skimmer = fields.Float(string="Skimmer", help="Skimmer", tracking=True)
    emp_big_lights = fields.Float(string="Lights (Big)", help="Lights (Big)", tracking=True)
    emp_small_lights = fields.Float(string="Lights (Small)", help="Lights (Small)", tracking=True)
    emp_jets = fields.Float(string="Jets", help="Jets", tracking=True)
    emp_sump_pit = fields.Float(string="Sump Pit", help="Sump Pit", tracking=True)
    emp_drain_pipes = fields.Float(string="Drain Pipes", help="Drain Pipes", tracking=True)
    emp_location_of_junction_box = fields.Float(string="Location of Junction Box", help="Location of Junction Box", tracking=True)
    emp_air_regulator = fields.Float(string="Air Regulator", help="Air Regulator", tracking=True)
    emp_touch_switch = fields.Float(string="Touch Switch", help="Touch Switch", tracking=True)
    emp_control_switch = fields.Float(string="Control Switch", help="Control Switch", tracking=True)
    emp_water_descent = fields.Float(string="Water Descent", help="Water Descent", tracking=True)
    emp_overflow_with_drain = fields.Float(string="Overflow with Drain", help="Overflow with Drain", tracking=True)
    emp_ventilation_pipes = fields.Float(string="Ventilation Pipes", help="Ventilation Pipes", tracking=True)
    emp_location_of_control_switch = fields.Float(string="Location of Control Switch", help="Location of Control Switch", tracking=True)

    emp_pool_dimension_as_per_drawing = fields.Boolean(string="Pool Dimension as per Drawing", help="Pool Dimension as per Drawing", tracking=True)
    emp_informed_to_client = fields.Boolean(string="Informed to Client", help="If NO, Actual Dimension are Informed to Client", tracking=True)

    emp_initial_pressure_test_reading = fields.Float(string="Initial Pressure Test Reading", help="Initial Pressure Test Reading", tracking=True)
    emp_final_pressure_test_reading = fields.Float(string="Final Pressure Test Reading", help="Final Pressure Test Reading", tracking=True)

    emp_pool_size = fields.Float(string="Pool Size", help="Pool Size", tracking=True)
    emp_spa_size = fields.Float(string="SPA Size", help="SAP Size", tracking=True)
    # __________________________________________________ Embedded Piping - END __________________________________________________

    # __________________________________________________ Work Before Waterproofing __________________________________________________
    wbw_floor_inlets = fields.Float(string="wbw Floor Inlets", help="Work Before Waterproofing Floor Inlets", tracking=True)
    wbw_vacuum_point = fields.Float(string="wbw Vacuum Point", help="Work Before Waterproofing Vacuum Point", tracking=True)
    wbw_main_drain = fields.Float(string="wbw Main Drain", help="Work Before Waterproofing Main Drain", tracking=True)
    wbw_tank_suction = fields.Float(string="wbw Tank Suction", help="Work Before Waterproofing Tank Suction", tracking=True)
    wbw_wall_suction = fields.Float(string="wbw Wall Suction", help="Work Before Waterproofing Wall Suction", tracking=True)
    wbw_filling_lines = fields.Float(string="wbw Filling Lines", help="Work Before Waterproofing Filling Lines", tracking=True)
    wbw_electrical_supply = fields.Float(string="wbw Electrical Supply", help="Work Before Waterproofing Electrical Supply", tracking=True)
    wbw_skimmer = fields.Float(string="wbw Skimmer", help="Work Before Waterproofing Skimmer", tracking=True)
    wbw_big_lights = fields.Float(string="wbw Lights (Big)", help="Work Before Waterproofing Lights (Big)", tracking=True)
    wbw_small_lights = fields.Float(string="wbw Lights (Small)", help="Work Before Waterproofing Lights (Small)", tracking=True)
    wbw_jets = fields.Float(string="wbw Jets", help="Work Before Waterproofing Jets", tracking=True)
    wbw_sump_pit = fields.Float(string="wbw Sump Pit", help="Work Before Waterproofing Sump Pit", tracking=True)
    wbw_drain_pipes = fields.Float(string="wbw Drain Pipes", help="Work Before Waterproofing Drain Pipes", tracking=True)
    wbw_location_of_junction_box = fields.Float(string="wbw Location of Junction Box", help="Work Before Waterproofing Location of Junction Box", tracking=True)
    wbw_air_regulator = fields.Float(string="wbw Air Regulator", help="Work Before Waterproofing Air Regulator", tracking=True)
    wbw_touch_switch = fields.Float(string="wbw Touch Switch", help="Work Before Waterproofing Touch Switch", tracking=True)
    wbw_control_switch = fields.Float(string="wbw Control Switch", help="Work Before Waterproofing Control Switch", tracking=True)
    wbw_water_descent = fields.Float(string="wbw Water Descent", help="Work Before Waterproofing Water Descent", tracking=True)
    wbw_overflow_with_drain = fields.Float(string="wbw Overflow with Drain", help="Work Before Waterproofing Overflow with Drain", tracking=True)
    wbw_ventilation_pipes = fields.Float(string="wbw Ventilation Pipes", help="Work Before Waterproofing Ventilation Pipes", tracking=True)
    wbw_location_of_control_switch = fields.Float(string="wbw Location of Control Switch", help="Work Before Waterproofing Location of Control Switch", tracking=True)

    wbw_pool_dimension_as_per_drawing = fields.Boolean(string="wbw Pool Dimension as per Drawing", help="Work Before Waterproofing Pool Dimension as per Drawing",
                                                       tracking=True)
    wbw_informed_to_client = fields.Boolean(string="wbw Informed to Client", help="If NO, Actual Dimension are Informed to Client", tracking=True)

    wbw_initial_pressure_test_reading = fields.Float(string="wbw Initial Pressure Test Reading", help="Work Before Waterproofing Initial Pressure Test Reading", tracking=True)
    wbw_final_pressure_test_reading = fields.Float(string="wbw Final Pressure Test Reading", help="Work Before Waterproofing Final Pressure Test Reading", tracking=True)

    wbw_pool_size = fields.Float(string="wbw Pool Size", help="Work Before Waterproofing Pool Size", tracking=True)
    wbw_spa_size = fields.Float(string="wbw SPA Size", help="Work Before Waterproofing SAP Size", tracking=True)

    wbw_backwash = fields.Boolean(string="wbw BackWash", help="Work Before Waterproofing Back Wash", tracking=True)
    wbw_ventilation = fields.Boolean(string="wbw Ventilation", help="Work Before Waterproofing Ventilation", tracking=True)
    wbw_filling_line = fields.Boolean(string="wbw Filling Line", help="Work Before Waterproofing Filling Line for Work Before Waterproofing", tracking=True)
    wbw_is_electrical_supply = fields.Boolean(string="wbw is Electrical Supply", help="Work Before Waterproofing Electrical Supply", tracking=True)
    wbw_summit_pit = fields.Boolean(string="wbw Summit Pit", help="Work Before Waterproofing Summit Pit", tracking=True)
    # __________________________________________________ Work Before Waterproofing END __________________________________________________

    # __________________________________________________ Waterproofing __________________________________________________
    wp_visit_site_and_finish_floor_level = fields.Boolean(string="Waterproofing Visit Site", help="Waterproofing Visit Site and Finish Floor Level (By Client)", tracking=True)
    site_preparation = fields.Boolean(string="Site Preparation", help="Waterproofing Site Preparation", tracking=True)
    first_layer_waterproofing = fields.Boolean(string="First Layer of Waterproofing", help="Waterproofing First Layer of Waterproofing", tracking=True)
    second_layer_waterproofing = fields.Boolean(string="Second Layer of Waterproofing", help="Waterproofing Second Layer of Waterproofing", tracking=True)
    water_filling = fields.Boolean(string="Water Filling(By Client)", help="Waterproofing Water Filling (By Client)", tracking=True)
    first_reading = fields.Boolean(string="First Reading", help="Waterproofing First Reading", tracking=True)
    second_reading = fields.Boolean(string="Second Reading", help="Waterproofing Second Reading", tracking=True)
    final_reading = fields.Boolean(string="Final Reading", help="Waterproofing Final Reading", tracking=True)
    waterproofing_test_approval = fields.Boolean(string="Waterproofing Test Approval", help="Waterproofing Test Approval", tracking=True)
    # __________________________________________________ Waterproofing END__________________________________________________

    # __________________________________________________ Acrylic __________________________________________________
    surface_condition = fields.Boolean(string="Surface Condition (no cracks, chips, or discoloration)", help="Acrylic Surface Condition (no cracks, chips, or discoloration)", tracking=True)
    acrylic_join_sealant_intact = fields.Boolean(string="Acrylic Joint Sealant Intact", help="Acrylic Joint Sealant Intact", tracking=True)
    adhesion_to_substrate = fields.Boolean(string="Adhesion to Substrate", help="Acrylic Adhesion to Substrate", tracking=True)
    no_sign_of_water_leakage_or_moisture = fields.Boolean(string="No Sign of Water Leakage or Moisture", help="Acrylic No Sign of Water Leakage or Moisture", tracking=True)
    no_surface_stain_or_build_up = fields.Boolean(string="No Surface Stain or Build-Up", help="Acrylic No Surface Stain or Build-Up", tracking=True)
    structural_support_stable = fields.Boolean(string="Structural Support Stable (no movement or deflection)",
                                               help="Acrylic Structural Support Stable (no movement or deflection)", tracking=True)
    proper_drainage = fields.Boolean(string="Proper Drainage (if applicable)", help="Acrylic Proper Drainage (if applicable)", tracking=True)
    cleaning_and_maintenance_instruction = fields.Boolean(string="Cleaning and Maintenance Instruction Provided to Client",
                                                          help="Acrylic Cleaning and Maintenance Instruction Provided to Client", tracking=True)
    any_repair_done_in_the_past_year = fields.Boolean(string="Any Repair Done in the Past Year", help="Acrylic Any Repair Done in the Past Year", tracking=True)
    # __________________________________________________ Acrylic END__________________________________________________

    # __________________________________________________ Tiling __________________________________________________
    tl_visit_site = fields.Boolean(string="Tiling Visit the Site", help="Tiling Visit the Site", tracking=True)
    finish_floor_level = fields.Boolean(string="Finish Floor Level (By Client)", help="Tiling Finish Floor Level (By Client)", tracking=True)
    closing_pipes = fields.Boolean(string="Closing Pipes", help="Tiling Closing Pipes", tracking=True)
    tl_waterproofing = fields.Boolean(string="Waterproofing", help="Tiling Waterproofing", tracking=True)
    pool_testing = fields.Boolean(string="Pool Testing", help="Tiling Pool Testing", tracking=True)
    tiles_approval = fields.Boolean(string="Tiles Approval", help="Tiling Tiles Approval", tracking=True)
    tiles_delivery = fields.Boolean(string="Tiles Delivery", help="Tiling Tiles Delivery", tracking=True)
    splashing_curing = fields.Boolean(string="Splashing / Curing", help="Tiling Splashing / Curing", tracking=True)
    plastering_curing = fields.Boolean(string="Plastering/Curing", help="Tiling Plastering / Curing", tracking=True)
    tiles_laying = fields.Boolean(string="Tiles Laying / Coping / Mech Room", help="Tiling Tiles Laying / Coping / Mech Room", tracking=True)
    grouting = fields.Boolean(string="Grouting / Pool/ Mech Room", help="Tiling Grouting / Pool/ Mech Room", tracking=True)
    overflow_level = fields.Boolean(string="Overflow Level", help="Tiling Overflow Level", tracking=True)
    tiling_area_as_per_contract = fields.Boolean(string="Tiling Area as per Contract", help="Tiling Tiling Area as per Contract", tracking=True)
    actual_area_of_tiling = fields.Boolean(string="Actual Area of Tiling", help="Tiling Actual Area of Tiling", tracking=True)
    # __________________________________________________ Tiling END__________________________________________________

    # __________________________________________________ EQSI __________________________________________________
    eq_filter = fields.Float(string="EQSI Filter", help="EQSI Filter", tracking=True)
    eq_pump = fields.Float(string="EQSI Pump", help="EQSI Pump", tracking=True)
    eq_heater = fields.Float(string="EQSI Heater", help="EQSI Heater", tracking=True)
    eq_jacuzzi = fields.Float(string="EQSI Jacuzzi", help="EQSI Jacuzzi", tracking=True)
    eq_transformer = fields.Float(string="EQSI Transformer", help="EQSI Transformer", tracking=True)

    eq_ozone = fields.Float(string="EQSI Ozone / UV", help="EQSI Ozone / UV", tracking=True)
    eq_ladder = fields.Float(string="EQSI Ladder", help="EQSI Ladder", tracking=True)
    eq_sump_pump = fields.Float(string="EQSI Sump Pump", help="EQSI Sump Pump", tracking=True)
    eq_chlorinator = fields.Float(string="EQSI Chlorinator", help="EQSI Chlorinator", tracking=True)
    eq_skimmer = fields.Float(string="EQSI Skimmer", help="EQSI Skimmer", tracking=True)

    eq_control_switch = fields.Float(string="EQSI Control Switch", help="EQSI Control Switch", tracking=True)
    eq_float_valve = fields.Float(string="EQSI Float Valve", help="EQSI Float Valve", tracking=True)
    eq_gutter = fields.Float(string="EQSI Gutter", help="EQSI Gutter", tracking=True)
    eq_control_panel = fields.Float(string="EQSI Control Panel", help="EQSI Control Panel", tracking=True)
    eq_electric_work = fields.Float(string="EQSI Electric Work", help="EQSI Electric Work", tracking=True)

    eq_lights_rcb_remote = fields.Float(string="EQSI Lights RCB Remote", help="EQSI Lights RCB Remote", tracking=True)
    eq_fountain_nozzle = fields.Float(string="EQSI Fountain Nozzle", help="EQSI Fountain Nozzle", tracking=True)
    eq_deck_box = fields.Float(string="EQSI Deck Box", help="EQSI Deck Box", tracking=True)

    eq_lights_cold_white = fields.Float(string="EQSI Lights Cold-White", help="EQSI Lights Cold-White", tracking=True)
    eq_water_fall = fields.Float(string="EQSI Water Fall", help="EQSI Water Fall", tracking=True)

    eq_lights_warm_white = fields.Float(string="EQSI Lights Warm-White", help="EQSI Lights Warm-White", tracking=True)
    eq_rain_water_fountain = fields.Float(string="EQSI Rain Water Fountain", help="EQSI Rain Water Fountain", tracking=True)
    eq_cleaning_equipment = fields.Float(string="EQSI Cleaning Equipment", help="EQSI Cleaning Equipment", tracking=True)
    # __________________________________________________ EQSI END __________________________________________________

    # __________________________________________________ Commissioning __________________________________________________
    com_filter = fields.Float(string="Commissioning Filter", help="Commissioning Filter", tracking=True)
    com_pump = fields.Float(string="Commissioning Pump", help="Commissioning Pump", tracking=True)
    com_heater = fields.Float(string="Commissioning Heater", help="Commissioning Heater", tracking=True)
    com_jacuzzi = fields.Float(string="Commissioning Jacuzzi", help="Commissioning Jacuzzi", tracking=True)
    com_transformer = fields.Float(string="Commissioning Transformer", help="Commissioning Transformer", tracking=True)

    com_ozone = fields.Float(string="Commissioning Ozone / UV", help="Commissioning Ozone / UV", tracking=True)
    com_ladder = fields.Float(string="Commissioning Ladder", help="Commissioning Ladder", tracking=True)
    com_sump_pump = fields.Float(string="Commissioning Sump Pump", help="Commissioning Sump Pump", tracking=True)
    com_chlorinator = fields.Float(string="Commissioning Chlorinator", help="Commissioning Chlorinator", tracking=True)
    com_skimmer = fields.Float(string="Commissioning Skimmer", help="Commissioning Skimmer", tracking=True)

    com_control_switch = fields.Float(string="Commissioning Control Switch", help="Commissioning Control Switch", tracking=True)
    com_float_valve = fields.Float(string="Commissioning Float Valve", help="Commissioning Float Valve", tracking=True)
    com_gutter = fields.Float(string="Commissioning Gutter", help="Commissioning Gutter", tracking=True)
    com_control_panel = fields.Float(string="Commissioning Control Panel", help="Commissioning Control Panel", tracking=True)
    com_electric_work = fields.Float(string="Commissioning Electric Work", help="Commissioning Electric Work", tracking=True)

    com_lights_rcb_remote = fields.Float(string="Commissioning Lights RCB Remote", help="Commissioning Lights RCB Remote", tracking=True)
    com_fountain_nozzle = fields.Float(string="Commissioning Fountain Nozzle", help="Commissioning Fountain Nozzle", tracking=True)
    com_deck_box = fields.Float(string="Commissioning Deck Box", help="Commissioning Deck Box", tracking=True)

    com_lights_cold_white = fields.Float(string="Commissioning Lights Cold-White", help="Commissioning Lights Cold-White", tracking=True)
    com_water_fall = fields.Float(string="Commissioning Water Fall", help="Commissioning Water Fall", tracking=True)

    com_lights_warm_white = fields.Float(string="Commissioning Lights Warm-White", help="Commissioning Lights Warm-White", tracking=True)
    com_rain_water_fountain = fields.Float(string="Commissioning Rain Water Fountain", help="Commissioning Rain Water Fountain", tracking=True)
    com_cleaning_equipment = fields.Float(string="Commissioning Cleaning Equipment", help="Commissioning Cleaning Equipment", tracking=True)
    # __________________________________________________ Commissioning END __________________________________________________

    remarks = fields.Text(string="Remarks", help="Remarks", tracking=True)

    @api.model
    def default_get(self, field_list):
        """
            This is to set the employee, while create the checklist from the back-end
        """
        result = super(CivilProjectChecklist, self).default_get(field_list)
        is_from_backed = self.env.context.get("is_from_backed")
        if is_from_backed and not result.get('employee_id'):
            result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id

        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals['checklist_type'] == 'concrete':
                checklist_code = 'concrete.checklist.seq'
            elif vals['checklist_type'] == 'embedded_piping':
                checklist_code = 'embedded.piping.checklist.seq'
            elif vals['checklist_type'] == 'work_before_waterproofing':
                checklist_code = 'work.before.waterproofing.checklist.seq'
            elif vals['checklist_type'] == 'waterproofing':
                checklist_code = 'waterproofing.checklist.seq'
            elif vals['checklist_type'] == 'acrylic':
                checklist_code = 'acrylic.checklist.seq'
            elif vals['checklist_type'] == 'tiling':
                checklist_code = 'tiling.checklist.seq'
            elif vals['checklist_type'] == 'eqsi':
                checklist_code = 'eqsi.checklist.seq'
            elif vals['checklist_type'] == 'commissioning':
                checklist_code = 'commissioning.checklist.seq'
            else:
                checklist_code = 'service.checklist.seq'

            vals['name'] = self.env['ir.sequence'].next_by_code(checklist_code) or _("New")

            if not vals.get('signed_on'):
                vals['signed_on'] = fields.Datetime.now()
            if not vals.get('employee_id'):
                employee_rec = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
                vals['employee_id'] = employee_rec.id if employee_rec else False,

        return super(CivilProjectChecklist, self).create(vals_list)

    def action_checklist_validate(self):
        for record in self:
            record.state = 'validate'
            record.validated_user_id = self.env.user.id

    def action_checklist_reset_to_draft(self):
        for record in self:
            record.state = 'draft'
            record.validated_user_id = False

    @api.model
    def create_from_checklist(self, args):
        task_id = args.get('task_id', False)
        user_id = args.get('user_id', False)
        employee_rec = False
        if user_id:
            employee_rec = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)

        if task_id:
            task_rec = self.env['project.task'].sudo().browse(task_id)
            if task_rec:
                project_id = task_rec.project_id
                # Robustly identify Service project to allow multiple checklist submissions
                is_service = (
                    (project_id.project_type_id and project_id.project_type_id.name == 'Service') or
                    project_id.opportunity_type == 'service' or
                    task_rec.checklist_type == 'service'
                )

                if not is_service and task_rec.project_task_checklist_ids:
                    return True

                vals = {
                    'task_id': task_rec.id,
                    'projects_id': project_id.id,
                    'signed_on': fields.Datetime.now(),
                    'signature': args.get('signature_img'),
                    'signed_by': args.get('signature_name'),
                    'employee_id': employee_rec.id if employee_rec else False,
                }
                if is_service:
                    vals.update({
                        'tds': args.get('tds'),
                        'checklist_type': 'service',
                        'salinity': args.get('salinity'),
                        'ph_level': args.get('ph_level'),
                        'skim_pool': args.get('skim_pool'),
                        'brush_pool': args.get('brush_pool'),
                        'vacuum_pool': args.get('vacuum_pool'),
                        'total_chlorine': args.get('total_chlorine'),
                        'total_alkalinity': args.get('total_alkalinity'),
                        'calcium_hardness': args.get('calcium_hardness'),
                        'water_temperature': args.get('water_temperature'),
                        'clean_machine_room': args.get('clean_machine_room'),
                        'free_chlorin_level': args.get('free_chlorin_level'),
                        'clean_balance_tank': args.get('clean_balance_tank'),
                        'clean_pump_strainer': args.get('clean_pump_strainer'),
                        'clean_skimmer_overflow': args.get('clean_skimmer_overflow'),
                        'back_wash_filter_after': args.get('back_wash_filter_after'),
                        'back_wash_filter_before': args.get('back_wash_filter_before'),
                        'cyanuric_acid': args.get('cyanuric_Acid') or args.get('cyanuric_acid'),
                        'clean_deck_area': args.get('clean_desk_area') or args.get('clean_deck_area'),
                    })
                elif task_rec.is_checklist_task or task_rec.checklist_type:
                    vals.update({
                        'checklist_type': task_rec.checklist_type,
                        'remarks': args.get('remarks'),
                    })
                    if task_rec.checklist_type == 'concrete':
                        vals.update({
                            'curing_with_water': args.get('curing_with_water'),
                            'form_work_for_walls': args.get('form_work_for_walls'),
                            'external_waterproofing': args.get('external_waterproofing'),
                            'excavation_and_compaction': args.get('excavation_and_compaction'),
                            'casting_clearance_concrete': args.get('casting_clearance_concrete'),
                            'remove_framework_and_clean': args.get('remove_framework_and_clean'),
                            'cement_block_for_pool_layout': args.get('cement_block_for_pool_layout'),
                            'steel_reinforcement_for_floor': args.get('steel_reinforcement_for_floor'),
                            'steel_reinforcement_for_walls': args.get('steel_reinforcement_for_walls'),
                            'visit_site_and_finish_floor_level': args.get('visit_site_and_finish_floor_level'),
                            'casting_reinforcement_concrete_floor': args.get('casting_reinforcement_concrete_floor'),
                            'casting_reinforcement_concrete_walls': args.get('casting_reinforcement_concrete_walls'),
                        })
                    elif task_rec.checklist_type == 'embedded_piping':
                        vals.update({
                            'emp_jets': args.get('emp_jets'),
                            'emp_skimmer': args.get('emp_skimmer'),
                            'emp_spa_size': args.get('emp_spa_size'),
                            'emp_sump_pit': args.get('emp_sump_pit'),
                            'emp_pool_size': args.get('emp_pool_size'),
                            'emp_big_lights': args.get('emp_big_lights'),
                            'emp_main_drain': args.get('emp_main_drain'),
                            'emp_drain_pipes': args.get('emp_drain_pipes'),
                            'emp_small_lights': args.get('emp_small_lights'),
                            'emp_floor_inlets': args.get('emp_floor_inlets'),
                            'emp_vacuum_point': args.get('emp_vacuum_point'),
                            'emp_tank_suction': args.get('emp_tank_suction'),
                            'emp_wall_suction': args.get('emp_wall_suction'),
                            'emp_touch_switch': args.get('emp_touch_switch'),
                            'emp_filling_lines': args.get('emp_filling_lines'),
                            'emp_air_regulator': args.get('emp_air_regulator'),
                            'emp_water_descent': args.get('emp_water_descent'),
                            'emp_control_switch': args.get('emp_control_switch'),
                            'emp_electrical_supply': args.get('emp_electrical_supply'),
                            'emp_ventilation_pipes': args.get('emp_ventilation_pipes'),
                            'emp_informed_to_client': args.get('emp_informed_to_client'),
                            'emp_overflow_with_drain': args.get('emp_overflow_with_drain'),
                            'emp_location_of_junction_box': args.get('emp_location_of_junction_box'),
                            'emp_location_of_control_switch': args.get('emp_location_of_control_switch'),
                            'emp_final_pressure_test_reading': args.get('emp_final_pressure_test_reading'),
                            'emp_pool_dimension_as_per_drawing': args.get('emp_pool_dimension_as_per_drawing'),
                            'emp_initial_pressure_test_reading': args.get('emp_initial_pressure_test_reading'),
                        })
                    elif task_rec.checklist_type == 'work_before_waterproofing':
                        vals.update({
                            'wbw_jets': args.get('wbw_jets'),
                            'wbw_skimmer': args.get('wbw_skimmer'),
                            'wbw_spa_size': args.get('wbw_spa_size'),
                            'wbw_backwash': args.get('wbw_backwash'),
                            'wbw_sump_pit': args.get('wbw_sump_pit'),
                            'wbw_pool_size': args.get('wbw_pool_size'),
                            'wbw_summit_pit': args.get('wbw_summit_pit'),
                            'wbw_big_lights': args.get('wbw_big_lights'),
                            'wbw_main_drain': args.get('wbw_main_drain'),
                            'wbw_drain_pipes': args.get('wbw_drain_pipes'),
                            'wbw_ventilation': args.get('wbw_ventilation'),
                            'wbw_small_lights': args.get('wbw_small_lights'),
                            'wbw_filling_line': args.get('wbw_filling_line'),
                            'wbw_floor_inlets': args.get('wbw_floor_inlets'),
                            'wbw_vacuum_point': args.get('wbw_vacuum_point'),
                            'wbw_tank_suction': args.get('wbw_tank_suction'),
                            'wbw_wall_suction': args.get('wbw_wall_suction'),
                            'wbw_touch_switch': args.get('wbw_touch_switch'),
                            'wbw_water_descent': args.get('wbw_water_descent'),
                            'wbw_filling_lines': args.get('wbw_filling_lines'),
                            'wbw_air_regulator': args.get('wbw_air_regulator'),
                            'wbw_control_switch': args.get('wbw_control_switch'),
                            'wbw_electrical_supply': args.get('wbw_electrical_supply'),
                            'wbw_ventilation_pipes': args.get('wbw_ventilation_pipes'),
                            'wbw_informed_to_client': args.get('wbw_informed_to_client'),
                            'wbw_overflow_with_drain': args.get('wbw_overflow_with_drain'),
                            'wbw_is_electrical_supply': args.get('wbw_is_electrical_supply'),
                            'wbw_location_of_junction_box': args.get('wbw_location_of_junction_box'),
                            'wbw_location_of_control_switch': args.get('wbw_location_of_control_switch'),
                            'wbw_final_pressure_test_reading': args.get('wbw_final_pressure_test_reading'),
                            'wbw_pool_dimension_as_per_drawing': args.get('wbw_pool_dimension_as_per_drawing'),
                            'wbw_initial_pressure_test_reading': args.get('wbw_initial_pressure_test_reading'),
                        })
                    elif task_rec.checklist_type == 'waterproofing':
                        vals.update({
                            'final_reading': args.get('final_reading'),
                            'water_filling': args.get('water_filling'),
                            'first_reading': args.get('first_reading'),
                            'second_reading': args.get('second_reading'),
                            'site_preparation': args.get('site_preparation'),
                            'first_layer_waterproofing': args.get('first_layer_waterproofing'),
                            'second_layer_waterproofing': args.get('second_layer_waterproofing'),
                            'waterproofing_test_approval': args.get('waterproofing_test_approval'),
                            'wp_visit_site_and_finish_floor_level': args.get('wp_visit_site_and_finish_floor_level'),
                        })
                    elif task_rec.checklist_type == 'acrylic':
                        vals.update({
                            'proper_drainage': args.get('proper_drainage'),
                            'surface_condition': args.get('surface_condition'),
                            'adhesion_to_substrate': args.get('adhesion_to_substrate'),
                            'structural_support_stable': args.get('structural_support_stable'),
                            'acrylic_join_sealant_intact': args.get('acrylic_join_sealant_intact'),
                            'no_surface_stain_or_build_up': args.get('no_surface_stain_or_build_up'),
                            'any_repair_done_in_the_past_year': args.get('any_repair_done_in_the_past_year'),
                            'no_sign_of_water_leakage_or_moisture': args.get('no_sign_of_water_leakage_or_moisture'),
                            'cleaning_and_maintenance_instruction': args.get('cleaning_and_maintenance_instruction'),
                        })
                    elif task_rec.checklist_type == 'tiling':
                        vals.update({
                            'grouting': args.get('grouting'),
                            'pool_testing': args.get('pool_testing'),
                            'tiles_laying': args.get('tiles_laying'),
                            'closing_pipes': args.get('closing_pipes'),
                            'tl_visit_site': args.get('tl_visit_site'),
                            'tiles_approval': args.get('tiles_approval'),
                            'tiles_delivery': args.get('tiles_delivery'),
                            'overflow_level': args.get('overflow_level'),
                            'tl_waterproofing': args.get('tl_waterproofing'),
                            'splashing_curing': args.get('splashing_curing'),
                            'plastering_curing': args.get('plastering_curing'),
                            'finish_floor_level': args.get('finish_floor_level'),
                            'actual_area_of_tiling': args.get('actual_area_of_tiling'),
                            'tiling_area_as_per_contract': args.get('tiling_area_as_per_contract'),
                        })
                    elif task_rec.checklist_type == 'eqsi':
                        vals.update({
                            'eq_pump': args.get('eq_pump'),
                            'eq_ozone': args.get('eq_ozone'),
                            'eq_filter': args.get('eq_filter'),
                            'eq_ladder': args.get('eq_ladder'),
                            'eq_heater': args.get('eq_heater'),
                            'eq_gutter': args.get('eq_gutter'),
                            'eq_jacuzzi': args.get('eq_jacuzzi'),
                            'eq_skimmer': args.get('eq_skimmer'),
                            'eq_deck_box': args.get('eq_deck_box'),
                            'eq_sump_pump': args.get('eq_sump_pump'),
                            'eq_water_fall': args.get('eq_water_fall'),
                            'eq_transformer': args.get('eq_transformer'),
                            'eq_chlorinator': args.get('eq_chlorinator'),
                            'eq_float_valve': args.get('eq_float_valve'),
                            'eq_control_panel': args.get('eq_control_panel'),
                            'eq_electric_work': args.get('eq_electric_work'),
                            'eq_control_switch': args.get('eq_control_switch'),
                            'eq_fountain_nozzle': args.get('eq_fountain_nozzle'),
                            'eq_lights_rcb_remote': args.get('eq_lights_rcb_remote'),
                            'eq_lights_cold_white': args.get('eq_lights_cold_white'),
                            'eq_lights_warm_white': args.get('eq_lights_warm_white'),
                            'eq_cleaning_equipment': args.get('eq_cleaning_equipment'),
                            'eq_rain_water_fountain': args.get('eq_rain_water_fountain'),
                        })
                    elif task_rec.checklist_type == 'commissioning':
                        vals.update({
                            'com_pump': args.get('com_pump'),
                            'com_ozone': args.get('com_ozone'),
                            'com_gutter': args.get('com_gutter'),
                            'com_filter': args.get('com_filter'),
                            'com_heater': args.get('com_heater'),
                            'com_ladder': args.get('com_ladder'),
                            'com_jacuzzi': args.get('com_jacuzzi'),
                            'com_skimmer': args.get('com_skimmer'),
                            'com_deck_box': args.get('com_deck_box'),
                            'com_sump_pump': args.get('com_sump_pump'),
                            'com_water_fall': args.get('com_water_fall'),
                            'com_transformer': args.get('com_transformer'),
                            'com_chlorinator': args.get('com_chlorinator'),
                            'com_float_valve': args.get('com_float_valve'),
                            'com_control_panel': args.get('com_control_panel'),
                            'com_electric_work': args.get('com_electric_work'),
                            'com_control_switch': args.get('com_control_switch'),
                            'com_fountain_nozzle': args.get('com_fountain_nozzle'),
                            'com_lights_warm_white': args.get('com_lights_warm_white'),
                            'com_lights_rcb_remote': args.get('com_lights_rcb_remote'),
                            'com_lights_cold_white': args.get('com_lights_cold_white'),
                            'com_cleaning_equipment': args.get('com_cleaning_equipment'),
                            'com_rain_water_fountain': args.get('com_rain_water_fountain'),
                        })

                checklist_id = self.env['project.checklist'].sudo().create(vals)
                if checklist_id and checklist_id.checklist_type == 'service':
                    checklist_id.mail_sent(checklist_id)
                    checklist_id.write({'mail_sent_done': True})
                    if checklist_id.projects_id:
                        data_lst = ['Task : %s' % (checklist_id.task_id.name), 'Employee: %s' % (checklist_id.employee_id.name), 'Date: %s' % (checklist_id.date)]
                        self.env['mail.message'].sudo().create({
                            'res_id': checklist_id.projects_id.id,
                            'model': 'project.project',
                            'body': 'Project Checklist created with details: %s' % ('\n'.join(map(str, data_lst)))
                        })

        return True

    def action_print_civil_checklist(self):
        self.ensure_one()
        if self.checklist_type != 'service':
            return self.env.ref('ats_civil_project_checklist.action_report_civil_project_checklist').report_action(self)
