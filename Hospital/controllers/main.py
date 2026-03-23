from werkzeug.utils import redirect
from odoo import http


class HospitalSupportController(http.Controller):

    @http.route("/hospital/request-free-support", type="http", auth="public", website=True, sitemap=False)
    def request_free_support(self, **kwargs):
        return redirect("https://www.aspiresoftserv.com/contact-us", code=302)