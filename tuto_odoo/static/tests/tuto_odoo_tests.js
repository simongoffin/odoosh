odoo.define('test_odoo.widget_tests', function (require) {
"use strict";

var FormView = require('web.FormView');
var testUtils = require('web.test_utils');

var createView = testUtils.createView;

QUnit.module('fields', {}, function () {

QUnit.module('tuto_odoo', {
    beforeEach: function () {
        this.data = {
            model_first: {
                fields: {
                    name: { string: "Name", type: "char" },
                },
                records: [{
                    id: 1,
                    name: "Nom",
                }],
            },
        };
    }
});

QUnit.test('Check my-custom-field widget', function (assert) {
    assert.expect(2);
    var form = createView({
        View: FormView,
        model: 'model_first',
        data: this.data,
        arch: '<form string="Model First">' +
                '<sheet>' +
                    '<field name="name" widget="my-custom-field"/>' +
                '</sheet>' +
            '</form>',
        res_id: 1,
    });
    assert.strictEqual(form.$('.o_field_char').css('color'), "rgb(0, 0, 255)");
    form.$('.o_field_char').click();
    assert.strictEqual(form.$('.o_field_char').css('color'), "rgb(255, 0, 0)");

    form.destroy();
});

});

});