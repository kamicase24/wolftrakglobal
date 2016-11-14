import time
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv

from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import UserError

class wolftrakcontract(osv.osv):
	_name = 'hr.contract'
	_inherit = 'hr.contract'

    @api.cr_uid_ids_context
    def get_all_structures(self, cr, uid, contract_ids, context=None):
        """
        @param contract_ids: list of contracts
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first, then first level children and so on) and without duplicata
        """
        structure_ids = [contract.struct_id.id for contract in self.browse(cr, uid, contract_ids, context=context) if contract.struct_id]
        if not structure_ids:
            return list(set(self.pool.get('hr.payroll.structure')._get_parent_structure(cr, uid, structure_ids, context=context)))
        return list(set(self.pool.get('hr.payroll.structure')._get_parent_structure(cr, uid, structure_ids, context=context)))

