# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.project_com.tests.test_access_rights import TestPortalProjectBase
from odoo.exceptions import AccessError
from odoo.tools import mute_logger


class TestPortalProject(TestPortalProjectBase):
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_portal_project_com_access_rights(self):
        pigs = self.project_com_pigs
        pigs.write({'privacy_visibility': 'portal'})

        # Do: Alfred reads project_com -> ok (employee ok public)
        pigs.sudo(self.user_project_comuser).read(['user_id'])
        # Test: all project_com tasks visible
        tasks = self.env['project_com.task'].sudo(self.user_project_comuser).search([('project_com_id', '=', pigs.id)])
        self.assertEqual(tasks, self.task_1 | self.task_2 | self.task_3 | self.task_4 | self.task_5 | self.task_6,
                         'access rights: project_com user should see all tasks of a portal project_com')

        # Do: Bert reads project_com -> crash, no group
        self.assertRaises(AccessError, pigs.sudo(self.user_noone).read, ['user_id'])
        # Test: no project_com task searchable
        self.assertRaises(AccessError, self.env['project_com.task'].sudo(self.user_noone).search, [('project_com_id', '=', pigs.id)])

        # Data: task follower
        pigs.sudo(self.user_project_commanager).message_subscribe(partner_ids=[self.user_portal.partner_id.id])
        self.task_1.sudo(self.user_project_comuser).message_subscribe(partner_ids=[self.user_portal.partner_id.id])
        self.task_3.sudo(self.user_project_comuser).message_subscribe(partner_ids=[self.user_portal.partner_id.id])
        # Do: Chell reads project_com -> ok (portal ok public)
        pigs.sudo(self.user_portal).read(['user_id'])
        # Do: Donovan reads project_com -> ko (public ko portal)
        self.assertRaises(AccessError, pigs.sudo(self.user_public).read, ['user_id'])
        # Test: no access right to project_com.task
        self.assertRaises(AccessError, self.env['project_com.task'].sudo(self.user_public).search, [])
        # Data: task follower cleaning
        self.task_1.sudo(self.user_project_comuser).message_unsubscribe(partner_ids=[self.user_portal.partner_id.id])
        self.task_3.sudo(self.user_project_comuser).message_unsubscribe(partner_ids=[self.user_portal.partner_id.id])
