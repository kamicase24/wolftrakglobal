# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import models, fields, api
from openerp.osv import fields, osv
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.exceptions import UserError

class gamification_badge_user(osv.Model):
	_name = 'gamification.badge.user'
	_inherit = 'gamification.badge.user'

	_columns = {
		'custom_value': fields.integer(
		string="Insignea ganada al")
	}

class gamification_badge_wizard(osv.Model):
	_name = 'gamification.badge.user.wizard'
	_inherit = 'gamification.badge.user.wizard'

	_columns = {
		'custom_value': fields.integer(
		string="Insignea ganada al")
	}

	def custom_grant_badge(self, cr, uid, ids, context=None):
		"""Wizard action for sending a badge to a chosen user"""

		badge_user_obj = self.pool.get('gamification.badge.user')
		for wiz in self.browse(cr, uid, ids, context=context):
			if uid == wiz.user_id.id:
				raise UserError(_('You can not grant a badge to yourself'))
			#create the badge
			values = {
				'user_id': wiz.user_id.id,
				'sender_id': uid,
				'badge_id': wiz.badge_id.id,
				'comment': wiz.comment,
				'custom_value': wiz.custom_value
			}
			badge_user = badge_user_obj.create(cr, uid, values, context=context)
			result = badge_user_obj._send_badge(cr, uid, badge_user, context=context)
		return result

class gamification_badge(osv.Model):
	_name = 'gamification.badge'
	_inherit = 'gamification.badge'

	_columns = {
		'custom_value': fields.integer(
		string="Valor de la Insignea")
	}

