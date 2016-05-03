# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.osv import osv, fields
class wolftrak_new2(osv.Model):
	_name = "res.partner"
	_inherit = "res.partner"

	_columns = {
		'ci': fields.char(string='Documento de Identificacion', help='Documento de Identificacion')
	}

	@api.onchange('ci', 'phone')
	def user_validation(self):
		# Realiza la comparacion del dato que se insertara con los registrados en la base de datos
		db_ci = self.search([('ci', '=', self.ci)])
		# Almacena el campo que se insertara en variables
		act_ci = self.ci
		# si db_ci esta vacio(False), el usuario no esta registrado 
		if db_ci and act_ci :
			raise orm.except_orm(
                _("Warning"),
                _("""\
Este Usuario ya esta registrado"""),
            )