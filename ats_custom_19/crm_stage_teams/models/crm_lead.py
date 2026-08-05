# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID


class Lead(models.Model):
    _inherit = 'crm.lead'

    stage_id = fields.Many2one('crm.stage', string="Stage", ondelete='restrict', index=True, copy=False, group_expand='_read_group_stage_ids',
                               domain="['|', ('team_ids', '=', False), ('team_ids', '=', team_id)]", default=lambda self: self._default_stage_id())

    def _default_stage_id(self):
        team = self._default_team_id(user_id=self.env.uid)
        return self._stage_find(team_id=team.id, domain=[('fold', '=', False)]).id

    def _default_team_id(self, user_id):
        domain = [('use_leads', '=', True)] if self._context.get('default_type') == "lead" or self.type == 'lead' else [('use_opportunities', '=', True)]
        return self.env['crm.team']._get_default_team_id(user_id=user_id, domain=domain)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        team_id = self._context.get('default_team_id')
        if team_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_ids', '=', False), ('team_ids', 'in', [team_id])]
        else:
            search_domain = ['|', ('id', 'in', stages.ids), ('team_ids', '=', False)]

        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)
