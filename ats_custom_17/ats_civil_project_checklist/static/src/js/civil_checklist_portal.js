/** @odoo-module **/

import { session } from "@web/session";
import publicWidget from '@web/legacy/js/public/public_widget';


publicWidget.registry.HrProjectTimesheetExtended.include({
    events: Object.assign({}, publicWidget.registry.HrProjectTimesheetExtended.prototype.events, {
        "click .submit_checklist_btn_custom_no_signature": "_submit_checklist_no_signature",
        "click .submit_checklist_btn_custom": "_submit_checklist",
    }),

    _create_timesheet: async function(event) {
        await this._super.apply(this, arguments);
        // Explicitly re-show checklist details for Service tasks upon Sign-in
        this.$('.input_atlas_checklist').removeClass('d-none');
    },

    _end_timesheet: async function(event) {
        await this._super.apply(this, arguments);
        var $target = $(event.currentTarget);
        var isService = $target.attr('data-task_type') === 'Service';
        if ($target.attr('data-is_checklist_task')) {
            if (isService) {
                // Ensure Signature button is shown for Service checklist tasks
                this.$('.submit_signature_btn_custom').addClass('d-none');
                this.$('.submit_signature_btn_custom_signature').removeClass('d-none');
                this.$('.submit_checklist_btn_custom_no_signature').addClass('d-none');
            } else {
                // Show direct Submit for other checklist tasks
                this.$('.submit_signature_btn_custom_signature').addClass('d-none');
                this.$('.submit_checklist_btn_custom_no_signature').removeClass('d-none');
            }
        }
    },

    _submit_checklist_no_signature: async function(event) {
        event.preventDefault();
        event.stopPropagation();
        let timesheet = await this._submit_timesheet_signature(event);
        if (timesheet && !timesheet.error) {
            await this._submit_checklist(event);
        }
    },

    _submit_checklist: async function(event) {
        event.preventDefault();
        event.stopPropagation();
        var self = this;
        var $target = $(event.currentTarget);
        var isService = $target.attr('data-task_type') === 'Service';

        // Validation for Numeric fields
        var hasError = false;
        this.$('.checklist_number_field').removeClass('is-invalid');
        this.$('.checklist_error_msg').remove();

        this.$('.checklist_number_field:visible').each(function() {
            var $field = $(this);
            var value = $field.val();
            var isInvalid = false;

            if (this.type === 'number') {
                if (this.validity.badInput || (value && parseFloat(value) < 0)) {
                    isInvalid = true;
                }
            } else {
                // For Text fields that should be numeric
                if (value && (isNaN(value) || parseFloat(value) < 0)) {
                    isInvalid = true;
                }
            }

            if (isInvalid) {
                hasError = true;
                $field.addClass('is-invalid');
                $field.after('<div class="checklist_error_msg text-danger" style="font-size: 12px;">Enter valid data</div>');
            }
        });

        if (hasError) {
            var $firstInvalid = this.$('.is-invalid:visible:first');
            if ($firstInvalid.length) {
                $firstInvalid[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                $firstInvalid.focus();
            }
            return false;
        }

        var signature_img = this.$('.o_web_sign_signature').jSignature('getData', 'image');

        // Prevent multiple submissions after validation
        this.$('.submit_checklist_btn_custom').addClass('d-none');
        this.$('.submit_checklist_btn_custom_no_signature').addClass('d-none');

        let args = {
            user_id: session.user_id,
            task_id: $target.data("task_id"),
            timesheet_id: self.analytic_line_id,
            description: $('.description_custom').val() || '',
            signature_img: signature_img && signature_img[1] || '',
            signature_name: this.$('.o_web_sign_name_input').val(),

            // Service fields
            tds: $(".tds").val(),
            salinity: $(".salinity").val(),
            ph_level: $(".ph_level").val(),
            cyanuric_Acid: $(".cyanuric_Acid").val(),
            skim_pool: $(".skim_pool").is(":checked"),
            total_chlorine: $(".total_chlorine").val(),
            brush_pool: $(".brush_pool").is(":checked"),
            vacuum_pool: $(".vacuum_pool").is(":checked"),
            calcium_hardness: $(".calcium_hardness").val(),
            total_alkalinity: $(".total_alkalinity").val(),
            water_temperature: $(".water_temperature").val(),
            free_chlorin_level: $(".free_chlorin_level").val(),
            clean_desk_area: $(".clean_desk_area").is(":checked"),
            clean_balance_tank:$(".clean_balance_tank").is(":checked"),
            back_wash_filter_after: $(".back_wash_filter_after").val(),
            clean_machine_room: $(".clean_machine_room").is(":checked"),
            back_wash_filter_before: $(".back_wash_filter_before").val(),
            clean_pump_strainer: $(".clean_pump_strainer").is(":checked"),
            clean_skimmer_overflow: $(".clean_skimmer_overflow").is(":checked"),
            // Service fields END

            // Concrete
            curing_with_water: $(".curing_with_water").is(":checked"),
            form_work_for_walls: $(".form_work_for_walls").is(":checked"),
            external_waterproofing: $(".external_waterproofing").is(":checked"),
            excavation_and_compaction: $(".excavation_and_compaction").is(":checked"),
            remove_framework_and_clean: $(".remove_framework_and_clean").is(":checked"),
            casting_clearance_concrete: $(".casting_clearance_concrete").is(":checked"),
            cement_block_for_pool_layout: $(".cement_block_for_pool_layout").is(":checked"),
            steel_reinforcement_for_floor: $(".steel_reinforcement_for_floor").is(":checked"),
            steel_reinforcement_for_walls: $(".steel_reinforcement_for_walls").is(":checked"),
            visit_site_and_finish_floor_level: $(".visit_site_and_finish_floor_level").is(":checked"),
            casting_reinforcement_concrete_floor: $(".casting_reinforcement_concrete_floor").is(":checked"),
            casting_reinforcement_concrete_walls: $(".casting_reinforcement_concrete_walls").is(":checked"),
            // Concrete END

            // Embedded Piping
            emp_jets: $(".emp_jets").val(),
            emp_skimmer: $(".emp_skimmer").val(),
            emp_sump_pit: $(".emp_sump_pit").val(),
            emp_spa_size: $(".emp_spa_size").val(),
            emp_pool_size: $(".emp_pool_size").val(),
            emp_main_drain: $(".emp_main_drain").val(),
            emp_big_lights: $(".emp_big_lights").val(),
            emp_drain_pipes: $(".emp_drain_pipes").val(),
            emp_small_lights: $(".emp_small_lights").val(),
            emp_floor_inlets: $(".emp_floor_inlets").val(),
            emp_vacuum_point: $(".emp_vacuum_point").val(),
            emp_tank_suction: $(".emp_tank_suction").val(),
            emp_touch_switch: $(".emp_touch_switch").val(),
            emp_wall_suction: $(".emp_wall_suction").val(),
            emp_filling_lines: $(".emp_filling_lines").val(),
            emp_water_descent: $(".emp_water_descent").val(),
            emp_air_regulator: $(".emp_air_regulator").val(),
            emp_control_switch: $(".emp_control_switch").val(),
            emp_electrical_supply: $(".emp_electrical_supply").val(),
            emp_ventilation_pipes: $(".emp_ventilation_pipes").val(),
            emp_overflow_with_drain: $(".emp_overflow_with_drain").val(),
            emp_informed_to_client: $(".emp_informed_to_client").is(":checked"),
            emp_location_of_junction_box: $(".emp_location_of_junction_box").val(),
            emp_location_of_control_switch: $(".emp_location_of_control_switch").val(),
            emp_final_pressure_test_reading: $(".emp_final_pressure_test_reading").val(),
            emp_initial_pressure_test_reading: $(".emp_initial_pressure_test_reading").val(),
            emp_pool_dimension_as_per_drawing: $(".emp_pool_dimension_as_per_drawing").is(":checked"),
            // Embedded Piping END

            // Work Before Waterproofing
            wbw_jets: $(".wbw_jets").val(),
            wbw_skimmer: $(".wbw_skimmer").val(),
            wbw_spa_size: $(".wbw_spa_size").val(),
            wbw_sump_pit: $(".wbw_sump_pit").val(),
            wbw_pool_size: $(".wbw_pool_size").val(),
            wbw_main_drain: $(".wbw_main_drain").val(),
            wbw_big_lights: $(".wbw_big_lights").val(),
            wbw_drain_pipes: $(".wbw_drain_pipes").val(),
            wbw_small_lights: $(".wbw_small_lights").val(),
            wbw_floor_inlets: $(".wbw_floor_inlets").val(),
            wbw_vacuum_point: $(".wbw_vacuum_point").val(),
            wbw_tank_suction: $(".wbw_tank_suction").val(),
            wbw_wall_suction: $(".wbw_wall_suction").val(),
            wbw_touch_switch: $(".wbw_touch_switch").val(),
            wbw_backwash: $(".wbw_backwash").is(":checked"),
            wbw_filling_lines: $(".wbw_filling_lines").val(),
            wbw_air_regulator: $(".wbw_air_regulator").val(),
            wbw_water_descent: $(".wbw_water_descent").val(),
            wbw_control_switch: $(".wbw_control_switch").val(),
            wbw_summit_pit: $(".wbw_summit_pit").is(":checked"),
            wbw_ventilation: $(".wbw_ventilation").is(":checked"),
            wbw_filling_line: $(".wbw_filling_line").is(":checked"),
            wbw_ventilation_pipes: $(".wbw_ventilation_pipes").val(),
            wbw_electrical_supply: $(".wbw_electrical_supply").val(),
            wbw_overflow_with_drain: $(".wbw_overflow_with_drain").val(),
            wbw_informed_to_client: $(".wbw_informed_to_client").is(":checked"),
            wbw_location_of_junction_box: $(".wbw_location_of_junction_box").val(),
            wbw_is_electrical_supply: $(".wbw_is_electrical_supply").is(":checked"),
            wbw_location_of_control_switch: $(".wbw_location_of_control_switch").val(),
            wbw_final_pressure_test_reading: $(".wbw_final_pressure_test_reading").val(),
            wbw_initial_pressure_test_reading: $(".wbw_initial_pressure_test_reading").val(),
            wbw_pool_dimension_as_per_drawing: $(".wbw_pool_dimension_as_per_drawing").is(":checked"),
            // Work Before Waterproofing END

            // Waterproofing
            first_reading: $(".first_reading").is(":checked"),
            water_filling: $(".water_filling").is(":checked"),
            final_reading: $(".final_reading").is(":checked"),
            second_reading: $(".second_reading").is(":checked"),
            site_preparation: $(".site_preparation").is(":checked"),
            first_layer_waterproofing: $(".first_layer_waterproofing").is(":checked"),
            second_layer_waterproofing: $(".second_layer_waterproofing").is(":checked"),
            waterproofing_test_approval: $(".waterproofing_test_approval").is(":checked"),
            wp_visit_site_and_finish_floor_level: $(".wp_visit_site_and_finish_floor_level").is(":checked"),
            // Waterproofing END

            // Acrylic
            proper_drainage: $(".proper_drainage").is(":checked"),
            surface_condition: $(".surface_condition").is(":checked"),
            adhesion_to_substrate: $(".adhesion_to_substrate").is(":checked"),
            structural_support_stable: $(".structural_support_stable").is(":checked"),
            acrylic_join_sealant_intact: $(".acrylic_join_sealant_intact").is(":checked"),
            no_surface_stain_or_build_up: $(".no_surface_stain_or_build_up").is(":checked"),
            any_repair_done_in_the_past_year: $(".any_repair_done_in_the_past_year").is(":checked"),
            no_sign_of_water_leakage_or_moisture: $(".no_sign_of_water_leakage_or_moisture").is(":checked"),
            cleaning_and_maintenance_instruction: $(".cleaning_and_maintenance_instruction").is(":checked"),
            // Acrylic END

            // Tiling
            grouting: $(".grouting").is(":checked"),
            pool_testing: $(".pool_testing").is(":checked"),
            tiles_laying: $(".tiles_laying").is(":checked"),
            tl_visit_site: $(".tl_visit_site").is(":checked"),
            closing_pipes: $(".closing_pipes").is(":checked"),
            tiles_approval: $(".tiles_approval").is(":checked"),
            tiles_delivery: $(".tiles_delivery").is(":checked"),
            overflow_level: $(".overflow_level").is(":checked"),
            tl_waterproofing: $(".tl_waterproofing").is(":checked"),
            splashing_curing: $(".splashing_curing").is(":checked"),
            plastering_curing: $(".plastering_curing").is(":checked"),
            finish_floor_level: $(".finish_floor_level").is(":checked"),
            actual_area_of_tiling: $(".actual_area_of_tiling").is(":checked"),
            tiling_area_as_per_contract: $(".tiling_area_as_per_contract").is(":checked"),
            // Tiling END

            // EQSI
            eq_pump: $(".eq_pump").val(),
            eq_ozone: $(".eq_ozone").val(),
            eq_filter: $(".eq_filter").val(),
            eq_ladder: $(".eq_ladder").val(),
            eq_heater: $(".eq_heater").val(),
            eq_gutter: $(".eq_gutter").val(),
            eq_jacuzzi: $(".eq_jacuzzi").val(),
            eq_skimmer: $(".eq_skimmer").val(),
            eq_deck_box: $(".eq_deck_box").val(),
            eq_sump_pump: $(".eq_sump_pump").val(),
            eq_water_fall: $(".eq_water_fall").val(),
            eq_transformer: $(".eq_transformer").val(),
            eq_chlorinator: $(".eq_chlorinator").val(),
            eq_float_valve: $(".eq_float_valve").val(),
            eq_control_panel: $(".eq_control_panel").val(),
            eq_electric_work: $(".eq_electric_work").val(),
            eq_control_switch: $(".eq_control_switch").val(),
            eq_fountain_nozzle: $(".eq_fountain_nozzle").val(),
            eq_lights_rcb_remote: $(".eq_lights_rcb_remote").val(),
            eq_lights_cold_white: $(".eq_lights_cold_white").val(),
            eq_lights_warm_white: $(".eq_lights_warm_white").val(),
            eq_cleaning_equipment: $(".eq_cleaning_equipment").val(),
            eq_rain_water_fountain: $(".eq_rain_water_fountain").val(),
            // EQSI END

            // Commissioning
            com_pump: $(".com_pump").val(),
            com_ozone: $(".com_ozone").val(),
            com_ladder: $(".com_ladder").val(),
            com_filter: $(".com_filter").val(),
            com_heater: $(".com_heater").val(),
            com_gutter: $(".com_gutter").val(),
            com_jacuzzi: $(".com_jacuzzi").val(),
            com_skimmer: $(".com_skimmer").val(),
            com_deck_box: $(".com_deck_box").val(),
            com_sump_pump: $(".com_sump_pump").val(),
            com_water_fall: $(".com_water_fall").val(),
            com_transformer: $(".com_transformer").val(),
            com_chlorinator: $(".com_chlorinator").val(),
            com_float_valve: $(".com_float_valve").val(),
            com_control_panel: $(".com_control_panel").val(),
            com_electric_work: $(".com_electric_work").val(),
            com_control_switch: $(".com_control_switch").val(),
            com_fountain_nozzle: $(".com_fountain_nozzle").val(),
            com_lights_rcb_remote: $(".com_lights_rcb_remote").val(),
            com_lights_cold_white: $(".com_lights_cold_white").val(),
            com_lights_warm_white: $(".com_lights_warm_white").val(),
            com_cleaning_equipment: $(".com_cleaning_equipment").val(),
            com_rain_water_fountain: $(".com_rain_water_fountain").val(),
            // Commissioning END

            // Remarks as Common for Civil/Mechanical Project Checklists
            remarks: $(".remarks").val(),
        };

        try {
            let project_checklist = await this.orm.call(
                "project.checklist",
                "create_from_checklist",
                [args],
            );
            if (project_checklist) {
                swal({
                    text: "Check-List Added successfully",
                    icon: "success",
                }).then((willDelete) => {
                    // Close signature modal if open
                    $('#modalaccept').modal('hide');
                    self._reset_portal_form();
                    // If service, hide and keep for next entry; otherwise remove to prevent multiple entries
                    if (isService) {
                        self.$('.input_atlas_checklist').addClass('d-none');
                    } else {
                        self.$('.input_atlas_checklist').remove();
                    }
                });
                return project_checklist;
            } else {
                // Re-show buttons if submission failed (returned false)
                this.$('.submit_checklist_btn_custom').removeClass('d-none');
                this.$('.submit_checklist_btn_custom_no_signature').removeClass('d-none');
            }
        } catch (error) {
            // Re-show buttons on RPC error
            this.$('.submit_checklist_btn_custom').removeClass('d-none');
            this.$('.submit_checklist_btn_custom_no_signature').removeClass('d-none');
            throw error;
        }
    },

    _reset_portal_form: function() {
        this._super.apply(this, arguments);
        $('.submit_checklist_btn_custom').removeClass('d-none');
        $('.submit_checklist_btn_custom_no_signature').addClass('d-none');

        // Clear Service Fields
        this.$(".vacuum_pool, .clean_skimmer_overflow, .brush_pool, .skim_pool, .clean_desk_area, .clean_pump_strainer, .clean_machine_room, .clean_balance_tank").prop('checked', false);
        this.$(".back_wash_filter_before, .back_wash_filter_after, .water_temperature, .total_alkalinity, .calcium_hardness, .free_chlorin_level, .ph_level, .cyanuric_Acid, .total_chlorine, .salinity, .tds").val('');

        // Clear Concrete Fields
        $(".visit_site_and_finish_floor_level, .excavation_and_compaction, .cement_block_for_pool_layout, .casting_clearance_concrete, .external_waterproofing, .steel_reinforcement_for_floor, .steel_reinforcement_for_walls, .casting_reinforcement_concrete_floor, .form_work_for_walls, .casting_reinforcement_concrete_walls, .remove_framework_and_clean, .curing_with_water").prop('checked', false);

        // Clear Embedded Piping Fields
        $(".emp_floor_inlets, .emp_vacuum_point, .emp_main_drain, .emp_tank_suction, .emp_wall_suction, .emp_filling_lines, .emp_electrical_supply, .emp_skimmer, .emp_big_lights, .emp_small_lights, .emp_jets, .emp_sump_pit, .emp_drain_pipes, .emp_location_of_junction_box, .emp_air_regulator, .emp_touch_switch, .emp_control_switch, .emp_water_descent, .emp_overflow_with_drain, .emp_ventilation_pipes, .emp_location_of_control_switch, .emp_initial_pressure_test_reading, .emp_final_pressure_test_reading, .emp_pool_size, .emp_spa_size").val('');
        $(".emp_pool_dimension_as_per_drawing, .emp_informed_to_client").prop('checked', false);

        // Clear Work Before Waterproofing Fields
        $(".wbw_floor_inlets, .wbw_vacuum_point, .wbw_main_drain, .wbw_tank_suction, .wbw_wall_suction, .wbw_filling_lines, .wbw_electrical_supply, .wbw_skimmer, .wbw_big_lights, .wbw_small_lights, .wbw_jets, .wbw_sump_pit, .wbw_drain_pipes, .wbw_location_of_junction_box, .wbw_air_regulator, .wbw_touch_switch, .wbw_control_switch, .wbw_water_descent, .wbw_overflow_with_drain, .wbw_ventilation_pipes, .wbw_location_of_control_switch, .wbw_initial_pressure_test_reading, .wbw_final_pressure_test_reading, .wbw_pool_size, .wbw_spa_size").val('');
        $(".wbw_pool_dimension_as_per_drawing, .wbw_informed_to_client, .wbw_backwash, .wbw_ventilation, .wbw_filling_line, .wbw_is_electrical_supply, .wbw_summit_pit").prop('checked', false);

        // Clear Waterproofing Fields
        $(".wp_visit_site_and_finish_floor_level, .site_preparation, .first_layer_waterproofing, .second_layer_waterproofing, .water_filling, .first_reading, .second_reading, .final_reading, .waterproofing_test_approval").prop('checked', false);

        // Clear Acrylic Fields
        $(".surface_condition, .acrylic_join_sealant_intact, .adhesion_to_substrate, .no_sign_of_water_leakage_or_moisture, .no_surface_stain_or_build_up, .structural_support_stable, .proper_drainage, .cleaning_and_maintenance_instruction, .any_repair_done_in_the_past_year").prop('checked', false);

        // Clear Tiling Fields
        $(".tl_visit_site, .finish_floor_level, .closing_pipes, .tl_waterproofing, .pool_testing, .tiles_approval, .tiles_delivery, .splashing_curing, .plastering_curing, .tiles_laying, .grouting, .overflow_level, .tiling_area_as_per_contract, .actual_area_of_tiling").prop('checked', false);

        // Clear EQSI Fields
        $(".eq_filter, .eq_pump, .eq_heater, .eq_jacuzzi, .eq_transformer, .eq_ozone, .eq_ladder, .eq_sump_pump, .eq_chlorinator, .eq_skimmer, .eq_control_switch, .eq_float_valve, .eq_gutter, .eq_control_panel, .eq_electric_work, .eq_lights_rcb_remote, .eq_fountain_nozzle, .eq_deck_box, .eq_lights_cold_white, .eq_water_fall, .eq_lights_warm_white, .eq_rain_water_fountain, .eq_cleaning_equipment").val('');

        // Clear Commissioning Fields
        $(".com_filter, .com_pump, .com_heater, .com_jacuzzi, .com_transformer, .com_ozone, .com_ladder, .com_sump_pump, .com_chlorinator, .com_skimmer, .com_control_switch, .com_float_valve, .com_gutter, .com_control_panel, .com_electric_work, .com_lights_rcb_remote, .com_fountain_nozzle, .com_deck_box, .com_lights_cold_white, .com_water_fall, .com_lights_warm_white, .com_rain_water_fountain, .com_cleaning_equipment").val('');

        // Clear Civil/Mechanical Remarks field
        $(".remarks").val('');
    },

});
