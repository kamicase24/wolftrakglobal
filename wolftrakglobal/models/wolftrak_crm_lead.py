# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import logging
from operator import itemgetter
from werkzeug import url_encode

from openerp import SUPERUSER_ID
from openerp import tools, api
from openerp.addons.base.res.res_partner import format_address
from openerp.addons.crm import crm_stage
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import email_re, email_split
from openerp.exceptions import UserError, AccessError


class crm_lead(format_address, osv.osv):
	_name = "crm.lead"
	_inherit = "crm.lead"

	_columns = {
		'call_duration': fields.float(string='Duración de la llamada')
	}
	
	def log_next_activity_done(self, cr, uid, ids, context=None, next_activity_name=False):

		to_clear_ids = []
		for lead in self.browse(cr, uid, ids, context=context):
			if not lead.next_activity_id:
				continue
			body_html = """<div><b>${object.next_activity_id.name}</b></div>
%if object.title_action:
<div>${object.title_action}</div>
<div>Duración de llamada: ${object.call_duration}0</div>
%endif"""
			body_html = self.pool['mail.template'].render_template(cr, uid, body_html, 'crm.lead', lead.id, context=context)
			msg_id = lead.message_post(body_html, subtype_id=lead.next_activity_id.subtype_id.id)
			to_clear_ids.append(lead.id)
			self.write(cr, uid, [lead.id], {'last_activity_id': lead.next_activity_id.id}, context=context)
			
			msg_id.write({'call_duration':lead.call_duration})

			lead.call_duration = 0.0

		if to_clear_ids:
			self.cancel_next_activity(cr, uid, to_clear_ids, context=context)
		return True