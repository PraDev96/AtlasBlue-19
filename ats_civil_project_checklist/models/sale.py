# -*- coding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """
            Replaced the method for adding the checklist type
            source: atlas_base/models/project.py ---- line no: 383
        """
        if self.opportunity_id:
            stage = self.env['crm.stage'].search([('code', '=', 'CLOSE')], limit=1)
            if stage:
                self.opportunity_id.stage_id = stage.id

        res = super(SaleOrder, self).action_confirm()
        if self.root_facility_ids or self.project_tmp_id:
            self.facility_ids.write({'partner_id': self.partner_id.id})
            if not self.project_id:
                tmpl_project_ids = False
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
                            # here added checklist_type and is_checklist_task
                            tmpl_project_task.copy({
                                'active': True,
                                'stage_id': stage.id,
                                'project_id': project_id.id,
                                'name': tmpl_project_task.name,
                                'facility_id': root_facility_id.id,
                                'weightage': tmpl_project_task.weightage,
                                'checklist_type': tmpl_project_task.checklist_type,
                                'is_checklist_task': tmpl_project_task.is_checklist_task,
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
