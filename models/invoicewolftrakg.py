# -*- coding: utf-8 -*-
from openerp import models, fields #importa los objetos models y fields de el Core de Odoo
from openerp.osv import orm
class wolftraknew(orm.Model): #declara un nuevo modelo. Deriva de models.Model
	#define el atributo _nombre, identificador que sera usado por Odoo para referises a este modelo 
	_name = 'account.invoice'
	_inherit = 'account.invoice'

	ncf = fields.Char(string="NCF")

	# _default = {
	# 	'ncf' : "hola"
	# }

	# estas ultimas 3 lineas define los campos del modelo
	# name    = fields.Char('Description', required=True)
	# is_done = fields.Boolean('Done?')
	# active  = fields.Boolean('Active?', default=True)
