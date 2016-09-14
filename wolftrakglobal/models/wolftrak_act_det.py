from openerp import api, fields, models, _
from openerp.osv import expression
from openerp import models, fields, api

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

class wolftrakActivity(models.Model):
	_name = 'wolftrak.actividad'
	_description = 'Actividad Detallada'

	desde = fields.Date(string='Desde', default=time.strftime('%Y-%m-01'))
	hasta = fields.Date(string='Hasta', default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])

	def _default_periodo(self):
		year = str(time.strftime('%Y-%m-01')[:4])
		wolftrak_actividades = self.env['wolftrak.actividad'].search([])
		for reg in wolftrak_actividades:
			ids = reg.id
		pernew = year+'00'+(str(ids+1))
		return pernew

	periodo = fields.Char(string='Periodo', readonly=True, default=_default_periodo)
	leads = fields.Many2many('crm.lead', 
		string='Ventas', 
		readonly=True,
		compute='_rango_leads')

	responsable = fields.Many2one('res.users')

	mensaje = fields.Many2many('mail.message',
		string='Mensajes',
		readonly='True',
		compute='_toma_mensajes')

	@api.depends('desde','hasta','responsable')
	def _rango_leads(self):
		date1 = self.desde
		date2 = self.hasta
		resp = self.responsable
		if not resp:
			self.leads = self.env['crm.lead'].search([('create_date','>=',date1),
																	('create_date','<=',date2)])
		else:
			self.leads = self.env['crm.lead'].search([('create_date','>=',date1),
																	('create_date','<=',date2),
																	('user_id', '=', resp.id)])

	@api.depends('leads')
	def _toma_mensajes(self):
		for name in self.leads:
			self.mensaje += self.env['mail.message'].search([('model','=','crm.lead'),
																			('res_id', '=', name.id)])