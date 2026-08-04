# -*- coding: utf-8 -*-

import copy
import logging
import functools
from werkzeug import urls
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import models, fields, api, tools, _
import dateutil.relativedelta as relativedelta
from odoo.tools.misc import get_lang, format_date, format_datetime

_logger = logging.getLogger(__name__)

try:
    from jinja2.sandbox import SandboxedEnvironment

    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': functools.reduce,
        'map': map,
        'timedelta': timedelta,
        'round': round,
        'relativedelta': lambda *a, **kw: relativedelta.relativedelta(*a, **kw),
    })
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


to_19_ar = (u'صفر', u'واحد', u'اثنان', u'ثلاثة', u'أربعة', u'خمسة', u'ستة',
            u'سبعة', u'ثمانية', u'تسعة', u'عشرة', u'أحد عشر', u'اثنا عشر', u'ثلاثة عشر',
            u'أربعة عشرة', u'خمسة عشر', u'ست عشرة', u'سبعة عشر', u'ثمانية عشر', u'تسعة عشر')

tens_ar = (u'', u'', u'عشرون', u'ثلاثون', u'أربعون', u'خمسون', u'ستون', u'سبعون', u'ثمانون', u'تسعون')

hund_ar = (u'', u'', u'مئتان', u'ثلاثمائة', u'اربعمائة', u'خمسمائة', u'ستمائة', u'سبعمائة', u'ثمانمائة', u'تسعمائة')


def convert_less_100(number):
    if number <= 19:
        return to_19_ar[int(number)]
    elif number < 100:
        ten = number / 10
        rest = number % 10
        if rest != 0:
            return to_19_ar[abs(int(rest))] + u' و ' + tens_ar[abs(int(ten))]
        else:
            return tens_ar[int(ten)]


def convert_less_1000(number):
    hund = number / 100
    rest = number % 100
    if hund == 0:
        hund_text = u''
    elif hund == 1:
        hund_text = u'مئة'
    elif hund < 10:
        hund_text = hund_ar[int(hund)]
    else:
        hund_text = convert_less_1000(hund) + u' مئة '
    if rest != 0:
        if hund_text != u'':
            hund_text = hund_text + u' و ' + convert_to_ar(rest)
        else:
            hund_text = convert_to_ar(rest)

    return hund_text


def convert_less_10000(number):
    thous = number / 1000
    rest = number % 1000
    if thous == 0:
        thous_text = u''
    elif thous == 1:
        thous_text = u'الف'
    elif thous == 2:
        thous_text = u'الفين'
    elif thous <= 10:
        thous_text = convert_less_100(thous) + u'آلاف'
    else:
        thous_text = convert_less_1000(thous) + u' الف '
    if rest != 0:
        if thous_text != u'':
            thous_text = thous_text + u' و ' + convert_to_ar(rest)
        else:
            thous_text = convert_to_ar(rest)

    return thous_text


def convert_less_billion(number):
    million = number / 1000000
    rest = number % 1000000
    if million == 1:
        million_text = u'مليون'
    elif million == 2:
        million_text = u'مليونين'
    elif million <= 10:
        million_text = convert_less_100(million) + u' ' + u'ملايين'
    else:
        million_text = convert_less_1000(million) + u' ' + u'مليون'
    if rest != 0:
        million_text = million_text + u' و ' + convert_to_ar(rest)

    return million_text


def convert_over_billion(number):
    million = number / 1000000000
    rest = number % 1000000000
    if million == 1:
        million_text = u'مليار'
    elif million == 2:
        million_text = u'مليارين'
    elif million <= 10:
        million_text = convert_less_100(million) + u' ' + u'ملايير'
    else:
        million_text = convert_less_1000(million) + u' ' + u'مليار'
    if rest != 0:
        million_text = million_text + u' و ' + convert_to_ar(rest)

    return million_text


def convert_to_ar(number):
    if number < 100:
        return convert_less_100(number)
    elif number < 1000 and number >= 100:
        return convert_less_1000(number)
    elif number < 1000000 and number >= 1000:
        return convert_less_10000(number)
    elif number < 1000000000 and number >= 1000000:
        return convert_less_billion(number)
    else:
        return convert_over_billion(number)


def amount_to_text_ar(number):
    number = '%.2f' % number
    # units_name = currency
    lst = str(number).split('.')
    start_word = convert_to_ar(abs(int(lst[0])))
    final_result = start_word + u' '

    return final_result


class ContractTemplate(models.Model):
    _name = 'contract.template'
    _description = "Contract Template"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    body = fields.Html(string="Body")


class SaleContract(models.Model):
    _name = 'sale.contract'
    _description = "Sale Contract"
    _rec_name = 'sale_order_id'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    contract_template_id = fields.Many2one('contract.template')
    body = fields.Html(string="Contract")

    @api.onchange('sale_order_id', 'contract_template_id')
    def _onchange_contranct_template_id(self):
        if self.contract_template_id and self.contract_template_id.body and self.sale_order_id:
            template = self.sudo()._render_template(self.contract_template_id.body, self.sale_order_id._name, self.sale_order_id.id)
            self.body = template

    def action_print_contract(self):
        action = self.env.ref('project_contract_tmpl.contract_report_action').report_action(self.ids)
        return action

    @api.model
    def _get_date_formats(self):
        lang = get_lang(self.env)
        return (lang.date_format, lang.time_format)

    @api.model
    def _render_template(self, template_txt, model, res_ids):
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]

        results = dict.fromkeys(res_ids, u"")
        try:
            mako_env = mako_safe_template_env if self.env.context.get('safe') else mako_template_env
            template = mako_env.from_string(tools.ustr(template_txt))
        except Exception:
            _logger.info("Failed to load template %r", template_txt, exc_info=True)
            return multi_mode and results or results[res_ids[0]]

        records = self.env[model].browse(it for it in res_ids if it)
        res_to_rec = dict.fromkeys(res_ids, None)
        for record in records:
            res_to_rec[record.id] = record

        variables = {
            'format_date': lambda date, format=False, context=self._context: format_date(self.env, date, format),
            'format_datetime': lambda dt, format=False, context=self._context: format_datetime(self.env, dt, format),
            'amount_to_text_ar': amount_to_text_ar,
            'user': self.env.user,
            'ctx': self._context,
            'web_base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
            'contract_date': self.create_date.strftime('%d/%m/%Y') if self.create_date else fields.Date.today().strftime('%d/%m/%Y'),
        }
        for res_id, record in res_to_rec.items():
            variables['object'] = record
            try:
                render_result = template.render(variables)
            except Exception:
                _logger.info("Failed to render template %r using values %r" % (template, variables), exc_info=True)
                raise UserError(_("Failed to render template %r using values %r") % (template, variables))
            if render_result == u"False":
                render_result = u""
            results[res_id] = render_result

        return multi_mode and results or results[res_ids[0]]
