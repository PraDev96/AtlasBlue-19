# -*- coding: utf-8 -*-

import zipfile
from io import BytesIO
from odoo import _, models, fields, api


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    project_name = fields.Char(string="Project Name", compute="_compute_project_details", readonly=True, store=True)
    project_task_state = fields.Char(string="Task State", compute="_compute_project_details", readonly=True, store=True)

    @api.depends('res_model', 'res_id')
    def _compute_project_details(self):
        for rec in self:
            if rec.res_model == 'project.project' and rec.res_id:
                project = self.env['project.project'].sudo().browse(rec.res_id)
                rec.project_name = project.display_name if project else ''
                rec.project_task_state = project.state_id.display_name if project and project.state_id else ''

            if rec.res_model == 'project.task' and rec.res_id:
                task = self.env['project.task'].sudo().browse(rec.res_id)
                rec.project_name = task.project_id.display_name if task and task.project_id else ''
                rec.project_task_state = task.project_id.state_id.display_name if task.project_id and task.project_id.state_id else ''

            if rec.res_model == 'project.checklist' and rec.res_id:
                checklist = self.env['project.checklist'].sudo().browse(rec.res_id)
                rec.project_name = checklist.projects_id.display_name if checklist and checklist.projects_id else ''
                rec.project_task_state = checklist.projects_id.state_id.display_name if checklist and checklist.projects_id and checklist.projects_id.state_id else ''

    def _create_temp_zip(self):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            # Group attachments by related record
            grouped = {}
            for attachment in self:
                key = (attachment.res_model, attachment.res_id)
                grouped.setdefault(key, []).append(attachment)

            for (model, res_id), attachments in grouped.items():
                folder_name = "Unlinked_Attachments"

                # Try to get record display name if linked
                if model and res_id:
                    record = self.env[model].sudo().browse(res_id)
                    if record.exists():
                        folder_name = record.display_name + '_id#' + str(record.id) or f"{model}_{res_id}"
                    else:
                        folder_name = f"{model}_{res_id}"

                # Sanitize folder name
                folder_name = folder_name.replace("/", "_").replace("\\", "_")

                # Add files under the folder
                for attachment in attachments:
                    attachment.check("read")
                    zip_path = f"{folder_name}/{attachment._compute_zip_file_name()}"
                    zip_file.writestr(zip_path, attachment.raw or b"")

            zip_file.close()
            zip_buffer.seek(0)
        return zip_buffer
