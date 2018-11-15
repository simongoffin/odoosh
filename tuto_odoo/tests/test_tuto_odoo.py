# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo.tests import common

from datetime import date, datetime
from dateutil import relativedelta

class Test_tuto_odoo(common.TransactionCase):

    def setUp(self):
        """*****setUp*****"""
        super(Test_tuto_odoo, self).setUp()
        self.record = self.env['model.first'].create({
            'name': 'Nom',
            'text': 'contenu',
            'style': 'music'
            })

    def test_00_tuto_odoo(self):
        self.assertEqual(self.record.state, 'draft')
        self.record.action_validate()
        self.assertEqual(self.record.state, 'validate')
        self.record.action_cancel()
        self.assertEqual(self.record.state, 'cancel')
        self.record.action_reset()
        self.assertEqual(self.record.state, 'draft')
