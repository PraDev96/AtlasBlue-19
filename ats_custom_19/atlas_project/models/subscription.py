# -*- coding: utf-8 -*-

from odoo import models, fields

class IrAttachments(models.Model):
    _inherit = "ir.attachment"

    def delete_binary_files(self, limit=None):
        domain = [('mimetype', 'in', ('application/pdf', 'image/jpeg', 'image/png'))]
        binary_attachments = self.env['ir.attachment'].sudo().search(domain, limit=limit)
        if binary_attachments:
            binary_attachments.unlink()
