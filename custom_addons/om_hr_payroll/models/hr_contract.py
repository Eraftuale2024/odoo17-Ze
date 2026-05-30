# -*- coding:utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class HrSalaryExchange(models.Model):
    _name = 'hr.salary.exchange.rate'
    _description = 'Salary Exchange Rate'

    currency_id = fields.Many2one('res.currency', related=False, string='Currency')
    exchange_rate = fields.Float(string='Exchange Rate')

    _sql_constraints = [
        ('unique_currency_id', 'unique(currency_id)', 'The currency must be unique.'),
    ]


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',
        help="Defines the frequency of the wage payment.")
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule.")
    currency_id = fields.Many2one('res.currency', related=False,
                                  default=lambda self: self._get_default_currency(), string='Currency')
    hra = fields.Monetary(string='HRA', help="House rent allowance.")
    travel_allowance = fields.Monetary(string="Travel Allowance", help="Travel allowance")
    da = fields.Monetary(string="DA", help="Dearness allowance")
    meal_allowance = fields.Monetary(string="Meal Allowance", help="Meal allowance")
    medical_allowance = fields.Monetary(string="Medical Allowance", help="Medical allowance")
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances")
    type_id = fields.Many2one('hr.contract.type', string="Employee Category",
                              required=True, help="Employee category",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))

    # Project assignments for LOE
    project_line_ids = fields.One2many(
        'hr.contract.project.line',
        'contract_id',
        string="Project Assignments"
    )

    @api.model
    def _get_default_currency(self):
        return self.env.company.currency_id.id

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0


class HrContractAdvantageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    lower_bound = fields.Float('Lower Bound', help="Lower bound authorized by the employer for this advantage")
    upper_bound = fields.Float('Upper Bound', help="Upper bound authorized by the employer for this advantage")
    default_value = fields.Float('Default value for this advantage')


class HrContractProject(models.Model):
    _name = 'hr.contract.project.line'
    _description = "Contract Project Line"
    _rec_name = 'project_id'

    contract_id = fields.Many2one(
        'hr.contract',
        string="Contract",
        required=True,
        ondelete='cascade'
    )
    # percentage = fields.Float('LOE %', required=True, default=100.0)

    rate = fields.Float('Rate', required=True)

    # IMPORTANT: Check what model you actually need
    # Option A: Use project.project (has analytic_account_id)
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True
    )

    # Option B: Use purchase.project but fix the related field
    # project_id = fields.Many2one(
    #     'purchase.project',
    #     string='Project',
    #     required=True
    # )

    # Use computed field instead of related
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        compute='_compute_analytic_account_id',
        store=True
    )

    # Optional: Add date range for LOE changes
    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_end = fields.Date(string='End Date')

    @api.depends('project_id')
    def _compute_analytic_account_id(self):
        """
        Compute analytic account from project
        This handles both project.project and purchase.project
        """
        for rec in self:
            analytic_account = False

            if rec.project_id:
                # Check if project has analytic_account_id
                if hasattr(rec.project_id, 'analytic_account_id') and rec.project_id.analytic_account_id:
                    analytic_account = rec.project_id.analytic_account_id

                # If using purchase.project, you might need to link to project.project
                elif rec.project_id._name == 'purchase.project':
                    # Try to find related project.project
                    related_project = self.env['project.project'].search(
                        [('custom_project_id', '=', rec.project_id.id)],
                        limit=1
                    )
                    if related_project and related_project.analytic_account_id:
                        analytic_account = related_project.analytic_account_id

            rec.analytic_account_id = analytic_account

    @api.model
    def create(self, vals):
        res = super(HrContractProject, self).create(vals)

        # Optional: Create analytic line if needed
        # Only if you're using timesheets
        if hasattr(res, 'contract_id') and res.contract_id.employee_id:
            # Find the actual project.project record
            actual_project = None
            if res.project_id._name == 'project.project':
                actual_project = res.project_id
            elif res.project_id._name == 'purchase.project':
                actual_project = self.env['project.project'].search(
                    [('custom_project_id', '=', res.project_id.id)],
                    limit=1
                )

            if actual_project and actual_project.analytic_account_id:
                try:
                    self.env['account.analytic.line'].create({
                        'employee_id': res.contract_id.employee_id.id,
                        'project_id': actual_project.id,
                        'account_id': actual_project.analytic_account_id.id,
                        'name': f'LOE Allocation: {actual_project.name}'
                    })
                except Exception as e:
                    _logger.warning(f"Could not create analytic line: {e}")

        return res