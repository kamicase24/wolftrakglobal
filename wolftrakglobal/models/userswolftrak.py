# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp.osv import orm
from openerp.osv import osv, fields
class wolftrak_new2(osv.Model):
	_name = "res.partner"
	_inherit = "res.partner"

	_columns = {
		'ci': fields.char(string='CI/RNC', help='Documento de Identificacion')
	}