# -*- coding: utf-8 -*-

from odoo import models


class Project(models.Model):
    _inherit = 'project.project'

    def _compute_man_power_details(self):
        """
            Added the super-user because we bypass the access controls.
        """
        man_power_details = 0
        for project in self:
            for line in project.sudo().employee_cost_lines:
                man_power_details += line.subtotal

            project.man_power_details = man_power_details
