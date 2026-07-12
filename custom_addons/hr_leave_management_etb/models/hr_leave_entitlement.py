from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date


class HrLeaveEntitlement(models.Model):
    _name = 'hr.leave.entitlement'
    _description = 'Employee Leave Entitlement'
    _rec_name = 'display_name'
    _order = 'year desc, employee_id asc'

    # ── Basic Fields ─────────────────────────────────────────────────────────────

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, ondelete='cascade',
        index=True
    )
    year = fields.Integer(
        string='Leave Year', required=True,
        default=lambda self: date.today().year
    )
    display_name = fields.Char(
        string='Name', compute='_compute_display_name', store=True
    )

    # ── Leave Days ───────────────────────────────────────────────────────────────

    base_leave_days = fields.Float(
        string='Base Annual Leave (Days)', required=True, default=16.0
    )
    increment_days = fields.Float(
        string='Service Increment (Days)',
        compute='_compute_increment_days', store=True
    )
    total_entitlement = fields.Float(
        string='Total Entitlement (Days)',
        compute='_compute_total_entitlement', store=True
    )
    leave_days_used = fields.Float(
        string='Leave Days Used',
        compute='_compute_leave_usage', store=True
    )
    leave_days_remaining = fields.Float(
        string='Leave Days Remaining',
        compute='_compute_leave_usage', store=True
    )

    # ── Salary & Monetary Fields ─────────────────────────────────────────────────

    salary = fields.Float(
        string='Monthly Salary (ETB)',
        compute='_compute_salary', store=True
    )
    annual_salary = fields.Float(
        string='Annual Salary (ETB)',
        compute='_compute_salary', store=True
    )
    daily_rate = fields.Float(
        string='Daily Rate (ETB)',
        compute='_compute_daily_rate', store=True,
        digits=(16, 4)
    )
    leave_monetary_value = fields.Float(
        string='Total Leave Monetary Value (ETB)',
        compute='_compute_monetary_value', store=True
    )
    remaining_leave_value = fields.Float(
        string='Remaining Leave Value (ETB)',
        compute='_compute_monetary_value', store=True
    )
    used_leave_value = fields.Float(
        string='Used Leave Value (ETB)',
        compute='_compute_monetary_value', store=True
    )

    # ── Service Fields ───────────────────────────────────────────────────────────

    # Joining date picked from the EARLIEST contract date_start
    date_of_joining = fields.Date(
        string='Date of Joining (from Contract)',
        compute='_compute_date_of_joining',
        store=True,
        readonly=True
    )

    years_of_service = fields.Float(
        string='Years of Service (Today)',
        compute='_compute_years_of_service',
        store=True
    )
    years_of_service_at_year = fields.Float(
        string='Years of Service (At Leave Year)',
        compute='_compute_years_of_service',
        store=True
    )
    applicable_increment_rule_id = fields.Many2one(
        'hr.leave.increment.rule',
        string='Applicable Increment Rule',
        compute='_compute_increment_days',
        store=True,
    )

    # ── SQL Constraints ──────────────────────────────────────────────────────────

    _sql_constraints = [
        ('unique_employee_year', 'unique(employee_id, year)',
         'An entitlement record for this employee and year already exists.'),
    ]

    # ── Compute Methods ──────────────────────────────────────────────────────────

    @api.depends('employee_id', 'year')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.employee_id.name} / {rec.year}"
                if rec.employee_id else ''
            )

    @api.depends('employee_id')
    def _compute_date_of_joining(self):
        """
        Pick joining date from the earliest contract date_start.
        Falls back to employee joining_date if no contract exists.
        """
        for rec in self:
            if not rec.employee_id:
                rec.date_of_joining = False
                continue

            # Get the earliest contract (any state) ordered by date_start asc
            earliest_contract = self.env['hr.contract'].search([
                ('employee_id', '=', rec.employee_id.id),
            ], order='date_start asc', limit=1)

            if earliest_contract and earliest_contract.date_start:
                rec.date_of_joining = earliest_contract.date_start
            elif rec.employee_id.joining_date:
                # Fallback to HR employee joining date
                rec.date_of_joining = rec.employee_id.joining_date
            else:
                rec.date_of_joining = False

    @api.depends('employee_id', 'date_of_joining', 'year')
    def _compute_years_of_service(self):
        today = date.today()
        for rec in self:
            joining = rec.date_of_joining

            if not joining:
                rec.years_of_service = 0.0
                rec.years_of_service_at_year = 0.0
                continue

            # ── Years of service as of TODAY
            try:
                delta_today = relativedelta(today, joining)
                rec.years_of_service = round(
                    delta_today.years + delta_today.months / 12.0, 2
                )
            except (ValueError, TypeError):
                rec.years_of_service = 0.0

            # ── Years of service as of Jan 1 of the leave year
            try:
                if rec.year and rec.year >= 1:
                    ref_date = date(rec.year, 1, 1)
                    delta_year = relativedelta(ref_date, joining)
                    yos = delta_year.years + delta_year.months / 12.0
                    # Can't have negative years of service
                    rec.years_of_service_at_year = round(max(yos, 0.0), 2)
                else:
                    rec.years_of_service_at_year = 0.0
            except (ValueError, TypeError):
                rec.years_of_service_at_year = 0.0

    @api.depends('years_of_service_at_year')
    def _compute_increment_days(self):
        """
        Two-tier increment logic:
        1. Check hr.leave.increment.rule for custom rules (priority).
        2. Fallback: 1 extra day per full year of service.
           e.g. joined 2022, leave year 2026 = 4 full years = +4 days
                total = 16 (base) + 4 = 20 days
        """
        rules = self.env['hr.leave.increment.rule'].search(
            [('active', '=', True)], order='years_of_service desc'
        )
        for rec in self:
            service_years = rec.years_of_service_at_year
            matched = self.env['hr.leave.increment.rule']

            for rule in rules:
                if service_years >= rule.years_of_service:
                    matched = rule
                    break

            if matched:
                rec.applicable_increment_rule_id = matched
                rec.increment_days = matched.additional_days
            else:
                # 1 day increment per full year of service
                rec.applicable_increment_rule_id = False
                rec.increment_days = float(int(service_years))

    @api.depends('base_leave_days', 'increment_days')
    def _compute_total_entitlement(self):
        for rec in self:
            rec.total_entitlement = rec.base_leave_days + rec.increment_days

    @api.depends('employee_id', 'year', 'total_entitlement')
    def _compute_leave_usage(self):
        HrLeave = self.env['hr.leave']
        for rec in self:
            if not rec.employee_id or not rec.year or rec.year < 1:
                rec.leave_days_used = 0.0
                rec.leave_days_remaining = rec.total_entitlement
                continue
            try:
                year_start = date(rec.year, 1, 1)
                year_end = date(rec.year, 12, 31)
            except (ValueError, TypeError):
                rec.leave_days_used = 0.0
                rec.leave_days_remaining = rec.total_entitlement
                continue
            leaves = HrLeave.search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'validate'),
                ('date_from', '>=', str(year_start)),
                ('date_from', '<=', str(year_end)),
            ])
            days_used = sum(leaves.mapped('number_of_days'))
            rec.leave_days_used = days_used
            rec.leave_days_remaining = rec.total_entitlement - days_used

    @api.depends('employee_id')
    def _compute_salary(self):
        """Pick salary from the most recent ACTIVE contract."""
        for rec in self:
            if not rec.employee_id:
                rec.salary = 0.0
                rec.annual_salary = 0.0
                continue
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', 'in', ['open', 'pending']),
            ], order='date_start desc', limit=1)
            rec.salary = contract.wage if contract else 0.0
            rec.annual_salary = rec.salary * 12

    @api.depends('annual_salary')
    def _compute_daily_rate(self):
        for rec in self:
            rec.daily_rate = rec.annual_salary / 365.0 if rec.annual_salary else 0.0

    @api.depends('daily_rate', 'total_entitlement', 'leave_days_used', 'leave_days_remaining')
    def _compute_monetary_value(self):
        for rec in self:
            rec.leave_monetary_value = rec.daily_rate * rec.total_entitlement
            rec.used_leave_value = rec.daily_rate * rec.leave_days_used
            rec.remaining_leave_value = rec.daily_rate * rec.leave_days_remaining

    # ── Action ───────────────────────────────────────────────────────────────────

    def action_recompute(self):
        """Manually trigger recomputation of all stored computed fields."""
        for rec in self:
            rec._compute_date_of_joining()
            rec._compute_years_of_service()
            rec._compute_increment_days()
            rec._compute_total_entitlement()
            rec._compute_leave_usage()
            rec._compute_salary()
            rec._compute_daily_rate()
            rec._compute_monetary_value()