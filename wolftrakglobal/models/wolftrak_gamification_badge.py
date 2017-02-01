# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _, exceptions

class WolftrakGamificationBadgeUser(models.Model):
    _name = 'gamification.badge.user'
    _inherit = 'gamification.badge.user'

    wolftrak_win_value_user = fields.Integer(string="Porcentaje de exito")


class WolftrakGamification(models.Model):
    _name = 'gamification.badge'
    _inherit = 'gamification.badge'

    wolftrak_value = fields.Integer(string="Valor de la Insignea")