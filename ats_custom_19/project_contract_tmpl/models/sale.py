# -*- coding: utf-8 -*-

import re
import logging
from odoo import models, fields, _

_logger = logging.getLogger(__name__)


try:
    from deep_translator import GoogleTranslator
except ImportError:
    _logger.warning("The deep_translator python library is not installed, amount-to-text in contract report print features won't be fully available.")
    GoogleTranslator = None


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_count = fields.Integer(tracking=True, compute='_compute_contract_count')

    def get_amount_in_word(self, language='en'):
        """
            This is for convert the amount in word for both English and Arabic.
        """
        amount_word = self.currency_id.amount_to_text(self.amount_total) + ' Only'
        if language == 'ar':
            amount_word = self._get_arabic_text(amount_word)

        return amount_word

    def get_project_second_party_address(self):
        """
            This is for getting the Project client Address.
        """
        project_client_address = []
        if self.partner_id.area_id:
            project_client_address.append(self.partner_id.area_id.name)
        if self.partner_id.block:
            project_client_address.append(self.partner_id.block)
        if self.partner_id.street:
            project_client_address.append(self.partner_id.street)
        if self.partner_id.house:
            project_client_address.append(self.partner_id.house)

        return ", ".join(project_client_address) if project_client_address else "............"

    def get_project_shipping_address(self):
        """
            This is for getting the Project address all together.
        """
        project_address_list = []
        if self.partner_shipping_id:
            if self.partner_shipping_id.area_id:
                project_address_list.append(self.partner_shipping_id.area_id.name)
            if self.partner_shipping_id.block:
                project_address_list.append(self.partner_shipping_id.block)
            if self.partner_shipping_id.street:
                project_address_list.append(self.partner_shipping_id.street)
            if self.partner_shipping_id.house:
                project_address_list.append(self.partner_shipping_id.house)

        return ", ".join(project_address_list) if project_address_list else "............"

    def _get_arabic_text(self, input_text):
        """
            This is for converting all the words that include letters, special character and number to Arabic language;
             By using the package 'deep_translator'
        """
        converted_text = " "
        if input_text:
            if isinstance(input_text, (int, float)):
                digit_map = {
                    '0': '٠',
                    '1': '١',
                    '2': '٢',
                    '3': '٣',
                    '4': '٤',
                    '5': '٥',
                    '6': '٦',
                    '7': '٧',
                    '8': '٨',
                    '9': '٩',
                    '.': '.'
                }
                converted_text = ''.join(digit_map[digit] for digit in str(input_text) if digit in digit_map)
            else:
                parts = re.split(r'(\d+|\D+|\s+|\(|\))', input_text)
                translated_parts = []

                for part in parts:
                    if part.isdigit():
                        # Convert Western Arabic numerals to Arabic numerals
                        arabic_numerals_text = ''.join(map(lambda x: str(chr(ord('٠') + int(x))), part))
                        translated_parts.append(arabic_numerals_text)
                    elif part.isspace() or part in ['(', ')', '/']:
                        translated_parts.append(part)
                    else:
                        translator = GoogleTranslator(source='auto', target='ar')
                        translated_text = translator.translate(part)
                        translated_parts.append(translated_text)

                converted_text = ''.join([str(item) for item in translated_parts if item is not None])

        return converted_text or " "

    def _compute_contract_count(self):
        contract_obj = self.env['sale.contract']
        for rec in self:
            rec.contract_count = contract_obj.search_count([('sale_order_id', '=', rec.id)])

    def open_contract_of_project(self):
        ctx = self.env.context.copy()
        ctx.update({
            'create': True,
            'default_sale_order_id': self.id,
        })
        return {
            'name': _('Contracts'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.contract',
            'domain': [('sale_order_id', 'in', self.ids)],
            'type': 'ir.actions.act_window',
            'context': ctx,
        }
