# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import UserError

class gamification_badge_user(osv.Model):
	_name = 'gamification.badge.user'
	_inherit = 'gamification.badge.user'

	_columns = {
		'custom_value': fields.char(
		string="Valor de la Insignia",
		help="Otorga un valor predeterminado para la insignia.",
		)
	}

class gamification_badge_wizard(osv.Model):
	_name = 'gamification.badge.user.wizard'
	_inherit = 'gamification.badge.user.wizard'

	_columns = {
		'custom_value': fields.char(
		string="Valor de la Insignia",
		help="Otorga un valor predeterminado para la insignia.",
		)
	}

# 	def new_action_grant_badge(self, cr, uid, ids, context=None):
# 		badge_user_obj = self.pool.get('gamifitacion.badge.user')

# 		for wiz in self.browse(cr, uid, ids, context=context):
# 			values = {
# 				'custom_value': wiz.custom_value
# 			}
# 			badge_user = badge_user_obj.


