# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.project_com.tests.test_project_com_base import TestProjectBase
from odoo.exceptions import AccessError
from odoo.tools import mute_logger


class TestPortalProjectBase(TestProjectBase):

    def setUp(self):
        super(TestPortalProjectBase, self).setUp()
        self.user_noone = self.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True}).create({
            'name': 'Noemie NoOne',
            'login': 'noemie',
            'email': 'n.n@example.com',
            'signature': '--\nNoemie',
            'notification_type': 'email',
            'groups_id': [(6, 0, [])]})

        self.task_3 = self.env['project_com.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test3', 'user_id': self.user_portal.id, 'project_com_id': self.project_com_pigs.id})
        self.task_4 = self.env['project_com.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test4', 'user_id': self.user_public.id, 'project_com_id': self.project_com_pigs.id})
        self.task_5 = self.env['project_com.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test5', 'user_id': False, 'project_com_id': self.project_com_pigs.id})
        self.task_6 = self.env['project_com.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test5', 'user_id': False, 'project_com_id': self.project_com_pigs.id})


class TestPortalProject(TestPortalProjectBase):

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_employee_project_com_access_rights(self):
        pigs = self.project_com_pigs

        pigs.write({'privacy_visibility': 'employees'})
        # Do: Alfred reads project_com -> ok (employee ok employee)
        pigs.sudo(self.user_project_comuser).read(['user_id'])
        # Test: all project_com tasks visible
        tasks = self.env['project_com.task'].sudo(self.user_project_comuser).search([('project_com_id', '=', pigs.id)])
        test_task_ids = set([self.task_1.id, self.task_2.id, self.task_3.id, self.task_4.id, self.task_5.id, self.task_6.id])
        self.assertEqual(set(tasks.ids), test_task_ids,
                        'access rights: project_com user cannot see all tasks of an employees project_com')
        # Do: Bert reads project_com -> crash, no group
        self.assertRaises(AccessError, pigs.sudo(self.user_noone).read, ['user_id'])
        # Do: Donovan reads project_com -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.sudo(self.user_public).read, ['user_id'])
        # Do: project_com user is employee and can create a task
        tmp_task = self.env['project_com.task'].sudo(self.user_project_comuser).with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs task',
            'project_com_id': pigs.id})
        tmp_task.sudo(self.user_project_comuser).unlink()

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_favorite_project_com_access_rights(self):
        pigs = self.project_com_pigs.sudo(self.user_project_comuser)

        # we can't write on project_com name
        self.assertRaises(AccessError, pigs.write, {'name': 'False Pigs'})
        # we can write on is_favorite
        pigs.write({'is_favorite': True})

    @mute_logger('odoo.addons.base.ir.ir_model')
    def test_followers_project_com_access_rights(self):
        pigs = self.project_com_pigs
        pigs.write({'privacy_visibility': 'followers'})

        # Do: Alfred reads project_com -> ko (employee ko followers)
        self.assertRaises(AccessError, pigs.sudo(self.user_project_comuser).read, ['user_id'])
        # Test: no project_com task visible
        tasks = self.env['project_com.task'].sudo(self.user_project_comuser).search([('project_com_id', '=', pigs.id)])
        self.assertEqual(tasks, self.task_1,
                         'access rights: employee user should not see tasks of a not-followed followers project_com, only assigned')

        # Do: Bert reads project_com -> crash, no group
        self.assertRaises(AccessError, pigs.sudo(self.user_noone).read, ['user_id'])

        # Do: Donovan reads project_com -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.sudo(self.user_public).read, ['user_id'])

        pigs.message_subscribe(partner_ids=[self.user_project_comuser.partner_id.id])

        # Do: Alfred reads project_com -> ok (follower ok followers)
        donkey = pigs.sudo(self.user_project_comuser)
        donkey.invalidate_cache()
        donkey.read(['user_id'])

        # Do: Donovan reads project_com -> ko (public ko follower even if follower)
        self.assertRaises(AccessError, pigs.sudo(self.user_public).read, ['user_id'])
        # Do: project_com user is follower of the project_com and can create a task
        self.env['project_com.task'].sudo(self.user_project_comuser.id).with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs task', 'project_com_id': pigs.id
        })
        # not follower user should not be able to create a task
        pigs.sudo(self.user_project_comuser).message_unsubscribe(partner_ids=[self.user_project_comuser.partner_id.id])
        self.assertRaises(AccessError, self.env['project_com.task'].sudo(self.user_project_comuser).with_context({
            'mail_create_nolog': True}).create, {'name': 'Pigs task', 'project_com_id': pigs.id})

        # Do: project_com user can create a task without project_com
        self.assertRaises(AccessError, self.env['project_com.task'].sudo(self.user_project_comuser).with_context({
            'mail_create_nolog': True}).create, {'name': 'Pigs task', 'project_com_id': pigs.id})
