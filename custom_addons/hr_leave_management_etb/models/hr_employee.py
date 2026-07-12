from odoo import models, fields, api
from datetime import date

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # This field is required by hr.leave.entitlement
    joining_date = fields.Date(string='Date of Joining')

    leave_entitlement_ids = fields.One2many(
        'hr.leave.entitlement', 'employee_id',
        string='Leave Entitlements'
    )
    leave_entitlement_count = fields.Integer(
        string='Entitlement Records',
        compute='_compute_leave_entitlement_count'
    )
    current_year_entitlement_id = fields.Many2one(
        'hr.leave.entitlement',
        string='Current Year Entitlement',
        compute='_compute_current_year_entitlement',
    )
    current_leave_remaining = fields.Float(
        string='Remaining Leave Days (Current Year)',
        compute='_compute_current_year_entitlement',
    )
    current_leave_remaining_value = fields.Float(
        string='Remaining Leave Value ETB (Current Year)',
        compute='_compute_current_year_entitlement',
    )

    @api.depends('leave_entitlement_ids')
    def _compute_leave_entitlement_count(self):
        for emp in self:
            emp.leave_entitlement_count = len(emp.leave_entitlement_ids)

    @api.depends('leave_entitlement_ids', 'leave_entitlement_ids.leave_days_remaining', 'leave_entitlement_ids.remaining_leave_value')
    def _compute_current_year_entitlement(self):
        current_year = date.today().year
        for emp in self:
            entitlement = emp.leave_entitlement_ids.filtered(lambda e: e.year == current_year)[:1]
            emp.current_year_entitlement_id = entitlement
            emp.current_leave_remaining = entitlement.leave_days_remaining if entitlement else 0.0
            emp.current_leave_remaining_value = entitlement.remaining_leave_value if entitlement else 0.0

    def action_view_leave_entitlements(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} — Leave Entitlements',
            'res_model': 'hr.leave.entitlement',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }