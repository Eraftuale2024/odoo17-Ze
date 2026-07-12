from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    employee_dob = fields.Date(
        string='Date of Birth',
        related='employee_id.birthday',
        store=False,
        readonly=False,
    )

    max_variable_pay = fields.Float(
        string="Max Variable Pay",
        default=0.0,
        help="Fixed maximum variable pay ceiling for this employee"
    )

    achievement_percent = fields.Float(
        string="Achievement (%)",
        default=0.0,
        help="Achievement percentage this period (0–100)"
    )