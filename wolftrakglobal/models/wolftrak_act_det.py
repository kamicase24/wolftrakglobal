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
		ids = 0
		for reg in wolftrak_actividades:
			ids = reg.ids
		nuevo_periodo = year+'00'+str(ids)
		return nuevo_periodo

	periodo = fields.Char(string='Periodo', readonly=True, default=_default_periodo)


	tipo_reporte = fields.Selection([
		('cliente','Por cliente'),
		('fecha','Por Fecha'),
		('total','Totalizado')], string="Tipo de Reporte")

	responsable = fields.Many2one('res.users')

	leads = fields.Many2many('crm.lead', string='Ventas', readonly=True, compute='_toma_leads')

	mensaje = fields.Many2many('mail.message', string='Mensajes', readonly='True', compute='_toma_mensajes')

	actividad = fields.Many2many('mail.message.subtype', string='Actividades', readonly='True', compute='_toma_actividad')

	act_report = fields.Many2many('crm.activity.report', string='Reporte de activiade', readonly='True', compute='_toma_actividad')

	@api.depends('desde','hasta','responsable')
	def _toma_leads(self):
		date1 = self.desde
		date2 = self.hasta
		resp = self.responsable
		if not resp:
			self.leads = self.env['crm.lead'].search([])
		else:
			self.leads = self.env['crm.lead'].search([('user_id', '=', resp.id)])

	@api.depends('leads')
	def _toma_mensajes(self):
		for name in self.leads:
			self.mensaje += self.env['mail.message'].search([('model','=','crm.lead'),('res_id', '=', name.id),('date','<',self.hasta),('date','>=',self.desde)])

	@api.depends('leads','hasta','desde')
	def _toma_actividad(self):
		resp = self.responsable
		self.actividad =  self.env['mail.message.subtype'].search([('res_model','=','crm.lead')])
		if not resp:
			self.act_report = self.env['crm.activity.report'].search([('date','<', self.hasta),('date','>=',self.desde)])
		else:
			self.act_report = self.env['crm.activity.report'].search([('date','<', self.hasta),('date','>=',self.desde),('user_id','=',resp.id)])