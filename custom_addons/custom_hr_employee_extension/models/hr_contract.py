from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    employee_dob = fields.Date(
        string='Date of Birth',
        related='employee_id.birthday',
        store=False,
        readonly=False,
    )