# -*- coding: utf-8 -*-

from odoo.tests.common import SavepointCase


class TestProjectBase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProjectBase, cls).setUpClass()

        user_group_employee = cls.env.ref('base.group_user')
        user_group_project_com_user = cls.env.ref('project_com.group_project_com_user')
        user_group_project_com_manager = cls.env.ref('project_com.group_project_com_manager')

        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Valid Lelitre',
            'email': 'valid.lelitre@agrolait.com'})
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Valid Poilvache',
            'email': 'valid.other@gmail.com'})

        # Test users to use through the various tests
        Users = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user_public = Users.create({
            'name': 'Bert Tartignole',
            'login': 'bert',
            'email': 'b.t@example.com',
            'signature': 'SignBert',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.env.ref('base.group_public').id])]})
        cls.user_portal = Users.create({
            'name': 'Chell Gladys',
            'login': 'chell',
            'email': 'chell@gladys.portal',
            'signature': 'SignChell',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])]})
        cls.user_project_comuser = Users.create({
            'name': 'Armande ProjectUser',
            'login': 'Armande',
            'email': 'armande.project_comuser@example.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_project_com_user.id])]
        })
        cls.user_project_commanager = Users.create({
            'name': 'Bastien ProjectManager',
            'login': 'bastien',
            'email': 'bastien.project_commanager@example.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_project_com_manager.id])]})

        # Test 'Pigs' project_com
        cls.project_com_pigs = cls.env['project_com.project_com'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs',
            'privacy_visibility': 'employees',
            'alias_name': 'project_com+pigs',
            'partner_id': cls.partner_1.id})
        # Already-existing tasks in Pigs
        cls.task_1 = cls.env['project_com.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs UserTask',
            'user_id': cls.user_project_comuser.id,
            'project_com_id': cls.project_com_pigs.id})
        cls.task_2 = cls.env['project_com.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs ManagerTask',
            'user_id': cls.user_project_commanager.id,
            'project_com_id': cls.project_com_pigs.id})

        # Test 'Goats' project_com, same as 'Pigs', but with 2 stages
        cls.project_com_goats = cls.env['project_com.project_com'].with_context({'mail_create_nolog': True}).create({
            'name': 'Goats',
            'privacy_visibility': 'followers',
            'alias_name': 'project_com+goats',
            'partner_id': cls.partner_1.id,
            'type_ids': [
                (0, 0, {
                    'name': 'New',
                    'sequence': 1,
                }),
                (0, 0, {
                    'name': 'Won',
                    'sequence': 10,
                })]
            })

    def format_and_process(self, template, to='groups@example.com, other@gmail.com', subject='Frogs',
                           extra='', email_from='Sylvie Lelitre <test.sylvie.lelitre@agrolait.com>',
                           cc='', msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
                           model=None, target_model='project_com.task', target_field='name'):
        self.assertFalse(self.env[target_model].search([(target_field, '=', subject)]))
        mail = template.format(to=to, subject=subject, cc=cc, extra=extra, email_from=email_from, msg_id=msg_id)
        self.env['mail.thread'].with_context(mail_channel_noautofollow=True).message_process(model, mail)
        return self.env[target_model].search([(target_field, '=', subject)])
