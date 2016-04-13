# -*- coding: utf-8 -*-
from openerp import models, fields #importa los objetos models y fields de el Core de Odoo
class wolftraknew(models.Model): #declara un nuevo modelo. Deriva de models.Model
	#define el atributo _nombre, identificador que sera usado por Odoo para referises a este modelo 
	_name = 'wolftrakglobal'
	_inherit = 'res.partner'
	
	_order = "display_name"
	_columns = {
		'category_id': fields.Char('res.partner.category', id1='partner_id', id2='category_id', string='Tags')    	
    }

	# estas ultimas 3 lineas define los campos del modelo
	# name    = fields.Char('Description', required=True)
	# is_done = fields.Boolean('Done?')
	# active  = fields.Boolean('Active?', default=True)
