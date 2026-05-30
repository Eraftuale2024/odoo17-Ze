# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)
_logger.info("✅ LOE MODULE LOADED - SIMPLE VERSION!")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_loe_distribution(self):
        """
        Simple LOE distribution method
        """
        _logger.info(f"🔍 LOE: _get_loe_distribution called for {self.employee_id.name}")

        distribution = {}

        # Check contract
        if self.contract_id:
            _logger.info(f"  Contract ID: {self.contract_id.id}")

            # Check if project_line_ids exists
            if hasattr(self.contract_id, 'project_line_ids'):
                _logger.info(f"  Has project_line_ids: Yes")
                _logger.info(f"  Number of project lines: {len(self.contract_id.project_line_ids)}")

                for line in self.contract_id.project_line_ids:
                    _logger.info(f"  - Project: {line.project_id.name}, Rate: {line.rate}%")

                    # Get analytic account
                    analytic_account = False
                    if hasattr(line, 'analytic_account_id') and line.analytic_account_id:
                        analytic_account = line.analytic_account_id
                    elif hasattr(line.project_id, 'analytic_account_id') and line.project_id.analytic_account_id:
                        analytic_account = line.project_id.analytic_account_id

                    if analytic_account:
                        distribution[analytic_account.id] = line.rate
                        _logger.info(f"    Analytic: {analytic_account.name}")
                    else:
                        _logger.warning(f"    No analytic account!")
            else:
                _logger.warning("  No project_line_ids attribute!")
        else:
            _logger.warning("  No contract!")

        _logger.info(f"  Final distribution: {distribution}")
        return distribution

    def action_payslip_done(self):
        """
        Override to apply LOE
        """
        _logger.info(f"🎯 LOE: action_payslip_done for {self.employee_id.name}")

        # Test LOE method
        _logger.info(f"  Has LOE method: {hasattr(self, '_get_loe_distribution')}")

        if hasattr(self, '_get_loe_distribution'):
            distribution = self._get_loe_distribution()
            _logger.info(f"  LOE Distribution: {distribution}")

            # Apply to accounting (simple test)
            if distribution:
                _logger.info(f"  ✓ Would apply LOE: {distribution}")
            else:
                _logger.info(f"  ✗ No LOE distribution")
        else:
            _logger.error("  ✗ LOE method missing!")

        # Call parent
        result = super().action_payslip_done()
        return result


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Simple validation method
    def validate_loe_for_payroll(self):
        _logger.info("🔍 LOE Validation called")
        return True