import logging
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from bs4 import BeautifulSoup
import requests
_logger = logging.getLogger(__name__)


class WolftrakSaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    def _compute_pack_picking_ids(self):
        pack_picking_ids = self.env['stock.picking']
        for line in self.order_line:
            if line.product_id.type == 'pack':
                origin = line.order_id.name + '(PACK-%s)' % str(line.product_id.name)
                pack_picking_ids += self.env['stock.picking'].search([('origin', '=', origin)])
        self.pack_picking_ids = pack_picking_ids

    pack_picking_ids = fields.Many2many('stock.picking', compute=_compute_pack_picking_ids,
                                        string='Movimientos de los paquetes asociado con este SO')

    def currency_exchange(self):
        self.env['wolftrak.tools'].currency_exchange(self)

    def action_view_packs(self):
        pack_picking_ids = self.mapped('pack_picking_ids')

        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        if len(pack_picking_ids) > 1:
            action['domain'] = [('id', 'in', pack_picking_ids.ids)]
        elif pack_picking_ids:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pack_picking_ids.id
        return action

    def _compute_pack_ids(self):
        packs = 0
        for line in self.order_line:
            if line.product_id.type == 'pack':
                _logger.info(line.product_id.name)
                packs += 1
        self.pack_count = len(self.pack_picking_ids)

    def default_ex_rate(self):
        if not self.partner_id and not self.ex_rate:
            return self.env['wolftrak.tools'].default_ex_rate_2()

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                   help="Pricelist for current sales order.", default=2)
    ex_rate = fields.Float(string='Tasa de Cambio del dia', digits=(1, 4),
                           default=lambda self: self.default_ex_rate())

    pack_count = fields.Integer(string='Paquetes', compute=_compute_pack_ids)

    def _delete_pack_picking(self):
        for line in self.order_line:
            picking_id = line.order_id.picking_ids
            if line.product_id.type == 'pack':
                if len(picking_id.move_lines) <= 1:
                    if picking_id.move_lines.product_id.type == 'pack':

                        sql = 'delete from stock_move where id = %s' % picking_id.move_lines.id
                        self.env.cr.execute(sql)
                    sql = 'delete from stock_picking where id = %s' % picking_id.id
                    self.env.cr.execute(sql)

                else:
                    for move in picking_id.move_lines:
                        if move.product_id.type == 'pack':
                            sql = 'delete from stock_move where id = %s' % move.id
                            self.env.cr.execute(sql)

    @api.multi
    def action_confirm(self):
        res = super(WolftrakSaleOrder, self).action_confirm()
        self._delete_pack_picking()
        return res


class WolftrakSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _calculate_packages(self):
        picking_id = False
        for line in self:
            if line.product_id.type == 'pack':
                pack_lines = line.product_id.pack_line_ids
                partner_id = line.order_id.partner_id
                origin = line.order_id.name + '(PACK-%s)' % str(line.product_id.name)
                picking_type = self.env['stock.picking.type'].search([('active', '=', True), ('code', '=', 'outgoing')])

                if picking_type.default_location_src_id:
                    location_id = picking_type.default_location_src_id.id

                if picking_type.default_location_dest_id:
                    location_dest_id = picking_type.default_location_dest_id.id
                elif partner_id:
                    location_dest_id = partner_id.property_stock_customer.id
                else:
                    location_dest_id = self.env['stock.warehouse']._get_partner_locations()[0].id

                datas = {
                    'origin': origin,
                    'picking_type_id': picking_type.id,
                    'min_date': line.order_id.confirmation_date,
                    'group_id': line.order_id.procurement_group_id.id,
                    'partner_id': partner_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'move_type': 'direct'
                }

                if not picking_id:
                    picking_id = self.env['stock.picking'].create(datas)

                if pack_lines:
                    for item in pack_lines:
                        if item.pack_item_id.type == 'product':
                            move = {
                                'picking_id': picking_id.id,
                                'origin': origin,
                                'name': item.pack_item_id.name,
                                'product_id': item.pack_item_id.id,
                                'product_uom': item.uom_id.id,
                                'procure_method': 'make_to_stock',
                                'product_uom_qty': item.quantity,
                                'ordered_qty': item.quantity,
                                'state': 'draft',
                                'partner_id': partner_id.id,
                                'picking_type_id': picking_type.id,
                                'location_id': location_id,
                                'location_dest_id': location_dest_id,
                                'partially_available': False,
                                'propagate': True,
                                'to_refund_so': False
                            }
                            move_id = self.env['stock.move'].create(move)
                            _logger.info(move_id)

    def _delete_pack_picking(self):
        for line in self:
            picking_id = line.order_id.picking_ids
            if line.product_id.type == 'pack':
                if len(picking_id.move_lines) <= 1:
                    if picking_id.move_lines.product_id.type == 'pack':

                        sql = 'delete from stock_move where id = %s' % picking_id.move_lines.id
                        self.env.cr.execute(sql)
                    sql = 'delete from stock_picking where id = %s' % picking_id.id
                    self.env.cr.execute(sql)

                else:
                    for move in picking_id.move_lines:
                        if move.product_id.type == 'pack':
                            sql  = 'delete from stock_move where id = %s' % move.id
                            self.env.cr.execute(sql)

    @api.multi
    def _action_procurement_create(self):
        res = super(WolftrakSaleOrderLine, self)._action_procurement_create()
        self._calculate_packages()

        return res


