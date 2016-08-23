from openerp import api, fields, models, _
from openerp.osv import expression
from openerp import models, fields, api

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

class wolftrakMove(models.Model):
	_name = 'wolftrak.move'
	_description = 'Libro Diario'

	date_to = fields.Date(string='Desde')
	date_from = fields.Date(string='Hasta')

	def _default_lines(self):
		return self.env['account.move.line'].search([]) # Retorna una lista con el nuevo api

	moves_ids = fields.Many2many('account.move', 'id', 'date', 'name', 
		string='Entrada del libro diario',
		readonly=True,
		compute='_default_move')

	@api.depends('date_to','date_from')
	def _default_move(self):
		date1 = self.date_to
		date2 = self.date_from
		self.moves_ids = self.env['account.move'].search([('date','>=',date1),('date','<=',date2),('company_id','=',3)])