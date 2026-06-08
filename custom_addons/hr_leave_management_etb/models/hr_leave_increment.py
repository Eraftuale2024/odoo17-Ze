from odoo import models, fields, api


class HrLeaveIncrementRule(models.Model):
    """
    Defines the service-period-based leave increment rules.
    E.g.: After 5 years of service, employee gets +5 extra leave days.
    """
    _name = 'hr.leave.increment.rule'
    _description = 'Leave Increment Rule by Service Period'
    _order = 'years_of_service asc'

    name = fields.Char(string='Rule Name', required=True)
    years_of_service = fields.Integer(
        string='Years of Service (From)',
        required=True,
        help='Minimum years of service to qualify for this increment.'
    )
    additional_days = fields.Float(
        string='Additional Leave Days',
        required=True,
        help='Number of extra leave days granted on top of the base entitlement.'
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_years_of_service', 'unique(years_of_service)',
         'A rule for this years-of-service threshold already exists.'),
    ]