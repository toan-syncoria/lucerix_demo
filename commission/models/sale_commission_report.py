# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class SalesCommissionReport(models.Model):
    _name = 'sale.commission.reports'
    _description = "Sale Commision"

    date = fields.Datetime(string='Order Date')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    invoice_date = fields.Date(string='Invoice Date')
    partner_id = fields.Many2one('res.partner', string='Customer')
    customer_reference = fields.Char(string='Customer Reference')
    invoice_value = fields.Float(string='Invoice Value')
    merchandise_value = fields.Float(string='Merchandise Value')
    commission_amount = fields.Float(string='Commission Amount')
    commission_percent = fields.Float(string='Commission (%)')
    product_id = fields.Many2one('product.product', string='Product')
    commission_id = fields.Many2one('sale.commission', string='Commission Code')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price')