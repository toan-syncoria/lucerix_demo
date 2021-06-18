# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields


class MrpWorkorderAdditionalPauseReason(models.TransientModel):
    _name = "mrp_workorder.additional.pause.reason"
    _description = "Additional Pause Reason"

    timeline_codes_id = fields.Many2one('mrp.timeline.codes', string='Pause Reason', required=True)
    workorder_id = fields.Many2one(
        'mrp.workorder', required=True,
        default=lambda self: self.env.context.get('active_id', None),
    )

    def add_pause_reason(self):
        wo = self.workorder_id
        workorder_user_pause_reason = self.env['mrp.workorder.user.pause.reason'].search([('workorder_id', '=', wo.id), ('user_id', '=', self.env.user.id)], limit=1)
        if workorder_user_pause_reason:
            workorder_user_pause_reason.last_timeline_codes_id = self.timeline_codes_id
        else:
            self.env['mrp.workorder.user.pause.reason'].create({
                'workorder_id': wo.id,
                'user_id': self.env.user.id,
                'last_timeline_codes_id': self.timeline_codes_id.id,
            })
        wo.end_previous()
        return True

class MrpWorkorderUserpauseReason(models.Model):
    _name = 'mrp.workorder.user.pause.reason'

    workorder_id = fields.Many2one('mrp.workorder')
    user_id = fields.Many2one('res.users')
    last_timeline_codes_id = fields.Many2one('mrp.timeline.codes')