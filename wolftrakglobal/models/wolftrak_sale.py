from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class wolftraksale(models.Model):
	_name = "sale.order"
	_inherit = "sale.order"

	tasa_cambio = fields.Float(string='Tasa de Cambio del dia', digits=(1,4))