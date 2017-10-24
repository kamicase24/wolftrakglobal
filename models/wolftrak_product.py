# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
_logger = logging.getLogger(__name__)


class ProductWolftrak(models.Model):
    _inherit = "product.template"

    type = fields.Selection([
        ('consu', _('Consumable')),
        ('service', _('Service')),
        ('product', _('Almacenable')),
        ('pack', _('Paquete'))], string='Product Type', default='consu', required=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A consumable product, on the other hand, is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')

    pack_line_ids = fields.One2many('pack.line.wolftrak', 'product_id', string='Productos')
    pack_code = fields.Char(string='Pack #')

    @api.multi
    def _compute_currency_id(self):
        for template in self:
            template.currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)


class PackWolftrak(models.Model):
    _name = 'pack.line.wolftrak'

    @api.onchange('pack_item_id')
    def _set_values(self):
        if self.pack_item_id:
            pack_item_id = self.pack_item_id
            self.currency_id = pack_item_id.currency_id
            self.uom_id = pack_item_id.uom_id
            self.list_price = pack_item_id.list_price
            self.description = pack_item_id.name

    product_id = fields.Many2one('product.template', string='Producto')
    pack_item_id = fields.Many2one('product.template', string='Item')
    description = fields.Char(string='Descripción')
    quantity = fields.Float(string='Cantidad', default=1.0)
    list_price = fields.Float(string='Precio de Venta')
    uom_id = fields.Many2one('product.uom', string='Unidad de Medida')
    currency_id = fields.Many2one('res.currency', string='Moneda')


class ProductProductWolftrak(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _need_procurement(self):
        for product in self:
            if product.type not in ['service', 'digital', 'pack']:
                return True
        return super(ProductProductWolftrak, self)._need_procurement()
