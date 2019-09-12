"use strict";

window.FilterToolbar = {
  _filters: [],
  _datepicker_default_opts: {
    locale: 'pt-br',
    showTodayButton: true,
    sideBySide: true,
    showClear: true,
    showClose: true,
    useCurrent: false, /* https://github.com/Eonasdan/bootstrap-datetimepicker/issues/1075 */
    format: 'YYYY-MM-DD HH:mm:ss',
    icons: {
      time: "fa fa-clock-o",
      date: "fa fa-calendar",
      up: "fa fa-arrow-up",
      down: "fa fa-arrow-down"
    }
  },
  _getParameterByName: function(name, url) {
    if (!url) {
      url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
  },
  _set_filter_values_to_fields: function(){
    for (var i = 0; i < this._filters.length; i++) {
      var fdata = this._filters[i];

      if(fdata['type'] == 'string' || fdata['type'] == 'uuid') {
        var field = document.getElementById(fdata['param_name']);
        var qs_value = fdata['param_value'];
        if (field && qs_value) {
          field.value = qs_value;
        }

        if(fdata['type'] == 'string'){
          var select_input_id = fdata['filter_select_id'];
          var option_value_from_qs = fdata['param_option_value'];
          // set the option_value_from_qs to be selected
          if (option_value_from_qs) {
            var option_selected_selector = '#'+ select_input_id +' [value="' + option_value_from_qs + '"]';
            document.querySelector(option_selected_selector).selected = true;
          }
        }

      } else if (fdata['type'] == 'boolean') {
        var field_true = document.getElementById(fdata['field_id_true']);
        var field_false = document.getElementById(fdata['field_id_false']);
        var qs_value = fdata['param_value'];

        if (qs_value == "true") {
          /* boolean filter is set to true in querystring */
          field_true.click();
        } else if (qs_value == "false") {
          /* boolean filter is set to false in querystring */
          field_false.click();
        } /* else, boolean filter is unset in querystring */
      } else if (fdata['type'] == 'choices') {
        var select_input_id = fdata['filter_select_id'];
        var option_value_from_qs = fdata['param_option_value'];
        // set the option_value_from_qs to be selected
        if (option_value_from_qs) {
          var option_selected_selector = '#'+ select_input_id +' [value="' + option_value_from_qs + '"]';
          document.querySelector(option_selected_selector).selected = true;
        }
      }
    }
  },
  setup_datepickers: function(){
    /* https://eonasdan.github.io/bootstrap-datetimepicker/#linked-pickers */
    for (var i = 0; i < this._filters.length; i++) {
      var fdata = this._filters[i];
      if (fdata['type'] == 'date_time') {
        var from_opts = Object.create(this._datepicker_default_opts);
        var until_opts = Object.create(this._datepicker_default_opts);
        var from_dt = $('#' + fdata['datetimepicker_from_id'].replace(/\./g, "\\."));
        var until_td = $('#' + fdata['datetimepicker_until_id'].replace(/\./g, "\\."));

        if (fdata['param_value_from'] !== "") {
          from_opts['defaultDate'] = fdata['param_value_from'];
        }

        if (fdata['param_value_until'] !== "") {
          until_opts['defaultDate'] = fdata['param_value_until'];
        }

        from_dt.datetimepicker(from_opts);
        until_td.datetimepicker(until_opts);

        /* relate both datetime pickers to avoid: UNTIL DATE TIME > FROM DATE TIME */
        from_dt.on("dp.change", function (e) {
          until_td.data("DateTimePicker").minDate(e.date);
        });
        until_td.on("dp.change", function (e) {
          from_dt.data("DateTimePicker").maxDate(e.date);
        });
      }
    }
  },
  push_filter: function(name, type){
    var fdata = {
      'name': name,
      'type': type,
    }

    if(type == 'uuid') {
      fdata['field_id'] = "filter__value__" + name;
      fdata['param_name'] = "filter__value__" + name;
      fdata['param_value'] = this._getParameterByName(fdata['param_name']);
    } else if (type == 'string') {
      fdata['field_id'] = "filter__value__" + name;
      fdata['filter_select_id'] = "filter__option__" + name;
      fdata['param_name'] = "filter__value__" + name;
      fdata['param_value'] = this._getParameterByName(fdata['param_name']);
      /* filter options are: iexact, icontains, istartswith, endswith  */
      fdata['param_option_name'] = "filter__option__" + name;
      fdata['param_option_value'] = this._getParameterByName(fdata['param_option_name']);
    } else if (type == 'boolean') {
      fdata['field_id_true'] = "filter__value__" + name + "_1";
      fdata['field_id_false'] = "filter__value__" + name + "_0";
      fdata['param_name'] = "filter__value__" + name;
      fdata['param_value'] = this._getParameterByName(fdata['param_name']);
    } else if (type == 'date_time') {
      /* from */
      fdata['field_id_from'] =  "filter__value__from__" + name;
      fdata['param_name_from'] = "filter__value__from__" + name;
      fdata['param_value_from'] = this._getParameterByName(fdata['param_name_from']);
      /* until */
      fdata['field_id_until'] =  "filter__value__until__" + name;
      fdata['param_name_until'] = "filter__value__until__" + name;
      fdata['param_value_until'] = this._getParameterByName(fdata['param_name_until']);
      /* datepickers ids */
      fdata['datetimepicker_from_id'] = "datetimepicker__from__" + name;
      fdata['datetimepicker_until_id'] = "datetimepicker__until__" + name;
    } else if (type == 'choices') {
      fdata['field_id'] = "filter__value__" + name;
      fdata['filter_select_id'] = "filter__option__" + name;
      fdata['param_option_name'] = "filter__option__" + name;
      fdata['param_option_value'] = this._getParameterByName(fdata['param_option_name']);
    }
    this._filters.push(fdata);
  },
  init: function(){
    /* initialize when dom ready event (jQuery required) */
    this._set_filter_values_to_fields();
  }
}
