from odoo import models, api, fields, _
from datetime import datetime, time, timedelta
import calendar
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import time as time_module  # Rename to avoid conflict
import babel
import logging
from odoo.tools import misc

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = "hr.payslip"
    overtime_ids = fields.Many2many("overtime.calculator")
    total_day_of_month = fields.Float(
        string="Total Day of Month",
        store=True,
        compute="_compute_total_day_of_month",
        readonly=False,
    )
    selected_day = fields.Float(
        string="Selected Days",
        store=True,
        compute="_compute_total_day_of_month",
        readonly=False,
    )

    def get_contract(self, employee, date_from, date_to):
        """
        Enhanced contract retrieval with better date handling
        """
        # Convert string dates to date objects for proper comparison
        if isinstance(date_from, str):
            date_from = fields.Date.from_string(date_from)
        if isinstance(date_to, str):
            date_to = fields.Date.from_string(date_to)

        clause_1 = ["&", ("date_end", "<=", date_to), ("date_end", ">=", date_from)]
        clause_2 = ["&", ("date_start", "<=", date_to), ("date_start", ">=", date_from)]
        clause_3 = [
            "&",
            ("date_start", "<=", date_from),
            "|",
            ("date_end", "=", False),
            ("date_end", ">=", date_to),
        ]

        clause_final = (
            [("employee_id", "=", employee.id), ("state", "=", "open"), "|", "|"]
            + clause_1
            + clause_2
            + clause_3
        )

        contracts = self.env["hr.contract"].search(clause_final)

        # Additional validation: ensure contract is active during the entire period
        valid_contracts = []
        for contract in contracts:
            contract_start = contract.date_start
            contract_end = contract.date_end or date_to

            # Check if contract covers the entire payslip period
            if contract_start <= date_from and contract_end >= date_to:
                valid_contracts.append(contract.id)
            else:
                _logger.warning(
                    f"Contract {contract.name} doesn't fully cover payslip period"
                )

        return valid_contracts

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        Enhanced worked days calculation with proper leave handling
        """
        res = []

        for contract in contracts.filtered(lambda c: c.resource_calendar_id):
            try:
                # Convert to datetime for proper calculation
                day_from = datetime.combine(
                    fields.Date.from_string(date_from), time.min
                )  # Use datetime.time
                day_to = datetime.combine(
                    fields.Date.from_string(date_to), time.max
                )  # Use datetime.time

                # Get employee and calendar
                employee = contract.employee_id
                calendar = contract.resource_calendar_id

                if not calendar:
                    _logger.warning(f"No calendar found for contract {contract.name}")
                    continue

                # Calculate total working days in period
                total_work_data = employee._get_work_days_data(
                    day_from,
                    day_to,
                    calendar=calendar,
                    compute_leaves=False,  # Get total possible working days
                )

                # Calculate actual worked days (excluding leaves)
                actual_work_data = employee._get_work_days_data(
                    day_from,
                    day_to,
                    calendar=calendar,
                    compute_leaves=True,  # Exclude leaves
                )

                # Calculate leave details
                leaves = {}
                leave_days = total_work_data["days"] - actual_work_data["days"]
                leave_hours = total_work_data["hours"] - actual_work_data["hours"]

                # Get detailed leave information
                leave_types = self._get_leave_details(
                    employee, day_from, day_to, calendar
                )

                # Normal working days (actual worked)
                attendances = {
                    "name": _("Worked Days"),
                    "sequence": 1,
                    "code": "WORK100",
                    "number_of_days": actual_work_data["days"],
                    "number_of_hours": actual_work_data["hours"],
                    "contract_id": contract.id,
                }
                res.append(attendances)

                # Add leave lines
                for leave_type, details in leave_types.items():
                    leave_line = {
                        "name": details["name"],
                        "sequence": 5,
                        "code": details["code"],
                        "number_of_days": details["days"],
                        "number_of_hours": details["hours"],
                        "contract_id": contract.id,
                    }
                    res.append(leave_line)

                _logger.info(
                    f"Worked days calculation: Total={total_work_data['days']}, Worked={actual_work_data['days']}, Leaves={leave_days}"
                )

            except Exception as e:
                _logger.error(
                    f"Error calculating worked days for contract {contract.name}: {str(e)}"
                )
                # Fallback: create basic worked days line
                res.append(
                    {
                        "name": _("Worked Days"),
                        "sequence": 1,
                        "code": "WORK100",
                        "number_of_days": 0.0,
                        "number_of_hours": 0.0,
                        "contract_id": contract.id,
                    }
                )

        return res

    def _get_leave_details(self, employee, day_from, day_to, calendar):
        """
        Get detailed leave information by type
        """
        leaves = {}

        try:
            # Get all leaves in the period
            leave_records = self.env["hr.leave"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("state", "=", "validate"),
                    ("date_from", "<=", day_to),
                    ("date_to", ">=", day_from),
                ]
            )

            for leave in leave_records:
                leave_type = leave.holiday_status_id
                leave_code = leave_type.code or "LEAVE"

                if leave_code not in leaves:
                    leaves[leave_code] = {
                        "name": leave_type.name,
                        "code": leave_code,
                        "days": 0.0,
                        "hours": 0.0,
                    }

                # Calculate leave duration in working days
                leave_duration = employee._get_work_days_data(
                    max(day_from, leave.date_from),
                    min(day_to, leave.date_to),
                    calendar=calendar,
                    compute_leaves=False,
                )

                leaves[leave_code]["days"] += leave_duration["days"]
                leaves[leave_code]["hours"] += leave_duration["hours"]

        except Exception as e:
            _logger.error(f"Error getting leave details: {str(e)}")

        return leaves

    def compute_sheet(self):
        """
        Enhanced compute_sheet with better error handling and validation
        """
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            try:
                # Validate inputs
                if not payslip.employee_id:
                    raise ValidationError(
                        _("Employee is required for payslip computation")
                    )

                if not payslip.date_from or not payslip.date_to:
                    raise ValidationError(
                        _("Date range is required for payslip computation")
                    )

                # Generate payslip number
                number = payslip.number or self.env["ir.sequence"].next_by_code(
                    "salary.slip"
                )

                # Delete old payslip lines
                payslip.line_ids.unlink()

                # Get contracts
                contract_ids = payslip.contract_id.ids or self.get_contract(
                    payslip.employee_id, payslip.date_from, payslip.date_to
                )

                if not contract_ids:
                    raise ValidationError(
                        _("No valid contract found for employee %s in period %s to %s")
                        % (payslip.employee_id.name, payslip.date_from, payslip.date_to)
                    )

                # Compute worked days
                contracts = self.env["hr.contract"].browse(contract_ids)
                worked_days_line_ids = self.get_worked_day_lines(
                    contracts, payslip.date_from, payslip.date_to
                )

                # Update worked days lines
                payslip.worked_days_line_ids = [(5, 0, 0)]  # Clear existing
                for line in worked_days_line_ids:
                    payslip.worked_days_line_ids += payslip.worked_days_line_ids.new(
                        line
                    )

                # Compute inputs
                input_lines = self.get_inputs(
                    contracts, payslip.date_from, payslip.date_to
                )
                _logger.info(payslip.input_line_ids)
                payslip.input_line_ids = [(5, 0, 0)]
                for line in input_lines:
                    payslip.input_line_ids += payslip.input_line_ids.new(line)

                _logger.info(payslip.input_line_ids)

                # Compute salary lines
                lines = [
                    (0, 0, line)
                    for line in self._get_payslip_lines(contract_ids, payslip.id)
                ]
                payslip.write(
                    {
                        "line_ids": lines,
                        "number": number,
                    }
                )

                _logger.info(
                    f"Successfully computed payslip {number} for {payslip.employee_id.name} "
                )

            except Exception as e:
                _logger.error(
                    f"Error computing payslip for {payslip.employee_id.name}: {str(e)}"
                )
                raise ValidationError(_("Error computing payslip: %s") % str(e))

        return res

    @api.onchange("employee_id", "date_from", "date_to")
    def onchange_employee(self):
        """
        Enhanced onchange with better date validation and contract handling
        """
        if not self.employee_id or not self.date_from or not self.date_to:
            return

        try:
            employee = self.employee_id
            date_from = self.date_from
            date_to = self.date_to

            # Validate date range
            if date_from > date_to:
                raise ValidationError(_("Date From cannot be after Date To"))

            # Set payslip name
            ttyme = datetime.combine(
                fields.Date.from_string(date_from), time.min
            )  # Use datetime.time
            locale = self.env.context.get("lang") or "en_US"
            self.name = _("Salary Slip of %s for %s") % (
                employee.name,
                misc.ustr(
                    babel.dates.format_date(date=ttyme, format="MMMM-y", locale=locale)
                ),
            )
            self.company_id = employee.company_id

            # Get contract
            if not self.env.context.get("contract") or not self.contract_id:
                contract_ids = self.get_contract(employee, date_from, date_to)
                if not contract_ids:
                    raise ValidationError(
                        _("No valid contract found for the selected period")
                    )
                self.contract_id = self.env["hr.contract"].browse(contract_ids[0])

            if not self.contract_id.struct_id:
                raise ValidationError(_("No salary structure defined for the contract"))

            self.struct_id = self.contract_id.struct_id

            # Compute worked days and inputs
            contracts = self.env["hr.contract"].browse([self.contract_id.id])

            # Worked days
            worked_days_line_ids = self.get_worked_day_lines(
                contracts, date_from, date_to
            )
            worked_days_lines = self.worked_days_line_ids.browse([])
            for r in worked_days_line_ids:
                worked_days_lines += worked_days_lines.new(r)
            self.worked_days_line_ids = worked_days_lines

            # Inputs
            if contracts:
                input_line_ids = self.get_inputs(contracts, date_from, date_to)
                input_lines = self.input_line_ids.browse([])
                for r in input_line_ids:
                    input_lines += input_lines.new(r)
                self.input_line_ids = input_lines

        except Exception as e:
            # Show error to user but don't break the UI
            _logger.warning(f"Error in onchange_employee: {str(e)}")
            return {"warning": {"title": _("Validation Error"), "message": str(e)}}

    def get_inputs(self, contract_ids, date_from, date_to):
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)

        contract_obj = self.env["hr.contract"]
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id

        # -----------------------------
        # LOAN HANDLING
        # -----------------------------
        try:
            loan_obj = self.env["hr.loan"].search(
                [("employee_id", "=", emp_id.id), ("state", "=", "approve")]
            )

            for loan in loan_obj:
                for loan_line in loan.loan_lines:
                    if (date_from <= loan_line.date <= date_to) and not loan_line.paid:
                        loan_input_exists = False

                        for result in res:
                            if result.get("code") == "LO":
                                result["amount"] = loan_line.amount
                                result["loan_line_id"] = loan_line.id
                                loan_input_exists = True
                                break

                        if not loan_input_exists:
                            res.append(
                                {
                                    "name": _("Loan Deduction"),
                                    "code": "LO",
                                    "amount": loan_line.amount,
                                    "contract_id": contract_ids[0].id,
                                    "loan_line_id": loan_line.id,
                                }
                            )

        except Exception as e:
            _logger.error(f"Error calculating loan inputs: {str(e)}")

        # OVERTIME HANDLING
        try:
            overtime_records = self.env["overtime.calculator"].search(
                [
                    ("employee_id", "=", emp_id.id),
                    ("state", "in", ["in_payment"]),
                    ("start_date", ">=", date_from),
                    ("end_date", "<=", date_to),
                ]
            )

            total_overtime_value = sum(o.value for o in overtime_records)

            if total_overtime_value > 0:
                res.append(
                    {
                        "name": _("Overtime"),
                        "code": "OT100",
                        "amount": total_overtime_value,
                        "contract_id": contract_ids[0].id,
                    }
                )

                _logger.info(
                    f"Employee {emp_id.name} - overtime added to inputs: {total_overtime_value}"
                )

        except Exception as e:
            _logger.error(f"Error calculating overtime inputs: {str(e)}")

        return res

    def action_payslip_done(self):
        """
        Mark payslip as done with validation
        """
        for payslip in self:
            # Validate that computation has been done
            if not payslip.line_ids:
                raise ValidationError(
                    _("Please compute the payslip before marking it as done")
                )

            # Validate worked days
            total_worked_days = sum(
                payslip.worked_days_line_ids.mapped("number_of_days")
            )
            if total_worked_days <= 0:
                raise ValidationError(_("Worked days cannot be zero or negative"))

        # Call super method
        return super(HrPayslip, self).action_payslip_done()
