# -*- coding: utf-8 -*-

from email.header import decode_header
from email.utils import formataddr
import logging

from openerp import _, api, fields, models, SUPERUSER_ID
from openerp import tools
from openerp.exceptions import UserError, AccessError
from openerp.osv import expression


_logger = logging.getLogger(__name__)


class Message(models.Model):
    _name = 'mail.message'
    _inherit = 'mail.message'

    call_duration = fields.Float(string='Duracion de la llamada')