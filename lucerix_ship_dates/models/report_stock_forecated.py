# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, models
from odoo.tools import float_is_zero, format_datetime, format_date, float_round



class ReplenishmentReport(models.AbstractModel):
    _inherit = 'report.stock.report_product_product_replenishment'
    
    def is_same_kit(self, parent, child):
        boms_of_parent = self.env['mrp.bom'].search(['|', ('product_id', '=', parent.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', parent.product_tmpl_id.id)])
        flag = False
        for bom in boms_of_parent:
            for line in bom.bom_line_ids:
                if line.product_id.id == child.id:
                    flag =  True
        return flag

    def get_delivery_date_so(self, product, move_out=None, move_in=None):
        timezone = self._context.get('tz')
        if move_out:
            if "sale.order" in type(move_out._get_source_document()).__name__:
                so = move_out._get_source_document()
                for line in so.order_line:
                    if line.product_id == product or self.is_same_kit(line.product_id, product):
                        return format_datetime(self.env, line.commitment_date, timezone, dt_format=False)
            else:
                return format_datetime(self.env, move_out.date, timezone, dt_format=False)
        if move_in:
            if "purchase.order" in type(move_in._get_source_document()).__name__:
                po = move_in._get_source_document()
                for line in po.order_line:
                    if line.product_id == product or self.is_same_kit(line.product_id, product):
                        return format_datetime(self.env, line.date_planned, timezone, dt_format=False)
            else:
                return format_datetime(self.env, move_in.date, timezone, dt_format=False)

    def _prepare_report_line(self, quantity, move_out=None, move_in=None, replenishment_filled=True, product=False, reservation=False):
        timezone = self._context.get('tz')
        product = product or (move_out.product_id if move_out else move_in.product_id)
        is_late = move_out.date < move_in.date if (move_out and move_in) else False
        return {
            'document_in': move_in._get_source_document() if move_in else False,
            'document_out': move_out._get_source_document() if move_out else False,
            'product': {
                'id': product.id,
                'display_name': product.display_name
            },
            'replenishment_filled': replenishment_filled,
            'uom_id': product.uom_id,
            'receipt_date': self.get_delivery_date_so(product, move_in = move_in) if move_in else False,
            'delivery_date': self.get_delivery_date_so(product, move_out = move_out) if move_out else False,
            'is_late': is_late,
            'quantity': float_round(quantity, precision_rounding=product.uom_id.rounding),
            'move_out': move_out,
            'move_in': move_in,
            'reservation': reservation,
        }