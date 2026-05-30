# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PayrollLOEValidationWizard(models.TransientModel):
    _name = 'payroll.loe.validation.wizard'
    _description = 'Payroll LOE Validation Wizard'

    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batch', required=True)

    validation_result = fields.Html(string='Validation Result', readonly=True)
    has_errors = fields.Boolean(string='Has Errors', default=False)

    def action_validate(self):
        """
        Validate LOE for all contracts in the payslip batch
        """
        self.ensure_one()

        contracts = self.env['hr.contract'].search([
            ('employee_id', 'in', self.payslip_run_id.slip_ids.mapped('employee_id').ids),
            ('state', '=', 'open')
        ])

        errors = []
        warnings = []

        for contract in contracts:
            if not contract.project_ids:
                errors.append(f"<strong>{contract.employee_id.name}</strong>: No project allocation")
                continue

            total_percentage = sum(contract.project_ids.mapped('percentage'))
            if abs(total_percentage - 100.0) > 0.01:
                errors.append(
                    f"<strong>{contract.employee_id.name}</strong>: "
                    f"Total allocation = {total_percentage:.2f}% (should be 100%)"
                )

            # Check for projects without analytic accounts
            for project_line in contract.project_ids:
                if not project_line.project_id.analytic_account_id:
                    warnings.append(
                        f"<strong>{contract.employee_id.name}</strong>: "
                        f"Project '{project_line.project_id.name}' has no analytic account"
                    )

        # Format results
        result_html = "<h3>LOE Validation Results</h3>"

        if errors:
            result_html += "<h4 style='color: red;'>❌ Errors (Must Fix):</h4><ul>"
            for error in errors:
                result_html += f"<li>{error}</li>"
            result_html += "</ul>"
            self.has_errors = True

        if warnings:
            result_html += "<h4 style='color: orange;'>⚠️ Warnings:</h4><ul>"
            for warning in warnings:
                result_html += f"<li>{warning}</li>"
            result_html += "</ul>"

        if not errors and not warnings:
            result_html += "<h4 style='color: green;'>✅ All validations passed!</h4>"
            result_html += "<p>You can proceed with payroll processing.</p>"

        self.validation_result = result_html

        return {
            'type': 'ir.actions.act_window',
            'name': 'LOE Validation Results',
            'res_model': 'payroll.loe.validation.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }