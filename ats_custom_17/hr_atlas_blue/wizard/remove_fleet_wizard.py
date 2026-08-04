# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RemoveFleetWizard(models.TransientModel):
    _name = 'remove.fleet.wizard'
    _description = "Remove Fleet Wizard"

    @api.model
    def _get_default_project(self):
        project_id = False
        if self.env.context.get('active_id'):
            project_id = self.env.context['active_id']

        return project_id

    end_date = fields.Date(string="End Date", required=True, default=fields.Date.context_today)
    fleet_ids = fields.Many2many('fleet.vehicle', string="Fleets", required=True)
    project_id = fields.Many2one('project.project', string="Project", default=_get_default_project)

    def remove_fleet(self):
        self.ensure_one()
        Project = self.env['project.project']
        HistoryProjectfleet = self.env['history.project.fleet']

        project_id = self.env.context.get('active_id')
        if project_id:
            proj = Project.browse(project_id)
            for fleet in self.fleet_ids:
                history_fleet = HistoryProjectfleet.search(
                    [('fleet_vehicle_id', '=', fleet.id), ('project_id', '=', project_id), ('end_date', '=', False)], order='id desc', limit=1
                )
                history_fleet.write({
                    'end_date': self.end_date,
                })
                proj.write({'fleet_ids': [(3, fleet.id)]})
                fleet.write({'state': 'parking', 'project_id': False})

        return True
