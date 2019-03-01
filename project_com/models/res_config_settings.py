# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_project_com_forecast = fields.Boolean(string="Forecasts")
    module_hr_timesheet = fields.Boolean(string="Task Logs")
    group_subtask_project_com = fields.Boolean("Sub-tasks", implied_group="project_com.group_subtask_project_com")
    group_project_com_rating = fields.Boolean("Use Rating on Project", implied_group='project_com.group_project_com_rating')
