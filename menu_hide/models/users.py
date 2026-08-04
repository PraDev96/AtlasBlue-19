# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.modules.registry import Registry


class Users(models.Model):
    _inherit = 'res.users'

    restricted_menus = fields.Many2many('ir.ui.menu')

    def write(self, vals):
        if 'restricted_menus' in vals:
            self._update_registry()

        return super(Users, self).write(vals)

    def _update_registry(self):
        if self.env.registry.ready and not self.env.context.get('import_file'):
            self._cr.commit()
            self.env.reset()
            registry = Registry.new(self._cr.dbname)
            registry.registry_invalidated = True
