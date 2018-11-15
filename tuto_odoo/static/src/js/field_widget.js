odoo.define('field.widget', function (require) {
'use strict';

var FieldChar = require('web.basic_fields').FieldChar;
var fieldRegistry = require('web.field_registry');

var CustomFieldChar = FieldChar.extend({
    _renderReadonly: function () {
        console.log("ok")
        debugger;
    },
});

fieldRegistry.add('my-custom-field', CustomFieldChar);



});