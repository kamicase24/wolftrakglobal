# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions

class WolftrakGamificationBadgeWizard(models.TransientModel):
    _name = 'gamification.badge.user.wizard'
    _inherit = 'gamification.badge.user.wizard'

    wolftrak_win_value = fields.Integer(string="Porcentaje de exito")

    @api.multi
    def action_grant_badge(self):
        """Wizard action for sending a badge to a chosen user"""

        BadgeUser = self.env['gamification.badge.user']
        uid = self.env.uid

        for wiz in self:
            if uid == wiz.user_id.id:
                raise exceptions.UserError(_('You can not grant a badge to yourself'))
            #create the badge
            BadgeUser.create({
                'user_id': wiz.user_id.id,
                'sender_id': uid,
                'badge_id': wiz.badge_id.id,
                'comment': wiz.comment,
                'wolftrak_win_value_user': wiz.wolftrak_win_value
            })._send_badged()

        return True

class WolftrakGamificationBadgeUserWizard(models.TransientModel):
    _name = 'gamification.badge.user.wizard'
    _inherit = 'gamification.badge.user.wizard'

    wolftrak_win_value = fields.Integer(string="Porcentaje de exito")

    @api.multi
    def action_grant_badge(self):
        """Wizard action for sending a badge to a chosen employee"""

        if not self.user_id:
            raise exceptions.UserError(_('You can send badges only to employees linked to a user.'))

        if self.env.uid == self.user_id.id:
            raise exceptions.UserError(_('You can not send a badge to yourself'))

        values = {
            'user_id': self.user_id.id,
            'sender_id': self.env.uid,
            'badge_id': self.badge_id.id,
            'employee_id': self.employee_id.id,
            'comment': self.comment,
            'wolftrak_win_value_user': self.wolftrak_win_value
        }

        return self.env['gamification.badge.user'].create(values)._send_badge()