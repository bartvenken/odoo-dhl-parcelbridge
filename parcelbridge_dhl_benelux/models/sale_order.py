from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_delivery_methods(self):
        """Drop DHL Parcel carriers whose recipient restriction does not
        match the shipping partner's consumer/business status. Mirrors
        the backend Add-Shipping wizard filter so the same carrier set is
        offered everywhere.

        Method is defined by `website_sale`; if that module is not
        installed the call has no caller anyway, but the super() lookup
        would raise - guarded with try/except so an install of just
        `parcelbridge_dhl_benelux + stock_delivery` on a backend-only Odoo
        stays loadable."""
        try:
            carriers = super()._get_delivery_methods()
        except AttributeError:
            return self.env["delivery.carrier"]
        partner = self.partner_shipping_id or self.partner_id
        wanted = "business" if partner.is_company else "consumer"
        return carriers.filtered(
            lambda c: c.delivery_type != "dhlparcel"
                      or not c.dhlparcel_recipient_restriction
                      or c.dhlparcel_recipient_restriction == wanted
        )
