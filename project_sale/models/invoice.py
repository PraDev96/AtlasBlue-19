# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    project_id = fields.Many2one('project.project', string="Project")


class Sale(models.Model):
    _inherit = 'sale.order'

    def _project_sale_domain(self):
        return [
            ('pricing_type', '=', 'fixed_rate'),
            ('analytic_account_id', '!=', False),
            ('company_id', '=', self.company_id.id),
            ('partner_id', '=', self.partner_id.id)
        ]

    project_id = fields.Many2one('project.project', string="Project", domain=_project_sale_domain, help='Select a non billable project on which tasks can be created.')


class Purchase(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one('project.project', string='Project')


class Picking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one('project.project', string='Project', index=True, tracking=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True, tracking=True)

    def button_validate(self):
        result = super(Picking, self).button_validate()
        for picking in self:
            MaintenanceEquipment = self.env['atlas.maintenance.equipment']
            if picking.state == 'done':
                for pick in self:
                    for line in pick.move_ids_without_package.filtered(lambda r: r.quantity > 0 and r.product_id.is_equipment):
                        facility = line.project_id.facility_ids and line.project_id.facility_ids[0].id
                        partner_id = line.project_id.partner_id.id
                        temp = line.quantity
                        for i in range(0, int(temp)):
                            MaintenanceEquipment.create({
                                'product_id': line.product_id.id,
                                'name': line.product_id.name,
                                'description': line.name,
                                'status': 'new',
                                'partner_id': partner_id,
                                'project_id': line.project_id.id,
                                'facility_id': facility,
                                'phase': line.product_id.phase,
                                'electrical_load': line.product_id.electrical_load,
                                'quant_done': 1
                            })

        return result


class Expense(models.Model):
    _inherit = 'hr.expense'

    project_id = fields.Many2one('project.project', string="Project", index=True)
