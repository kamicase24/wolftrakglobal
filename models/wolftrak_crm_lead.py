# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError


class LeadWolftrak(models.Model):
    _inherit = "crm.lead"

    def update_fields(self):
        if self.partner_id.email:
            self.email_from = self.partner_id.email
        if self.partner_id.phone:
            self.phone = self.partner_id.phone
