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
