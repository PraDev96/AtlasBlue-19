
from odoo import models, fields


class PassportHistory(models.Model):
    _inherit = 'res.bank'

    branch_name = fields.Char(string="Branch Name")
