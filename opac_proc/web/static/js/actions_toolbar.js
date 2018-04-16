"use strict";

var ActionToolbar = {
  /* action buttons selectors */
  btn_process_all_selector: '[data-action="process"][data-target="all"]',
  btn_process_selected_selector: '[data-action="process"][data-target="selected"]',
  btn_delete_all_selector: '[data-action="delete"][data-target="all"]',
  btn_delete_selected_selector: '[data-action="delete"][data-target="selected"]',
  /* action buttons */
  btn_process_all: null,
  btn_process_selected: null,
  btn_delete_all: null,
  btn_delete_selected: null,
  /* list of rows selected */
  rows_selected: [],
  custom_actions: [],
  /* helpers */
  get_rows_selected: function(){
    ActionToolbar.rows_selected = []
    $('input:checkbox:checked', '.tbody_object_list').each(function(index, element){
      ActionToolbar.rows_selected.push($(element).data('rowid'));
    });
  },
  show_loading_box: function(){
    var dialog = bootbox.dialog({
        message: '<p class="text-center">Por favor aguarde enquanto iniciamos o processo...<br><i class="fa fa-spin fa-spinner"></i></p>',
        closeButton: false
    });
    dialog.modal();
  },
  notify_no_rows_selected:function(){
    bootbox.alert({
      message: "Você deve selecionar pelo menos um registro!",
      size: 'small',
    });
  },
  notify_invalid_action:function(){
    bootbox.alert({
      message: "Esta ação é inválida!",
      size: 'small',
    });
  },
  ask_confirmation: function(msg, callback, callback_args=null, callback_action_type=null){
    bootbox.confirm({
      message: msg,
      size: 'small',
      buttons: {
        confirm: {
          label: '<i class="fa fa-check"></i> Confirmar',
          className: 'btn-success'
        },
        cancel: {
          label: '<i class="fa fa-times"></i> Cancelar',
          className: 'btn-danger'
        }
      },
      callback: function (result) {
        if (result) {
          if (callback_args === null) {
            if (callback_action_type === null) {
              callback();
            } else {
              callback(callback_action_type);
            }
          } else {
            if (callback_action_type === null) {
              callback(callback_args);
            } else {
              callback(callback_args, callback_action_type);
            }
          }
          ActionToolbar.show_loading_box();
        }
      }
    });
  },
  submit_custom_action_form: function(method_name, action_type){
    /*
      action_type: 'all' ou 'selected'. Se for 'selected' passamos os ids das rows selecionadas
    */
    var self = this;
    var form = $('#action_form');
    var action_field = $('input#action_name', form);
    var custom_action_definition = null;

    for (var i = 0; i < self.custom_actions.length; i++) {
      if (method_name === self.custom_actions[i]['method_name']) {
        custom_action_definition = self.custom_actions[i];
      }
    }

    if (custom_action_definition == null) {
      console.log('ação não definida');
      self.notify_invalid_action();
      return;
    }

    action_field.val('custom_action__' + method_name + '__' + action_type);
    console.log('action_field.value: ', action_field.val());
    form.attr('method', 'POST');
    form.attr('action', '.');
    if (action_type === 'selected') {
      var rows = ActionToolbar.rows_selected;
      for (var i = 0; i < rows.length; i++) {
        form.append( "<input type='text' name='rowid' value='" + rows[i] + " '>" );
      }
    }
    form.submit();
  },
  submit_action_form: function(action){
    var form = $('#action_form');
    var action_field = $('input#action_name', form);
    switch (action) {
      case "process_all":{
        action_field.val('process_all');
        form.attr('method', 'POST');
        form.attr('action', '.');
        form.submit();
        break;
      };
      case "process_selected":{
        action_field.val('process_selected');
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
  submit_process_all: function(){
    ActionToolbar.submit_action_form('process_all');
  },
  submit_process_selected: function(){
    ActionToolbar.submit_action_form('process_selected');
  },
  submit_delete_all: function(){
    ActionToolbar.submit_action_form('delete_all');
  },
  submit_delete_selected: function(){
    ActionToolbar.submit_action_form('delete_selected');
  },
  submit_custom_action: function(method_name, action_type) {
    console.log('Here call: "ActionToolbar.submit_action_form("method_name");" with method_name: ', method_name);
    ActionToolbar.submit_custom_action_form(method_name, action_type);
  },
  register_custom_action: function(method_name, label, can_select_rows){
    var self = this;
    var custom_action_definition = {
      'method_name': method_name,
      'label': label,
      'can_select_rows': can_select_rows,
      'btn_action_selector': {
        'btn_alone': '[data-action="' + method_name + '"]:not(".disabled")',
        'btn_all': '[data-action="' + method_name + '"][data-target="all"]',
        'btn_selected': '[data-action="' + method_name + '"][data-target="selected"]',
      }
    }
    this.custom_actions.push(custom_action_definition);
    /* bind click events */
    if (can_select_rows) {
      /* o botão que dispara a ação são na verdade 2 botões.
         temos dropdown com 2 botões: "All" e "Selected"
         -> usamos os selectores: 'all_records' e 'selected_records' */
      var btn_action_all = $(custom_action_definition['btn_action_selector']['btn_all']);
      var btn_action_sel = $(custom_action_definition['btn_action_selector']['btn_selected']);

      btn_action_all.click(function(){
        var msg = 'Você vai executar o processo de: ' + label + ' sobre todos os registros. Tem certeza?';
        self.ask_confirmation(
          msg,
          ActionToolbar.submit_custom_action,
          method_name,
          'all');
      });

      btn_action_sel.click(function(){
        self.get_rows_selected();
        if (self.rows_selected == 0){
          self.notify_no_rows_selected();
          return;
        } else {
          var selected_count =  self.rows_selected.length;
          var msg = 'Você vai executar o processo de: ' + label + ' sobre ' + selected_count + ' registro(s). Tem certeza?';
          self.ask_confirmation(
            msg,
            ActionToolbar.submit_custom_action,
            method_name,
            'selected');
        }
      });
    } else {
      /* o botão que dispara a ação é o apontado pelo selector: 'alone' */
      var btn_action_alone = $(custom_action_definition['btn_action_selector']['btn_alone']);
      btn_action_alone.click(function(){
        var msg = 'Você vai executar o processo de: ' + label + ' sobre todos os registros. Tem certeza?';
        self.ask_confirmation(
          msg,
          ActionToolbar.submit_custom_action,
          method_name,
          'all');
      });
    }
  },
  init: function(){
    var self = this;
    /* process all */
    this.btn_process_all = $(this.btn_process_all_selector);
    this.btn_process_all.click(function(){
      var msg = 'Você vai executar o processo de: <strong>ATUALIZAÇÃO</strong> sobre todos os registros. Tem certeza?';
      self.ask_confirmation(msg, ActionToolbar.submit_process_all);
    });
    /* process selected */
    this.btn_process_selected = $(this.btn_process_selected_selector);
    this.btn_process_selected.click(function(){
      self.get_rows_selected();
      if (self.rows_selected == 0){
        self.notify_no_rows_selected();
        return;
      } else {
        var selected_count =  self.rows_selected.length;
        var msg = 'Você vai executar o processo de: <strong>ATUALIZAÇÃO</strong> sobre ' + selected_count + ' registro(s). Tem certeza?';
        self.ask_confirmation(msg, ActionToolbar.submit_process_selected);
      }
    });
    /* delete all*/
    this.btn_delete_all = $(this.btn_delete_all_selector);
    this.btn_delete_all.click(function(){
      var msg = 'Você vai executar o processo de: <strong>REMOVER</strong> todos os registros. <strong>Esta ação não pode ser desfeita<strong>. Tem certeza?';
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
        var msg = 'Você vai executar o processo de: <strong>REMOVER</strong> ' + selected_count + ' registro(s).<strong>Esta ação não pode ser desfeita<strong>. Tem certeza?';
        self.ask_confirmation(msg, ActionToolbar.submit_delete_selected);
      }
    });

    return this;
  }
}
