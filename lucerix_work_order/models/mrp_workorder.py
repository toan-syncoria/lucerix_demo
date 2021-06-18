# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    timeline_codes_id = fields.Many2one('mrp.timeline.codes', string='Pause Reason')

    def button_start(self):
        self.ensure_one()
        # As button_start is automatically called in the new view
        if self.state in ('done', 'cancel'):
            return True
        if self.product_tracking == 'serial':
            self.qty_producing = 1.0
        #Create a break
        datetime_now = datetime.now()
        mrp_workcenter_productivity_id = self.env['mrp.workcenter.productivity'].search([('workorder_id', '=', self.id), ('user_id', '=', self.env.user.id)], limit=1)
        if mrp_workcenter_productivity_id.id:
            temp = self.env['mrp.workcenter.productivity'].create(
              
                self._prepare_timeline_vals(self.duration, mrp_workcenter_productivity_id.date_end, datetime_now)
            )
            workorder_user_pause_reason = self.env['mrp.workorder.user.pause.reason'].search([('workorder_id', '=', self.id), ('user_id', '=', self.env.user.id)], limit=1)
            if workorder_user_pause_reason:
                temp.write({'timeline_codes_id': workorder_user_pause_reason.last_timeline_codes_id})
        #Create start
        self.env['mrp.workcenter.productivity'].create(
            self._prepare_timeline_vals(self.duration, datetime_now)
        )
        if self.production_id.state != 'progress':
            self.production_id.write({
                'date_start': datetime.now(),
            })
        if self.state == 'progress':
            return True
        start_date = datetime.now()
        vals = {
            'state': 'progress',
            'date_start': start_date,
        }
        if not self.leave_id:
            leave = self.env['resource.calendar.leaves'].create({
                'name': self.display_name,
                'calendar_id': self.workcenter_id.resource_calendar_id.id,
                'date_from': start_date,
                'date_to': start_date + relativedelta(minutes=self.duration_expected),
                'resource_id': self.workcenter_id.resource_id.id,
                'time_type': 'other'
            })
            vals['leave_id'] = leave.id
            return self.write(vals)
        else:
            if self.date_planned_start > start_date:
                vals['date_planned_start'] = start_date
            if self.date_planned_finished and self.date_planned_finished < start_date:
                vals['date_planned_finished'] = start_date
            return self.write(vals)

    def button_pending(self):
        self.action_add_pause_reason()
        return True

    def action_add_pause_reason(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp_workorder.additional.pause.reason',
            'views': [[self.env.ref('lucerix_work_order.view_mrp_workorder_additional_pause_reason_wizard').id, 'form']],
            'name': _('Add Pause Reason'),
            'target': 'new',
            'context': {
            }
        }

class MrpProductionWorkcenterLineTime(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    timeline_codes_id = fields.Many2one('mrp.timeline.codes', string='Pause Reason')
    break_duration = fields.Float('Break Duration', compute='_compute_duration', store=True)

    @api.depends('date_end', 'date_start')
    def _compute_duration(self):
        for blocktime in self:
            if not blocktime.timeline_codes_id:
                if blocktime.date_end:
                    d1 = fields.Datetime.from_string(blocktime.date_start)
                    d2 = fields.Datetime.from_string(blocktime.date_end)
                    diff = d2 - d1
                    if (blocktime.loss_type not in ('productive', 'performance')) and blocktime.workcenter_id.resource_calendar_id:
                        r = blocktime.workcenter_id._get_work_days_data_batch(d1, d2)[blocktime.workcenter_id.id]['hours']
                        blocktime.duration = round(r * 60, 2)
                    else:
                        blocktime.duration = round(diff.total_seconds() / 60.0, 2)
                else:
                    blocktime.duration = 0.0
            else:
                if blocktime.date_end:
                    d1 = fields.Datetime.from_string(blocktime.date_start)
                    d2 = fields.Datetime.from_string(blocktime.date_end)
                    diff = d2 - d1
                    if (blocktime.loss_type not in ('productive', 'performance')) and blocktime.workcenter_id.resource_calendar_id:
                        r = blocktime.workcenter_id._get_work_days_data_batch(d1, d2)[blocktime.workcenter_id.id]['hours']
                        blocktime.break_duration = round(r * 60, 2)
                    else:
                        blocktime.break_duration = round(diff.total_seconds() / 60.0, 2)
                else:
                    blocktime.break_duration = 0.0