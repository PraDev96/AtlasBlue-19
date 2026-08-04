/** @odoo-module **/

import { Component } from "@odoo/owl";
import { session } from "@web/session";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import publicWidget from '@web/legacy/js/public/public_widget';


publicWidget.registry.HrProjectTimesheetExtended = publicWidget.Widget.extend({
    selector: '.o_project_portal_sidebar #task_content',
    events: {
        "click .end_btn_custom": "_end_timesheet",
        "click .start_btn_custom": "_create_timesheet",
        "click .submit_signature_btn_custom": "_submit_timesheet",
        "click .submit_checklist_btn_custom": "_submit_checklist",
        "click .submit_signature_btn_custom_signature": "_submit_timesheet_signature",
    },

    init: function (parent, options) {
        var def = this._super.apply(this, arguments);
        this.analytic_line_id = false;
        this.employee_cost_line_id = false;
        this.analytic_line_id = $('#exist_rec').val()
        $('.end_btn_custom_hide').css('display', 'none');
        this.employee_cost_line_id = $('#exist_cost_rec').val()
        return def;
    },

    start: function () {
        this.orm = this.bindService("orm");
        var def = this._super.apply(this, arguments);
        return def;
    },

    _create_timesheet: async function(event) {
        var self = this;
        var $target = $(event.target);
        var analytic_line_id = self.analytic_line_id;
        let timesheet;
        timesheet = await this.orm.call(
            "account.analytic.line",
            "create_from_portal",
            [{task_id: $target.data("task_id"), analytic_line_id: analytic_line_id}],
        );
        if (timesheet.error) {
            this.notification.add(_t("Something went Wrong!!!"), {
                type: "danger",
            });
            console.error("Error:", timesheet.error);
        } else {
            $('.start_btn_custom').css('display', 'none');
            $('.start_time_show').css('display', 'block');
            $('.start_time_show').text(timesheet.start_date);
            $('.input_atlas_checklist').removeClass('d-none');
            $('.end_btn_custom_hide').css('display', 'block');
            self.analytic_line_id = timesheet.analytic_line_rec;
            if ($('.description_custom').length) {
                var description = $('.description_custom').val();
            }
        }
    },

    _end_timesheet: async function(event) {
        var self = this;
        var $target = $(event.target);
        var analytic_line_id = self.analytic_line_id;
        if (!analytic_line_id) {
            var analytic_line_id = $target.data("timesheet_id");
        }

        let timesheet;
        timesheet = await this.orm.call(
            "account.analytic.line",
            "update_from_portal",
            [{analytic_line_id: analytic_line_id}],
        );
        if (timesheet.error) {
            this.notification.add(_t("Something went Wrong!!!"), {
                type: "danger",
            });
            console.error("Error:", timesheet.error);
        } else {
            $('.end_time_show').css('display', 'block');
            $('.end_time_show').text(timesheet.end_date);
            $('.end_btn_custom_hide').css('display', 'none');
            $('.end_btn_custom_hide_1').css('display', 'none');
            $('.duration_time_show').val(timesheet.unit_amount);
            self.analytic_line_id = timesheet.analytic_line_rec;
            $('.duration_time_show').attr('disabled', 'disabled');
            if (event.target.dataset.task_type != 'Service') {
                $('.submit_signature_btn_custom').removeClass('d-none');
            }else {
                $('.submit_signature_btn_custom_signature').removeClass('d-none');
            }
        }
    },

    _submit_timesheet: async function(event) {
        var self = this;
        var $target = $(event.target);
        var analytic_line_id = self.analytic_line_id;
        var description = $('.description_custom').val() || '';
        let timesheet;
        timesheet = await this.orm.call(
            "account.analytic.line",
            "submit_from_portal",
            [{analytic_line_id: analytic_line_id, description: description}],
        );
        if (timesheet.error) {
            this.notification.add(_t("Something went Wrong!!!"), {
                type: "danger",
            });
            console.error("Error:", response.error);
        } else {
            swal({
                text: "Timesheet Added successfully",
                icon: "success",
            }).then((willDelete) => {
                $('#exist_rec').val('');
                self.analytic_line_id = false;
                $('.start_btn_custom').show();
                $('.description_custom').val('');
                $('.end_btn_custom_hide').hide();
                $('.end_btn_custom_hide_1').hide();
                $('.end_time_show').text('').css('display', 'none');
                $('.submit_signature_btn_custom').addClass('d-none');
                $('.start_time_show').text('').css('display', 'none');
                $('.duration_time_show').val('').attr('disabled', 'disabled');
                $('.submit_signature_btn_custom_signature').addClass('d-none');
                // location.reload();
            });
        }
    },

    _submit_checklist: async function(event) {
        var self = this;
        var $target = $(event.target);
        var analytic_line_id = self.analytic_line_id;
        var signature_img = this.$('.o_web_sign_signature').jSignature('getData', 'image');
        let project_checklist;
        project_checklist = await this.orm.call(
            "project.checklist",
            "create_from_checklist",
            [{
                tds: $(".tds").val(),
                user_id: session.user_id,
                salinity: $(".salinity").val(),
                ph_level: $(".ph_level").val(),
                task_id: $target.data("task_id"),
                timesheet_id: self.analytic_line_id,
                cyanuric_Acid: $(".cyanuric_Acid").val(),
                skim_pool: $(".skim_pool").is(":checked"),
                total_chlorine: $(".total_chlorine").val(),
                brush_pool: $(".brush_pool").is(":checked"),
                vacuum_pool: $(".vacuum_pool").is(":checked"),
                calcium_hardness: $(".calcium_hardness").val(),
                total_alkalinity: $(".total_alkalinity").val(),
                water_temperature: $(".water_temperature").val(),
                description: $('.description_custom').val() || '',
                free_chlorin_level: $(".free_chlorin_level").val(),
                clean_desk_area: $(".clean_desk_area").is(":checked"),
                signature_name: this.$('.o_web_sign_name_input').val(),
                signature_img: signature_img && signature_img[1] || '',
                clean_balance_tank:$(".clean_balance_tank").is(":checked"),
                back_wash_filter_after: $(".back_wash_filter_after").val(),
                clean_machine_room: $(".clean_machine_room").is(":checked"),
                back_wash_filter_before: $(".back_wash_filter_before").val(),
                clean_pump_strainer: $(".clean_pump_strainer").is(":checked"),
                clean_skimmer_overflow: $(".clean_skimmer_overflow").is(":checked"),
            }],
        );
        if (project_checklist.error) {
            this.notification.add(_t("Something went Wrong!!!"), {
                type: "danger",
            });
            console.error("Error:", project_checklist.error);
        } else {
            swal({
                text: "Check-List Added successfully",
                icon: "success",
            }).then((willDelete) => {
                $('#exist_rec').val('');
                self.analytic_line_id = false;
                $('.start_btn_custom').show();
                $('.end_btn_custom_hide').hide();
                $('.description_custom').val('');
                $('.end_btn_custom_hide_1').hide();
                this.$('.o_web_sign_name_input').val('');
                $('.input_atlas_checklist').addClass('d-none');
                this.$('.o_web_sign_signature').jSignature('reset');
                $('.end_time_show').text('').css('display', 'none');
                $('.submit_signature_btn_custom').addClass('d-none');
                $('.start_time_show').text('').css('display', 'none');
                $('.duration_time_show').val('').attr('disabled', 'disabled');
                $('.submit_signature_btn_custom_signature').addClass('d-none');
                // Clear checklist fields
                $(".vacuum_pool, .clean_skimmer_overflow, .brush_pool, .skim_pool, .clean_desk_area, .clean_pump_strainer, .clean_machine_room, .clean_balance_tank").prop('checked', false);
                $(".back_wash_filter_before, .back_wash_filter_after, .water_temperature, .total_alkalinity, .calcium_hardness, .free_chlorin_level, .ph_level, .cyanuric_Acid, .total_chlorine, .salinity, .tds").val('');
                // location.reload();
            });
        }
    },

    _submit_timesheet_signature: async function(event) {
        var self = this;
        var $target = $(event.target);
        var analytic_line_id = self.analytic_line_id;
        var description = $('.description_custom').val() || '';
        let timesheet;
        timesheet = await this.orm.call(
            "account.analytic.line",
            "submit_from_portal",
            [{analytic_line_id: analytic_line_id, description: description}],
        );
        if (timesheet.error) {
            this.notification.add(_t("Something went Wrong!!!"), {
                type: "danger",
            });
            console.error("Error:", timesheet.error);
        }
        return timesheet
    },

});
