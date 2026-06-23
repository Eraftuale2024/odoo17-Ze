from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    tin_no = fields.Char(
        string='TIN Number',
        help='Employee Tax Identification Number'
    )

    pension_no = fields.Char(
        string='Pension Number',
        help='Employee Pension Registration Number'
    )