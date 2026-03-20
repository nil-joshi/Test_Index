{
    "name": "Hospital Management",
    "version": "1.1.0",
    "author": "Training",
    "maintainer": "Training",
    "website": "https://www.odoo.com",
    "category": "Services",
    "summary": "Manage patients and appointments in a lightweight hospital workflow",
    "description": """
Hospital Management
===================

This module provides a compact hospital workflow with:
- Patient registration
- Appointment scheduling
- Status management
- Calendar and search views
    """,
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/hospital_sequence.xml",
        "views/hospital_patient_views.xml",
        "views/hospital_appointment_views.xml",
        "views/hospital_management_views.xml",
    ],
    "images": ["static/description/icon.png"],
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
