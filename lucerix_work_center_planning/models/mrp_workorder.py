# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class MrpWorkOrderInherit(models.Model):
    _inherit = 'mrp.workorder'
    
    person_mins_wkly = fields.Float('Person Mins Wkly')
    week_number = fields.Integer('Week Number', compute="get_week_number", store=True)

    @api.depends("date_planned_start")
    def get_week_number(self):
        self.week_number = 0
        for rec in self:
            if rec.date_planned_start:
                rec.week_number = rec.date_planned_start.isocalendar()[1]
            else:
                rec.week_number = 0