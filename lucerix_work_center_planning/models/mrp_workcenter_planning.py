# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class MrpWorkcenterPlanning(models.Model):
    _name = 'mrp.workcenter.planning'

    date = fields.Date('Date', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=True)
    workcenter_load = fields.Float('Load', compute="get_load")
    person_minutes = fields.Integer('Person Minutes', index=True)
    user_id = fields.Many2one('res.users', 'Employee')
    week_number = fields.Integer('Week Number', compute="get_week_number", store=True)

    def name_get(self):
        result = []
        for plan in self:
            if plan.user_id:
                name = '[' + plan.workcenter_id.name + '] ' + plan.user_id.name
            else: 
                name = '[' + plan.workcenter_id.name + ']'
            result.append((plan.id, name))
        return result

    @api.depends("date", "workcenter_id")
    def get_load(self):
        self.workcenter_load = 0
        for rec in self:
            workorder_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', rec.workcenter_id.id)])
            for workorder in workorder_obj:
                if fields.Date.from_string(workorder.production_date) == fields.Date.from_string(rec.date):
                    rec.workcenter_load += workorder.duration_expected
    
    @api.depends("date")
    def get_week_number(self):
        self.week_number = 0
        for rec in self:
            if rec.date:
                rec.week_number = rec.date.isocalendar()[1]
            else:
                rec.week_number = 0

    def calculation_person_mins_wkly(self, workcenter_id, week_number):
        print("input)")
        print(workcenter_id)
        print(week_number)
        #Get Total person_minutes by Week in Planning
        total_person_mins_planning = 0
        planning_obj = self.env['mrp.workcenter.planning'].search([('workcenter_id', '=', workcenter_id),
                                                                    ('week_number', '=', week_number)])
        for rec in planning_obj:
            if rec.week_number == week_number:
                total_person_mins_planning += rec.person_minutes
        print(total_person_mins_planning)
        #Get lists object by Week in Real and update person minutes wkly
        workorder_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', workcenter_id),
                                                            ('week_number', '=', week_number), 
                                                            ('state', 'in', ['pending','ready', 'progress'])])
        if len(workorder_obj) > 0:
            person_mins_wkly_calculated = total_person_mins_planning/len(workorder_obj)
            for workorder in workorder_obj:
                workorder.person_mins_wkly = person_mins_wkly_calculated

    def write(self, values):
        old_week_number = ''
        old_workcenter_id = ''
        if values.get('date') and self.date != values.get('date'):
            old_week_number = self.date.isocalendar()[1]
        if values.get('workcenter_id') and self.workcenter_id.id != values.get('workcenter_id'):
            old_workcenter_id = self.workcenter_id.id
        result = super(MrpWorkcenterPlanning, self).write(values)
        
        #Change date same week OR change Person Minutes
        if ((old_week_number != '' and old_week_number == self.week_number and old_workcenter_id == '') 
            or (old_week_number == '' and old_workcenter_id == '')):
            print("11111111")
            self.calculation_person_mins_wkly(self.workcenter_id.id, self.week_number)
            return 
        #Change Date different week
        if (old_week_number != '' and old_week_number != self.week_number and old_workcenter_id == ''):
            print("222222")
            print(old_week_number)
            print(self.week_number)
            self.calculation_person_mins_wkly(self.workcenter_id.id, old_week_number)
            self.calculation_person_mins_wkly(self.workcenter_id.id, self.week_number)
            return 
        #Change Work Center
        if (old_workcenter_id != '' and old_workcenter_id != self.workcenter_id.id and old_week_number == ''):
            print("33333")
            print(old_week_number)
            print(self.week_number)
            self.calculation_person_mins_wkly(old_workcenter_id, self.week_number)
            self.calculation_person_mins_wkly(self.workcenter_id.id, self.week_number)
            return 
        #Change Work Center and date
        # if ( (old_workcenter_id != '' and old_workcenter_id != self.workcenter_id.id) 
            # and (old_week_number != '' and old_week_number != self.week_number) ):
        if (old_workcenter_id != '' and old_week_number != ''):
            print("4444")
            self.calculation_person_mins_wkly(old_workcenter_id, self.week_number)
            self.calculation_person_mins_wkly(old_workcenter_id, old_week_number)
            self.calculation_person_mins_wkly(self.workcenter_id.id, self.week_number)
            self.calculation_person_mins_wkly(self.workcenter_id.id, old_week_number)
            return 
        
        return result
    
    @api.model_create_multi
    def create(self, values):
        result = super(MrpWorkcenterPlanning, self).create(values)
        result.calculation_person_mins_wkly(result.workcenter_id.id, result.week_number)
        return result