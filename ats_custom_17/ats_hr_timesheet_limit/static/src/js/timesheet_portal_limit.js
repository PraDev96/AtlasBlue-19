/** @odoo-module **/

import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";
import publicWidget from '@web/legacy/js/public/public_widget';


patch(publicWidget.registry.HrProjectTimesheetExtended.prototype, {
    _create_timesheet: async function(event) {
        var self = this;
        var $target = $(event.target);
        var analytic_line_id = self.analytic_line_id;

        // Check if limit already reached before starting
        const result = await this.orm.call(
            "account.analytic.line",
            "check_limit_exceeded",
            [{}],
        );

        if (result.already_reached) {
            swal({
                title: _t("Daily Limit Reached"),
                text: sprintf(_t("You have already Reached the Daily Limit of %s for %s. You cannot add more Timesheet Entries for this Date."), result.limit, result.date),
                icon: "error",
            });
            return;
        }

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
            $('.start_btn_custom').hide();
            $('.end_btn_custom_hide').show();
            $('.input_atlas_checklist').removeClass('d-none');
            self.analytic_line_id = timesheet.analytic_line_rec;
            $('.start_time_show').text(timesheet.start_date).show();
        }
    },

    _end_timesheet: async function(event) {
        var self = this;
        var $target = $(event.target);
        var analytic_line_id = self.analytic_line_id;
        if (!analytic_line_id) {
            var analytic_line_id = $target.data("timesheet_id");
        }

        // Check if limit exceeded before updating
        const result = await this.orm.call(
            "account.analytic.line",
            "check_limit_exceeded",
            [{analytic_line_id: analytic_line_id}],
        );

        let confirm_limit = false;
        if (result.exceeded) {
            const willContinue = await new Promise((resolve) => {
                swal({
                    title: _t("Daily Limit Exceeded"),
                    text: sprintf(_t("You have already Logged %s for %s. This Entry adds %s, which Exceeds the Daily Limit of %s. You can only add %s more for this Date. Extra Worked Hours: %s. Do you want to continue with the Remaining %s?"),
                        result.existing, result.date, result.worked_hours, result.limit, result.remaining, result.overtime_unit_amount, result.remaining),
                    icon: "warning",
                    buttons: {
                        cancel: _t("Cancel"),
                        confirm: _t("Continue with Remaining Time"),
                    },
                    dangerMode: true,
                }).then((val) => {
                    resolve(val);
                });
            });

            if (!willContinue) {
                location.reload();
                return;
            }
            confirm_limit = true;
        }

        let timesheet;
        timesheet = await this.orm.call(
            "account.analytic.line",
            "update_from_portal",
            [{analytic_line_id: analytic_line_id, confirm_limit: confirm_limit}],
        );

        if (timesheet.error) {
            this.notification.add(_t("Something went Wrong!!!"), {
                type: "danger",
            });
            console.error("Error:", timesheet.error);
        } else {
            $('.end_btn_custom_hide').hide();
            $('.end_btn_custom_hide_1').hide();
            $('.end_time_show').text(timesheet.end_date).show();
            $('.duration_time_show').val(timesheet.unit_amount).attr('disabled', 'disabled');
            if (timesheet.overtime_unit_amount) {
                const extraMinutes = Math.round(Math.abs(timesheet.overtime_unit_amount) * 60);
                const extraHHmm = `${Math.floor(extraMinutes / 60).toString().padStart(2, '0')}:${(extraMinutes % 60).toString().padStart(2, '0')}`;
                $('.overtime_unit_amount_show').val(extraHHmm);
                $('.overtime_unit_amount_container').removeClass('d-none');
            }
            self.analytic_line_id = timesheet.analytic_line_rec;
            if (event.target.dataset.task_type != 'Service') {
                $('.submit_signature_btn_custom').removeClass('d-none');
            } else {
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
            console.error("Error:", timesheet.error);
        } else {
            swal({
                text: "Timesheet Added successfully",
                icon: "success",
            }).then((willDelete) => {
                this._reset_portal_form();
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
                signature_img: signature_img && signature_img[1] || '',
                signature_name: this.$('.o_web_sign_name_input').val(),
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
                this._reset_portal_form();
            });
        }
    },

    _reset_portal_form: function() {
        $('#exist_rec').val('');
        this.analytic_line_id = false;
        $('.start_btn_custom').show();
        $('.end_btn_custom_hide').hide();
        $('.description_custom').val('');
        $('.end_btn_custom_hide_1').hide();
        $('.end_time_show').text('').hide();
        $('.start_time_show').text('').hide();
        this.$('.o_web_sign_name_input').val('');
        $('.input_atlas_checklist').addClass('d-none');
        var $signature = this.$('.o_web_sign_signature');
        $('.submit_signature_btn_custom').addClass('d-none');
        $('.overtime_unit_amount_container').addClass('d-none');
        $('.duration_time_show').val('').attr('disabled', 'disabled');
        $('.submit_signature_btn_custom_signature').addClass('d-none');
        $('.overtime_unit_amount_show').val('').attr('disabled', 'disabled');
        // Clear checklist fields
        $(".vacuum_pool, .clean_skimmer_overflow, .brush_pool, .skim_pool, .clean_desk_area, .clean_pump_strainer, .clean_machine_room, .clean_balance_tank").prop('checked', false);
        $(".back_wash_filter_before, .back_wash_filter_after, .water_temperature, .total_alkalinity, .calcium_hardness, .free_chlorin_level, .ph_level, .cyanuric_Acid, .total_chlorine, .salinity, .tds").val('');
        if ($signature.length && $signature.data('jSignature')) {
            $signature.jSignature('reset');
        }
    }

});
