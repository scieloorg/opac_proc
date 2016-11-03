"use strict";

var ActionToolbar = {
  /* action buttons selectors */
  btn_create_selector: '[data-action="create"]:not(".disabled")',
  btn_update_all_selector: '[data-action="update"][data-target="all"]',
  btn_update_selected_selector: '[data-action="update"][data-target="selected"]',
  btn_delete_all_selector: '[data-action="delete"][data-target="all"]',
  btn_delete_selected_selector: '[data-action="delete"][data-target="selected"]',
  /* action buttons */
  btn_create: null,
  btn_update_all: null,
  btn_update_selected: null,
  btn_delete_all: null,
  btn_delete_selected: null,
  /* list of rows selected */
  rows_selected: [],
  /* helpers */
  get_rows_selected: function(){
    ActionToolbar.rows_selected = []
    $('input:checkbox:checked', '.tbody_object_list').each(function(index, element){
      ActionToolbar.rows_selected.push($(element).data('rowid'));
    });
  },
  show_loading_box: function(){
    var dialog = bootbox.dialog({
        message: '<p class="text-center">Please wait while we do something...<br><i class="fa fa-spin fa-spinner"></i></p>',
        closeButton: false
    });
    dialog.modal();
  },
  notify_no_rows_selected:function(){
    bootbox.alert({
      message: "You must select at least one row!",
      size: 'small',
    });
  },
  notify_invalid_action:function(){
    bootbox.alert({
      message: "This action is invalid!",
      size: 'small',
    });
  },
  ask_confirmation: function(msg, callback){
    bootbox.confirm({
      message: msg,
      size: 'small',
      buttons: {
        confirm: {
          label: '<i class="fa fa-check"></i> Confirm',
          className: 'btn-success'
        },
        cancel: {
          label: '<i class="fa fa-times"></i> Cancel',
          className: 'btn-danger'
        }
      },
      callback: function (result) {
        if (result) {
          callback();
          ActionToolbar.show_loading_box();
        }
      }
    });
  },
  submit_action_form: function(action){
    var form = $('#action_form');
    var action_field = $('input#action_name', form);

    switch (action) {
      case "create":{
        action_field.val('create');
        form.attr('method', 'POST');
        form.attr('action', '.');
        form.submit();
        break;
      };
      case "update_all":{
        action_field.val('update_all');
        form.attr('method', 'POST');
        form.attr('action', '.');
        form.submit();
        break;
      };
      case "update_selected":{
        action_field.val('update_selected');
        form.attr('method', 'POST');
        form.attr('action', '.');
        var rows = ActionToolbar.rows_selected;
        for (var i = 0; i < rows.length; i++) {
          form.append( "<input type='text' name='rowid' value='" + rows[i] + " '>" );
        }
        form.submit();
        break;
      };
      case "delete_all":{
        action_field.val('delete_all');
        form.attr('method', 'POST');
        form.attr('action', '.');
        form.submit();
        break;
      };
      case "delete_selected":{
        action_field.val('delete_selected');
        form.attr('method', 'POST');
        form.attr('action', '.');
        var rows = ActionToolbar.rows_selected;
        for (var i = 0; i < rows.length; i++) {
          form.append( "<input type='text' name='rowid' value='" + rows[i] + " '>" );
        }
        form.submit();
        break;
      };
      default:{
        ActionToolbar.notify_invalid_action();
        break;
      }
    }
  },
  submit_create: function(){
    ActionToolbar.submit_action_form('create');
  },
  submit_update_all: function(){
    ActionToolbar.submit_action_form('update_all');
  },
  submit_update_selected: function(){
    ActionToolbar.submit_action_form('update_selected');
  },
  submit_delete_all: function(){
    ActionToolbar.submit_action_form('delete_all');
  },
  submit_delete_selected: function(){
    ActionToolbar.submit_action_form('delete_selected');
  },
  init: function(){
    var self = this;
    /* create */
    this.btn_create = $(this.btn_create_selector);
    this.btn_create.click(function(){
      var msg = 'You will <b>CREATE</b> new records.<br/>Are you sure? ';
      self.ask_confirmation(msg, ActionToolbar.submit_create);
    });
    /* update all */
    this.btn_update_all = $(this.btn_update_all_selector);
    this.btn_update_all.click(function(){
      var msg = 'You will <b>UPDATE</b> all records.<br/>Are you sure? ';
      self.ask_confirmation(msg, ActionToolbar.submit_update_all);
    });
    /* update selected */
    this.btn_update_selected = $(this.btn_update_selected_selector);
    this.btn_update_selected.click(function(){
      self.get_rows_selected();
      if (self.rows_selected == 0){
        self.notify_no_rows_selected();
        return;
      } else {
        var selected_count =  self.rows_selected.length;
        var msg = 'You will <b>UPDATE</b> selected ' + selected_count + ' record(s).<br/>Are you sure? ';
        self.ask_confirmation(msg, ActionToolbar.submit_update_selected);
      }
    });
    /* delete all*/
    this.btn_delete_all = $(this.btn_delete_all_selector);
    this.btn_delete_all.click(function(){
      var msg = 'You will <b>DELETE</b> all records.<br/>Are you sure? ';
      self.ask_confirmation(msg, ActionToolbar.submit_delete_all);
    });
    /* delete selected */
    this.btn_delete_selected = $(this.btn_delete_selected_selector);
    this.btn_delete_selected.click(function(){
      self.get_rows_selected();
      if (self.rows_selected == 0){
        self.notify_no_rows_selected();
        return;
      } else {
        var selected_count =  self.rows_selected.length;
        var msg = 'You will <b>DELETE</b> selected ' + selected_count + ' record(s).<br/>re you sure? ';
        self.ask_confirmation(msg, ActionToolbar.submit_delete_selected);
      }
    });
  }
}
