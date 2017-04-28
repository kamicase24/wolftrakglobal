# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    os = fields.Char(string='Sistema Operativo')
    cpu = fields.Char(string='Procesador')
    ram_1 = fields.Many2one('memory.storage', string='Memoria RAM', domain=[('type','=','ram')])
    ram_2 = fields.Many2one('memory.storage', string='Memoria RAM', domain=[('type','=','ram')])
    hard_disc = fields.Many2one('memory.storage', string='Disco Duro', domain=[('type','=','hard_disc')])
    charger = fields.Many2one('equipment.replacement', string='Cargador', domain=[('category','=','charger')])
    batery = fields.Many2one('equipment.replacement', string='Baterial', domain=[('category','=','batery')])
    peripheral = fields.Many2many('equipment.replacement', string='Perifericos', domain=[('category','=','peripheral')])

class MemoryStorage(models.Model):
    _name = 'memory.storage'

    name = fields.Char(string='Nombre', required=True)
    brand = fields.Char(string='Marca')
    model = fields.Char(string='Modelo')
    memory = fields.Integer(string='Capacidad')
    serial = fields.Char(string='Serial')
    type = fields.Selection([('hard_disc','Disco Duro'),('ram','Memoria RAM')], string="Tipo", required=True)

class EquipmentReplacement(models.Model):
    _name = 'equipment.replacement'

    name = fields.Char(string='Nombre del producto', required=True)
    brand = fields.Char(string='Marca')
    model = fields.Char(string='Modelo')
    serial = fields.Char(string='Serial')
    note = fields.Text(string='Nota')
    category = fields.Selection([('charger','Cargador'),('batery','Bateria'),('peripheral','Periferico')],string='Categoria', required=True)



