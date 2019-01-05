odoo.define('field.widget', function (require) {
'use strict';

var FieldChar = require('web.basic_fields').FieldChar;
var fieldRegistry = require('web.field_registry');

var CustomFieldChar = FieldChar.extend({

    events: _.extend({}, FieldChar.prototype.events, {
        'click': '_onClick',
    }),

    _renderReadonly: function () {
        this.$el.text(this.value).css('color', 'blue');
    },

    _onClick: function (event) {
        event.stopPropagation();
        var is_blue = this.$el.text(this.value).css('color') == "rgb(0, 0, 255)";
        if(is_blue){
            this.$el.text(this.value).css('color', 'red');
        }
        else{
            this.$el.text(this.value).css('color', 'blue');
        }
    },
});

fieldRegistry.add('my-custom-field', CustomFieldChar);



});


odoo.define('tuto_odoo.ga.setting', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Dialog = require('web.Dialog');
var field_utils = require('web.field_utils');
var session = require('web.session');
var web_client = require('web.web_client');

var _t = core._t;
var QWeb = core.qweb;

var Dashboard = AbstractAction.extend(ControlPanelMixin, {
    template: 'tuto_odoo.maindashboard',

    events: {
        'click .js_link_analytics_settings': 'on_link_analytics_settings',
        'click .js_authorize': 'on_authorize',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['tuto_odoo.dashboard_content'];
    },

    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.fetch_data();
        });
    },

    start: function() {
        var self = this;
        return this._super().then(function() {
            self.render_dashboards();
            self.load_analytics_api();
        });
    },

    fetch_data: function() {
        var self = this;
        return this._rpc({
            route: '/tuto_odoo/fetch_dashboard_data',
            params: {
                user_id: odoo.session_info.uid || false,
            },
        }).done(function(result) {
            self.dashboard_data = result;
        });
    },

    load_analytics_api: function() {
        var self = this;
        if (!("gapi" in window)) {
            (function(w,d,s,g,js,fjs){
                g=w.gapi||(w.gapi={});g.analytics={q:[],ready:function(cb){this.q.push(cb);}};
                js=d.createElement(s);fjs=d.getElementsByTagName(s)[0];
                js.src='https://apis.google.com/js/platform.js';
                fjs.parentNode.insertBefore(js,fjs);js.onload=function(){g.load('analytics');};
            }(window,document,'script'));
        }
    },

    render_dashboards: function() {
        var self = this;
        _.each(this.dashboards_templates, function(template) {
            self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self}));
        });
    },

    on_authorize: function(ev) {
        var self = this;
        var CLIENT_ID = self.dashboard_data.ga_client_id;
        var SCOPES = ['https://www.googleapis.com/auth/analytics.readonly'];
        var authData = {
            client_id: CLIENT_ID,
            scope: SCOPES,
            immediate: false
        };
        gapi.auth.authorize(authData, function(response) {
            var authButton = self.$('.js_authorize');
            if (response.error) {
                authButton.hide();
            }
            else {
                authButton.show();
            }
        });
    },

    on_link_analytics_settings: function(ev) {
        ev.preventDefault();

        var self = this;
        var dialog = new Dialog(this, {
            size: 'medium',
            title: _t('Google Analytics'),
            $content: QWeb.render('tuto_odoo.ga_dialog_content', {
                ga_key: this.dashboard_data.ga_key || "",
                ga_client_id: this.dashboard_data.ga_client_id || "",
                ga_client_secret: this.dashboard_data.ga_client_secret || "",
                domain: "http:// " + window.location.href.split('/')[2] || "",
            }),
            buttons: [
                {
                    text: _t("Save"),
                    classes: 'btn-primary',
                    close: true,
                    click: function() {
                        var ga_key = dialog.$el.find('input[name="ga_key"]').val();
                        var ga_client_id = dialog.$el.find('input[name="ga_client_id"]').val();
                        var ga_client_secret = dialog.$el.find('input[name="ga_client_secret"]').val();
                        var domain = dialog.$el.find('input[name="domain"]').val();
                        self.on_save_ga_client_id(ga_key, ga_client_id, ga_client_secret, domain);
                    },
                },
                {
                    text: _t("Cancel"),
                    close: true,
                },
            ],
        }).open();
    },

    on_save_ga_client_id: function(ga_key, ga_client_id, ga_client_secret, domain) {
        var self = this;
        return this._rpc({
            route: '/tuto_odoo/dashboard/set_ga_data',
            params: {
                'ga_key': ga_key,
                'ga_client_id': ga_client_id,
                'ga_client_secret': ga_client_secret,
                'domain': domain,
                'user_id': odoo.session_info.uid || false,
            },
        }).then(function (result) {
            if (result.error) {
                self.do_warn(result.error.title, result.error.message);
                return;
            }
            self.fetch_data();
        });
    },

    render_dashboards: function() {
        var self = this;
        _.each(this.dashboards_templates, function(template) {
            self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self}));
        });
    },

});

core.action_registry.add('backend_dashboard', Dashboard);

return Dashboard;
});