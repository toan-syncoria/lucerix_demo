# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime, date, timedelta

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    customer_req_date = fields.Date('Customer Req Date', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    # commitment_date = fields.Datetime('Delivery Date', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    commitment_date = fields.Datetime('Delivery Date')

    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        if 'commitment_date' in vals:
            self.order_id.action_recalculate_delivery_date()
            #update Stock.Move
            # new_date = fields.Datetime.to_datetime(vals['commitment_date'])
            # self._update_move_date_deadline(new_date)
        return result

    @api.onchange("commitment_date")
    def onchange_commitment_date(self):
        if self.order_id.picking_ids:
            for picking in self.order_id.picking_ids:
                if picking.state not in ['cancel', 'done']:
                    stock_move_obj = self.env['stock.move'].search([('picking_id', '=', picking._origin.id)])
                    for move in stock_move_obj:
                        if move.product_id.id == self.product_id.id:
                            print("MATCHHHH")
                            print(move.product_id.id)
                            move.date_deadline = self.commitment_date

    # def _update_move_date_deadline(self, new_date):
    #     """ Updates corresponding move picking line deadline dates that are not yet completed. """
    #     moves_to_update = self.move_ids.filtered(lambda m: m.state not in ('done', 'cancel'))
    #     for move in moves_to_update:
    #         move.date_deadline = new_date

    def _prepare_procurement_values(self, group_id=False):
        print("inherit _prepare_procurement_values")
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        # Use the delivery date if there is else use date_order and lead time
        # date_deadline = self.order_id.commitment_date or (self.order_id.date_order + timedelta(days=self.customer_lead or 0.0))
        date_deadline = self.commitment_date or (self.order_id.date_order + timedelta(days=self.customer_lead or 0.0))
        date_planned = date_deadline - timedelta(days=self.order_id.company_id.security_lead)
        values.update({
            'group_id': group_id,
            'sale_line_id': self.id,
            'date_planned': date_planned,
            'date_deadline': date_deadline,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
            'product_description_variants': self._get_sale_order_line_multiline_description_variants(),
            'company_id': self.order_id.company_id,
        })
        return values

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'


    commitment_date = fields.Datetime('Delivery Date', index=True, copy=False, store=True, compute='_compute_commitment_date',
                                      states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                                      help="This is the delivery date promised to the customer. "
                                           "If set, the delivery order will be scheduled based on "
                                           "this date rather than product lead times.")
    def write(self, values):
        result = super(SaleOrderInherit, self).write(values)

        if values.get('commitment_date'):
            print("SO inherit WRITE commitnemt_date")
            if self.picking_ids:
                for picking in self.picking_ids:
                    if picking.state not in ['cancel', 'done']:
                        stock_move_obj = self.env['stock.move'].search([('picking_id', '=', picking._origin.id)])
                        for move in stock_move_obj:
                            for line in self.order_line:
                                if move.product_id.id == line.product_id.id:
                                    move.date_deadline = line.commitment_date

    def action_recalculate_delivery_date(self):
        temp = [0]
        for rec in self.order_line:
            if rec.commitment_date and rec.invoice_status == 'no':
                temp.append(rec.commitment_date)
        temp.pop(0)
        if len(temp) > 0:
            self.commitment_date = min(temp)
        return True


    @api.depends('order_line.commitment_date')
    def _compute_commitment_date(self):
        """ commitment_date = the earliest commitment_date across all order lines. """
        for order in self:
            dates_list = order.order_line.filtered(lambda x: not x.display_type and x.commitment_date).mapped('commitment_date')
            if dates_list:
                order.commitment_date = fields.Datetime.to_string(min(dates_list))
            else:
                order.commitment_date = False