from odoo import models, fields, api
import time
from datetime import datetime
from dateutil import relativedelta

class wolftrakActivity(models.Model):
    _name = 'wolftrak.activity'
    _description = 'Actividad Detallada'

    date_from = fields.Date(string='Desde', default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Hasta', default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])

    def _default_name(self):
        ids=0
        for reg in self:
            ids = reg.id
        new_name = str(time.strftime('%Y-%m-01')[:4])+'/00'+str(ids)
        return new_name

    name = fields.Char(string='Reporte', readonly=True, default=_default_name)
    responsable = fields.Many2many('res.users', domain=[('id','!=',1)])
    activity = fields.Many2many('mail.message.subtype', string='Actividades', domain=[('res_model','=','crm.lead')])
    leads = fields.Many2many('crm.lead', string='Oportunidades')
    message = fields.Many2many('mail.message', string='Mensajes', readonly='True', compute='_get_messages')
    order = fields.Selection([('date','Fecha'),('activity','Actividades'),
                            ('user','Responsable'),('lead','Oportunidad/Cliente')],string="Ordenar por")


    @api.depends('message')
    def _get_total_act(self):
        message_subtypes = []
        total_act = []
        for msg in self.message:
            message_subtypes.append(msg.subtype_id.id)
        for i in self.activity:
            name_encode = str(i.name)
            total_act.append(name_encode+': '+str(message_subtypes.count(i.id)))
        self.total_act = str(len(self.message))+str(total_act).encode("utf-8")

    total_act = fields.Char(string="Total de Actividades", compute=_get_total_act)

    @api.depends('leads','date_from','date_to','activity','responsable')
    def _get_messages(self):
        date_n_model = [('date','<=',self.date_to),('date','>=',self.date_from),('model','=','crm.lead')]
        mail_msg = self.env['mail.message']
        for u in self.responsable:
            if self.activity:
                for act in self.activity:
                    if self.leads:
                        for ld in self.leads:
                            self.message += mail_msg.search([('create_uid','=',u.id),('subtype_id','=',act.id),('res_id','=',ld.id)]+date_n_model)
                    else:
                        self.message += mail_msg.search([('create_uid','=',u.id),('subtype_id','=',act.id)]+date_n_model)
            else:
                if self.leads:
                    for ld in self.leads:
                        self.message += mail_msg.search([('create_uid', '=', u.id),('res_id', '=', ld.id)] + date_n_model)
                else:
                    self.message += mail_msg.search([('create_uid', '=', u.id)] + date_n_model)
