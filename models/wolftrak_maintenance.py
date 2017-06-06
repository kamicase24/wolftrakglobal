# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.modules import get_module_resource
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

class GpsDevice(models.Model):
    _name = 'gps.device'

    @api.model
    def _get_default_image(self):
        colorize, img_path, image = False, False, False
        if not image:
            img_path = get_module_resource('wolftrakglobal','static/src/img','gps.png')
            _logger.info(img_path)
            colorize = True
        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
                _logger.info(image)
        if image and colorize:
            image = tools.image_colorize(image)

        return tools.image_resize_image_medium(image.encode('base64'))

    name = fields.Char(required=True)
    image = fields.Binary(default=_get_default_image)
    brand = fields.Many2one('gps.brand', string='Marca')
    model = fields.Many2one('gps.model',string='Modelo')
    imei = fields.Char(string='IMEI', help='International Mobile Station Equipment Identity')
    esn = fields.Char(string='ESN')
    sn = fields.Char(string='S/N')
    stock = fields.Integer(string='Stock')
    note = fields.Text(string='Nota Interna')

class GpsBrand(models.Model):
    _name = 'gps.brand'

    name = fields.Char(string='Marca')
    note = fields.Text(string='Nota')
    supplier = fields.Many2one('res.partner', string='Proveedor', domain=[('supplier','=',True),('customer','=',False)])

class GpsModel(models.Model):
    _name = 'gps.model'

    name = fields.Char(string='Modelo')
    note = fields.Text(string='Nota')



