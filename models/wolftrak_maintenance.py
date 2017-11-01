# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.modules import get_module_resource
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    os = fields.Char(string='Sistema Operativo')
    cpu = fields.Char(string='Procesador')
    ram_1 = fields.Many2one('memory.storage', string='Memoria RAM', domain=[('type', '=', 'ram')])
    ram_2 = fields.Many2one('memory.storage', string='Memoria RAM', domain=[('type', '=', 'ram')])
    hard_disc = fields.Many2one('memory.storage', string='Disco Duro', domain=[('type', '=', 'hard_disc')])
    charger = fields.Many2one('equipment.replacement', string='Cargador', domain=[('category', '=', 'charger')])
    batery = fields.Many2one('equipment.replacement', string='Baterial', domain=[('category', '=', 'batery')])
    peripheral = fields.Many2many('equipment.replacement', string='Perifericos',
                                  domain=[('category', '=', 'peripheral')])


class MemoryStorage(models.Model):
    _name = 'memory.storage'

    name = fields.Char(string='Nombre', required=True)
    brand_id = fields.Char(string='Marca')
    model_id = fields.Char(string='Modelo')
    memory = fields.Integer(string='Capacidad')
    serial = fields.Char(string='Serial')
    type = fields.Selection([('hard_disc', 'Disco Duro'), ('ram', 'Memoria RAM')], string="Tipo", required=True)


class EquipmentReplacement(models.Model):
    _name = 'equipment.replacement'

    name = fields.Char(string='Nombre del producto', required=True)
    brand_id = fields.Char(string='Marca')
    model_id = fields.Char(string='Modelo')
    serial = fields.Char(string='Serial')
    note = fields.Text(string='Nota')
    category = fields.Selection([('charger', 'Cargador'),
                                 ('batery', 'Bateria'),
                                 ('peripheral', 'Periferico')], string='Categoria', required=True)


class GpsDevice(models.Model):
    _name = 'gps.device'

    @api.model
    def _get_default_image(self):
        colorize, img_path, image = False, False, False
        if not image:
            img_path = get_module_resource('wolftrakglobal', 'static/src/img', 'gps.png')
            _logger.info(img_path)
            colorize = True
        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
                _logger.info(image)
        if image and colorize:
            image = tools.image_colorize(image)

        return tools.image_resize_image_medium(image.encode('base64'))

    @api.onchange('partner_id')
    def _get_default_invoice(self):
        self.invoices = self.env['account.invoice'].search([('partner_id', '=', self.partner_id.id)])

    @api.onchange('car_brand_id')
    def get_domain_model_id(self):

        self.car_model_id = None
        return {
            'domain': {
                'car_model_id': [('brand_id', '=', self.car_brand_id.id)]
            }
        }

    @api.onchange('brand_id')
    def get_domain_gps_model_id(self):

        self.model_id = None
        return {
            'domain': {
                'model_id': [('brand_id', '=', self.brand_id.id)]
            }
        }

    def _set_device_price(self):
        if self.invoices:
            unit_price = 0.0
            for inv in self.invoices:
                for lines in inv.invoice_line_ids:
                    if lines.product_id.id == 6:
                        if not unit_price != 0.0:
                            unit_price = lines.price_unit
            self.gps_price = unit_price

    def _default_start_date(self):
        if self.partner_id and self.partner_id.start_date:
            return self.partner_id.start_date

    def _default_currency(self):
        company_id = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
        currency_id = company_id.currency_id.id
        return currency_id

    def set_partner_dateprice(self):
        if self.partner_id:
            if self.partner_id.start_date:
                self.start_date = self.partner_id.start_date
            else:
                raise UserError(_("El cliente no posee Fecha de inicio de servicio."))

            if self.invoices:
                unit_price = 0.0
                month_payment = 0.0
                for inv in self.invoices:
                    inv_date = datetime.strptime(inv.date_invoice, '%Y-%m-%d')
                    gps_date = datetime.strptime(self.start_date, '%Y-%m-%d')
                    for lines in inv.invoice_line_ids:
                        if lines.product_id.id == 6:
                            if not unit_price != 0.0:
                                unit_price = lines.price_unit

                        if inv_date.month == gps_date.month and inv_date.year == gps_date.year:
                            if 'Mensualidad' in lines.product_id.name:
                                _logger.info(lines.product_id.id)
                                _logger.info(lines.product_id.name)
                                _logger.info(lines.price_unit)
                                month_payment = lines.price_unit
                self.gps_month_payment = month_payment
                self.gps_price = unit_price

            else:
                raise UserError(_("El cliente no posee facturas"))
        else:
            raise UserError(_("Seleccione un Cliente por favor"))

    name = fields.Char(required=True, string='Ficha')
    image = fields.Binary(default=_get_default_image)
    brand_id = fields.Many2one('gps.brand', string='Marca')
    model_id = fields.Many2one('gps.model', string='Modelo')
    imei = fields.Char(string='IMEI del GPS', help='International Mobile Station Equipment Identity')
    esn = fields.Char(string='ESN')
    sn = fields.Char(string='S/N')

    device_num = fields.Char(string='Número Asignado')
    sim_imei = fields.Char(string='IMEI SIMCARD')

    chassis = fields.Char(string='Chasis')
    license_plate = fields.Char(string='Placa')
    car_brand_id = fields.Many2one('car.brand', string='Marca del Vehiculo')
    car_model_id = fields.Many2one('car.model', string='Modelo del Vehiculo')
    year = fields.Char(string='Año del Vehiculo')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    alias = fields.Char(string='Razón Comercial', related='partner_id.alias', store=True)
    status = fields.Selection([('on', 'Activado'),
                               ('off', 'Desactivado'),
                               ('personal', 'Personal'),
                               ('garage', 'Taller'),
                               ('check', 'Verificar')],
                              string='Estado', readonly=True, default='on')

    note = fields.Text(string='Nota Interna')
    proyect = fields.Char(string='Proyecto')
    gps_price = fields.Float(string='Precio del Dispositivo')
    gps_month_payment = fields.Float(string='Mensualidad del Dispositivo')
    currency_id = fields.Many2one('res.currency', string='Moneda', default=_default_currency)
    start_date = fields.Date(string='Fecha de Inicio',
                             help='Fecha en que inicio el contrato el cliente',
                             default=_default_start_date)
    invoices = fields.Many2many('account.invoice', compute=_get_default_invoice)

    def status_on(self):
        self.status = 'on'

    def status_off(self):
        self.status = 'off'


class GpsBrand(models.Model):
    _name = 'gps.brand'

    name = fields.Char(string='Marca')
    note = fields.Text(string='Nota')
    model_lines = fields.One2many('gps.model', 'brand_id')
    supplier = fields.Many2one('res.partner', string='Proveedor',
                               domain=[('supplier', '=', True), ('customer', '=', False)])
    config_id = fields.Many2one('brands.models.config')


class GpsModel(models.Model):
    _name = 'gps.model'

    name = fields.Char(string='Modelo')
    note = fields.Text(string='Nota')
    brand_id = fields.Many2one('gps.brand', string='Marca')
    config_id = fields.Many2one('brands.models.config')


class CarBrand(models.Model):
    _name = 'car.brand'

    name = fields.Char(string='Marca')
    note = fields.Char(string='Nota')
    model_lines = fields.One2many('car.model', 'brand_id')
    config_id = fields.Many2one('brands.models.config')


class CarModel(models.Model):
    _name = 'car.model'

    name = fields.Char(string='Modelo')
    note = fields.Char(string='Nota')
    brand_id = fields.Many2one('car.brand', string='Marca')
    config_id = fields.Many2one('brands.models.config')


class GpsConfig(models.TransientModel):
    _name = 'gps.config'

    partner_id = fields.Many2one('res.partner', string='Cliente')
    sync_date = fields.Boolean(string='Fecha', default=True)
    custom_date = fields.Date()
    sync_unit_price = fields.Boolean(string='Precio del Disp.', default=True)
    custom_unit_price = fields.Float()
    sync_month_payment = fields.Boolean(string='Mensualidad del Disp.', default=True)
    custom_mont_payment = fields.Float()

    def sync_data(self):
        result = {'type': 'ir.actions.do_nothing'}

        if self.partner_id:
            if self.partner_id.start_date:
                start_date = self.partner_id.start_date
            else:
                raise UserError(_("El Cliente no posee fecha de inicio, actualice los datos antes de proceder"))

            gps_price = 0.0
            month_payment = 0.0
            invoices = self.env['account.invoice'].search([('partner_id', '=', self.partner_id.id)])

            if invoices:
                for inv in invoices:
                    inv_date = datetime.strptime(inv.date_invoice, '%Y-%m-%d')
                    gps_date = datetime.strptime(start_date, '%Y-%m-%d')
                    for lines in inv.invoice_line_ids:
                        if lines.product_id.id == 6:
                            if not gps_price != 0.0:
                                gps_price = lines.price_unit

                        # if inv_date.month == gps_date.month and inv_date.year == gps_date.year:
                        if 'Mensualidad' in lines.product_id.name:
                                month_payment = lines.price_unit

            if self.sync_unit_price and not self.custom_unit_price:
                gp_update = ', gps_price = %s' % gps_price
                result['gps_price'] = gp_update
            elif self.sync_unit_price and self.custom_unit_price:
                gp_update = ', gps_price = %s' % self.custom_unit_price
                result['gps_price'] = gp_update
            else:
                result['gps_price'] = ''

            if self.sync_month_payment and not self.custom_mont_payment:
                mp_update = 'gps_month_payment = %s' % month_payment
                result['month_payment'] = mp_update
            elif self.sync_month_payment and self.custom_mont_payment:
                mp_update = 'gps_month_payment = %s' % self.custom_mont_payment
                result['month_payment'] = mp_update
            else:
                result['month_payment'] = ''

            if self.sync_date and not self.custom_date:
                dt_update = ', start_date = "%s"' % start_date
                result['start_date'] = dt_update
            elif self.sync_date and self.custom_date:
                dt_update = ', start_date = "%s"' % self.custom_date
                result['start_date'] = dt_update
            else:
                result['start_date'] = ''

            _logger.info(result)

            sql = 'update gps_device set ' + result['month_payment'] + result['gps_price'] + result['start_date'] + ' where partner_id = %s' % self.partner_id.id

            _logger.info(sql)
            self.env.cr.execute(sql)

        else:
            raise UserError(_("Por Favor seleccione un Cliente"))

        return result


class MobileDevice(models.Model):
    _name = 'mobile.device'

    @api.onchange('brand_id')
    def get_domain_model_id(self):

        return {
            'domain': {
                'model_id': [('brand_id', '=', self.brand_id.id)]
            }
        }

    name = fields.Char(required=True)
    brand_id = fields.Many2one('mobile.brand', string='Marca')
    model_id = fields.Many2one('mobile.model', string='Modelo')
    imei = fields.Char(string='IMEI', help='International Mobile Station Equipment Identity')
    batery = fields.Char(string='Batería')
    batery_serial = fields.Char(string='Serial de la Batería')
    batery_model = fields.Char(string='Modelo de la Batería')
    employee_id = fields.Many2one('hr.employee', string='Empleado', domain=[('id', '!=', 1)],
                                  help='Empleado Asignado a este número de telefono')
    number = fields.Char(string='Número asociado')
    simcard_imei = fields.Char(string='IMEI de la Simcard')


class BransModelsConfig(models.Model):
    _name = 'brands.models.config'

    def default_gps_brands(self):
        return self.env['gps.brand'].search([])

    def default_gps_models(self):
        return self.env['gps.model'].search([])

    def default_car_brands(self):
        return self.env['car.brand'].search([])

    def default_car_models(self):
        return self.env['car.model'].search([])

    @api.onchange('brand_id', 'model_id', 'car_brand_id', 'car_model_id')
    def write(self):
        sql = 'delete from brands_models_config'
        self.env.cr.execute(sql)

    brand_id = fields.One2many('gps.brand', 'config_id', string='Marca', default=default_gps_brands)
    model_id = fields.One2many('gps.model', 'config_id', string='Modelo', default=default_gps_models)
    car_brand_id = fields.One2many('car.brand', 'config_id', string='Marca del Vehiculo', default=default_car_brands)
    car_model_id = fields.One2many('car.model', 'config_id', string='Modelo del Vehiculo', default=default_car_models)


class MobileBrand(models.Model):
    _name = 'mobile.brand'

    name = fields.Char(string='Marca', required=True)
    note = fields.Text(string='Nota')
    model_lines = fields.One2many('mobile.model', 'brand_id')

    # @api.multi
    # def write(self, vals):
    #
    #     vals['name'] = self.name+' ['+self.model+']'
    #     return super(MobileBrand, self).write(vals)


class MobileModel(models.Model):
    _name = 'mobile.model'

    name = fields.Char(string='Modelo', required=True)
    brand_id = fields.Many2one('mobile.brand', string='Marca')



