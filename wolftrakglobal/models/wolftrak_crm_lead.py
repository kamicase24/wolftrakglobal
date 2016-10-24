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
	