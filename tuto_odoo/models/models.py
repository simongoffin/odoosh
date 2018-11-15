# -*- coding: utf-8 -*-

from odoo import models, fields, api

STYLE = [('sport', 'sport'),
         ('music', 'musique'),
         ('cinema', 'cinéma'),
         ('politic', 'politique')]

class model_first(models.Model):
    _name = 'model.first'
    _description = 'First Model'

    name = fields.Char("Titre", required=True)
    text = fields.Text("Contenu")
    style = fields.Selection(STYLE, required=True, default='music')
    date = fields.Date('Date', required=True, index=True, default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('validate', 'Validated'),
        ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')

    def action_validate(self):
        self.state = 'validate'

    def action_cancel(self):
        self.state = 'cancel'

    def action_reset(self):
        self.state = 'draft'

class GoogleAnalytics(models.Model):
    _name = 'model.second'
    _description = 'Google Analytics'

    ga_key = fields.Char('Google Analytics Key')
    ga_client_id = fields.Char('Google Client ID')
    ga_client_secret = fields.Char('Google Client Secret')
    user_id = fields.Many2one('res.users', string="User")
    domain = fields.Char('Domain')
    is_configurated = fields.Boolean(compute='_is_configurated', string='Configurated')

    @api.multi
    def _is_configurated(self):
        for rec in self:
            rec.is_configurated = rec.ga_key and rec.ga_client_id and rec.ga_client_secret and rec.domain and True

