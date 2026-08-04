# -*- coding: utf-8 -*-
import pprint

from odoo import models, api


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def get_user_roots(self):
        menus = super(IrUiMenu, self).get_user_roots()
        menu_to_hide = self.env.user.restricted_menus.filtered(lambda m: not m.parent_id)

        return menus - menu_to_hide

    @api.model
    def load_menus(self, debug):
        menu_root = super(IrUiMenu, self).load_menus(debug)
        child_menus = menu_root['root']['children']
        child_menu_to_hide = self.env.user.restricted_menus.ids

        def check_recursive_menu(menu):
            """ To check and remove menu from final destination. """
            for m in menu:
                if m['id'] in child_menu_to_hide:
                    menu.remove(m)
                elif m['children']:
                    check_recursive_menu(m['children'])

        # if child_menus and child_menu_to_hide:
        #     for cmenu in child_menus.keys():
        #         if cmenu['id'] in child_menu_to_hide:
        #             child_menus.remove(cmenu)
        #         elif cmenu['children']:
        #             check_recursive_menu(cmenu['children'])

        # menu_root['all_menu_ids'] = list(set(menu_root['all_menu_ids']) - set(child_menu_to_hide))
        # for menu in menu_root.keys():
        #     if menu in set(child_menu_to_hide):
        #         menu_root.pop(menu)

        return menu_root
