# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from bs4 import BeautifulSoup
import requests


class WolftrakCurrencyRate(models.Model):
    _name = "res.currency.rate"
    _inherit = "res.currency.rate"

    # rate = fields.Float(default=lambda self: self.env['wolftrak.tools'].default_ex_rate_2())
