# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class MrpTimelineCodes(models.Model):
    _name = 'mrp.timeline.codes'
    _description = "Timeline Codes"

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')

    def name_get(self):
        result = []
        for TimelineCode in self:
            if TimelineCode.code and TimelineCode.name:
                name = '[' + TimelineCode.code + '] ' + TimelineCode.name
                result.append((TimelineCode.id, name))
        return result
