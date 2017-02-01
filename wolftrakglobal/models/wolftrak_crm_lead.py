# -*- coding: utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons.base.res.res_partner import FormatAddress

class crm_lead(FormatAddress, models.Model):
    _name = "crm.lead"
    _inherit = "crm.lead"

    call_duration = fields.float(string='Duracion de la Llamada')

    def log_next_activity_done(self, cr, uid, ids, context=None, next_activity_name=False):

        to_clear_ids = []
        for lead in self.browse(cr, uid, ids, context=context):
            if not lead.next_activity_id:
                continue
            body_html = """<div><b>${object.next_activity_id.name}</b></div>
%if object.title_action:
<div>${object.title_action}</div>
<div>Duración de llamada: ${object.call_duration}0</div>
%endif"""
            body_html = self.pool['mail.template'].render_template(cr, uid, body_html, 'crm.lead', lead.id, context=context)
            msg_id = lead.message_post(body_html, subtype_id=lead.next_activity_id.subtype_id.id)
            to_clear_ids.append(lead.id)
            self.write(cr, uid, [lead.id], {'last_activity_id': lead.next_activity_id.id}, context=context)

            msg_id.write({'call_duration':lead.call_duration})

            lead.call_duration = 0.0

        if to_clear_ids:
            self.cancel_next_activity(cr, uid, to_clear_ids, context=context)
        return True