# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _description = "Hospital Patient"
    _order = "id desc"

    reference = fields.Char(
        string="Patient Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    name = fields.Char(string="Patient Name", required=True)
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
        required=True,
        default="male",
    )
    birth_date = fields.Date(string="Birth Date")
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    blood_group = fields.Selection(
        [
            ("a_pos", "A+"),
            ("a_neg", "A-"),
            ("b_pos", "B+"),
            ("b_neg", "B-"),
            ("ab_pos", "AB+"),
            ("ab_neg", "AB-"),
            ("o_pos", "O+"),
            ("o_neg", "O-"),
        ],
        string="Blood Group",
    )
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    doctor_name = fields.Char(string="Primary Doctor")
    address = fields.Text(string="Address")
    note = fields.Text(string="Notes")
    date_admitted = fields.Date(
        string="Admission Date",
        default=fields.Date.context_today,
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("admitted", "Admitted"),
            ("discharged", "Discharged"),
        ],
        string="Status",
        default="draft",
        required=True,
    )
    active = fields.Boolean(default=True)
    appointment_ids = fields.One2many(
        "hospital.appointment",
        "patient_id",
        string="Appointments",
    )
    appointment_count = fields.Integer(
        string="Appointment Count",
        compute="_compute_appointment_count",
    )

    _sql_constraints = [
        (
            "hospital_patient_reference_unique",
            "unique(reference)",
            "The patient reference must be unique.",
        )
    ]

    @api.depends("birth_date")
    def _compute_age(self):
        today = fields.Date.today()
        for record in self:
            if not record.birth_date:
                record.age = 0
                continue
            years = today.year - record.birth_date.year
            before_birthday = (today.month, today.day) < (
                record.birth_date.month,
                record.birth_date.day,
            )
            record.age = years - int(before_birthday)

    @api.depends("appointment_ids")
    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = len(record.appointment_ids)

    @api.constrains("birth_date", "date_admitted")
    def _check_patient_dates(self):
        today = fields.Date.today()
        for record in self:
            if record.birth_date and record.birth_date > today:
                raise ValidationError(_("Birth date cannot be in the future."))
            if record.birth_date and record.date_admitted and record.birth_date > record.date_admitted:
                raise ValidationError(_("Admission date must be after the birth date."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", _("New")) == _("New"):
                vals["reference"] = (
                    self.env["ir.sequence"].next_by_code("hospital.patient") or _("New")
                )
        return super().create(vals_list)

    def action_admit(self):
        self.write({"state": "admitted"})

    def action_discharge(self):
        self.write({"state": "discharged"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def action_view_appointments(self):
        self.ensure_one()
        action = self.env.ref("Hospital.action_hospital_appointment").read()[0]
        action["domain"] = [("patient_id", "=", self.id)]
        action["context"] = {
            **self.env.context,
            "default_patient_id": self.id,
            "search_default_filter_patient": 1,
        }
        return action


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _description = "Hospital Appointment"
    _order = "appointment_date desc, id desc"

    name = fields.Char(
        string="Appointment Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    patient_id = fields.Many2one(
        "hospital.patient",
        string="Patient",
        required=True,
        ondelete="cascade",
    )
    patient_phone = fields.Char(related="patient_id.phone", string="Patient Phone", store=True)
    doctor_name = fields.Char(string="Doctor", required=True)
    department = fields.Selection(
        [
            ("general", "General Medicine"),
            ("cardiology", "Cardiology"),
            ("dermatology", "Dermatology"),
            ("neurology", "Neurology"),
            ("orthopedic", "Orthopedic"),
            ("pediatrics", "Pediatrics"),
        ],
        string="Department",
        required=True,
        default="general",
    )
    appointment_date = fields.Datetime(
        string="Appointment Date",
        required=True,
        default=fields.Datetime.now,
    )
    priority = fields.Selection(
        [("0", "Low"), ("1", "Medium"), ("2", "High"), ("3", "Urgent")],
        string="Priority",
        default="1",
    )
    symptoms = fields.Text(string="Symptoms")
    diagnosis = fields.Text(string="Diagnosis")
    prescription = fields.Text(string="Prescription")
    note = fields.Text(string="Internal Notes")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    _sql_constraints = [
        (
            "hospital_appointment_name_unique",
            "unique(name)",
            "The appointment reference must be unique.",
        )
    ]

    @api.constrains("appointment_date", "patient_id")
    def _check_appointment_date(self):
        for record in self:
            if not record.appointment_date or not record.patient_id.date_admitted:
                continue
            if record.appointment_date.date() < record.patient_id.date_admitted:
                raise ValidationError(_("Appointment date cannot be earlier than the patient admission date."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("hospital.appointment") or _("New")
                )
        return super().create(vals_list)

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})
