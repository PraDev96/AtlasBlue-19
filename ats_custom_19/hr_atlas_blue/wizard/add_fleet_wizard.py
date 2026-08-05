# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class AddFleetWizard(models.TransientModel):
    _name = 'add.fleet.wizard'
    _description = "Add Fleet Wizard"

    start_date = fields.Date(string="Start Date", required=True, default=fields.Date.context_today)
    fleet_ids = fields.Many2many('fleet.vehicle', string="Fleets", required=True)

    def add_fleet(self):
        self.ensure_one()
        Project = self.env['project.project']
        HistoryProjectFleet = self.env['history.project.fleet']

        project_id = self.env.context.get('active_id')
        already_project_fleet = []
        if project_id:
            proj = Project.browse(project_id)
            for fleet in self.fleet_ids:
                history_fleets = HistoryProjectFleet.search([
                    ('fleet_vehicle_id', '=', fleet.id), ('project_id', '!=', project_id),
                    '|', ('end_date', '>=', self.start_date), ('end_date', '=', False)
                ], limit=1)
                if history_fleets:
                    already_project_fleet.append(fleet.name)
                else:
                    history_fleets = HistoryProjectFleet.search([('fleet_vehicle_id', '=', fleet.id), ('project_id', '=', project_id), ('end_date', '=', False)], limit=1)
                    if not history_fleets:
                        HistoryProjectFleet.create({
                            'project_id': project_id,
                            'fleet_vehicle_id': fleet.id,
                            'start_date': self.start_date,
                        })
                        proj.write({'fleet_ids': [(4, fleet.id)]})
                        fleet.with_context(start_date=self.start_date).write({'state': 'project', 'project_id': proj.id})

        if already_project_fleet:
            fleet_name = ', '.join(already_project_fleet)
            raise ValidationError(_('Fleet %s already working in project. First remove from existing project!') % fleet_name)

        return True
