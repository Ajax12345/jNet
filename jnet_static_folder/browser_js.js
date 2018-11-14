async function get_app_listing_html(){
  let _html = await eel.get_app_listing()();
  $('.content_place').html(_html);
}
async function delete_user_app(title){
  let _final_result = await eel.delete_app(title)();

}
async function scan_enable_app(title){
  let _html_result = await eel.enable_app_check(title)();
  $('#__display_invalid_tag_'+title+'__').html(_html_result);
}

async function create_jnet_app(link, payload){

  var the_current_tab = 0;
  $('.tab').each(function(){
    if ($(this).css('background-color') === 'rgb(222, 222, 222)'){
      the_current_tab = parseInt(this.id.match('\\d+'));
    }
  });
  let jsonified_result = await eel.accept_dynamic_query_form(link, the_current_tab, JSON.stringify(payload))();
  var returned_result = JSON.parse(jsonified_result);
  
  if (!returned_result.success){
    var _error_message_html = `
      <p style="font-size:13px;color:#FF3402">App already exists</p>
      `;
      $('.__on_app_name_error__').html(_error_message_html);
  }
  else{
    get_jnet_url('jnet-browser:@apps');
  }
}


async function filter_browser_history(substring){
  let new_history_content = await eel.filter_browser_history(substring)();
  $('.__history_listing_canvas__').html(new_history_content);
}
async function delete_selected_history(delete_ids){
  let result = await eel.delete_selected_history(delete_ids)();

}

async function get_jnet_url_form(url_input, payload){
  $('.url_input').val(url_input);
  var the_current_tab = 0;
  $('.tab').each(function(){
    if ($(this).css('background-color') === 'rgb(222, 222, 222)'){
      the_current_tab = parseInt(this.id.match('\\d+'));
    }
  });
  if (typeof(payload) === 'object'){
    payload = JSON.stringify(payload);
  }
  let full_json = await eel.accept_query_form(url_input, the_current_tab, payload)();
  var returned_content = JSON.parse(full_json);
  if (returned_content['is_redirect']){
    $('.url_input').val(returned_content['route']);
  }
  $('.content_place').html(returned_content['html']);
}
async function get_jnet_url(url_input){
  $('.url_input').val(url_input);
  var the_current_tab = 0;
  $('.tab').each(function(){
    if ($(this).css('background-color') === 'rgb(222, 222, 222)'){
      the_current_tab = parseInt(this.id.match('\\d+'));
    }
  });

  let full_json = await eel.accept_query(url_input, the_current_tab)();
  var returned_content = JSON.parse(full_json);
  if (returned_content['is_redirect']){
    $('.url_input').val(returned_content['route']);
  }
  $('.content_place').html(returned_content['html']);
}

async function delete_all_history(){
  let result = await eel.delete_all_history()();
}
async function display_browsing_history(){
  let history_content = await eel.get_browser_history()();
  $('.content_place').html(history_content);
}

function get_max(arr){
    var start = arr[0];
    for (var i = 0; i < arr.length; i++){
      if (arr[i] > start){
        start = arr[i]
      }
    }
    return start;
  }
  function random_string(){
    var alphabet = "abcdefghijklmnopqrstuvwxyz";
    var result = "";
    for (var i = 2; i < Math.round(Math.random()*10)+3; i++){
      try{
        result += alphabet[Math.round(Math.random()*25)]
      }
      catch(error){
        result += "z";
      }
    }
    return result;
  }
var current_data = "";
async function update_browser_owner_display(){
  let username = await eel.get_full_username()();
  $('.__signin__').html(username);
  let body_search_content = await eel.get_home_search()();
  $('.content_place').append(body_search_content);
}
  function disable_start(){
      $('.input_wrapper').css('display', 'none');
      $('.main_action_wrapper').css('display', 'none');
      //$('.add_tab').css('display', 'none');
  }
  async function check_passcode(passcode){
    let result = await eel.verify_passcode(passcode)();
  
    if (result === 'true'){
      let final_result = await eel.setup_main_browser(passcode, current_data);
      $('.loading_bar').css('display', 'none');
      $('.__welcome_banner').css('display', 'none');
      $('.input_wrapper').css('display', 'block');
      $('.main_action_wrapper').css('display', 'block');
      update_browser_owner_display();

    }
    else{
      $('#passcodeissue').html('<p class="warning_text">incorrect passcode</p>');
    }
  }
  async function is_setup(){
    let result = await eel.is_setup()();
    if (result === 'true'){
      $('.loading_bar').css('display', 'none');
      $('.input_wrapper').css('display', 'block');
      $('.main_action_wrapper').css('display', 'block');
      update_browser_owner_display()
    }
    else{
      $('.loading_bar').css('display', 'none');
      $('.footer').css('display', 'none');
      $('.__welcome_banner').css('display', 'block');
      
    }
  }
  $(document).ready(function(){
    $('.__welcome_banner').css('display', 'none');
    $('.footer').css('display', 'none');
    disable_start();
    setTimeout(function(){
      is_setup();

    }, 2000);
    
    var current_clicked = null;
    var just_removed = false;
    var original_headers = {0:["Home"]};
    $('.main_action_wrapper').on('click', '.add_tab', function(){
      $('.url_input').val('jnet:@');
      var current_tabs = [];
      $('.tab').each(function(){
        current_tabs.push(parseInt(this.id.match('\\d+')));
      });
  
      var results = get_max(current_tabs) + 1;
      var new_results = results.toString();
      var generic_header = random_string();
      var the_html = `
        <div class='tab tab_item main_tab' id='tab${new_results}'>
          <div id='title_for_${new_results}'>
            <p class='browser_text' id='titletext${new_results}'>${generic_header}</p>
          </div>
          <div class='deletion_pane' id='remove_for_${new_results}'>
            <button class='delete_tab' id='delete${new_results}'>
              <i class="fas fa-times timesdeletion" style='color:black;'></i>
            </button>
          </div>
        </div>
      `;
      original_headers[new_results] = [generic_header];
      $('.all_tabs').append(the_html);
      if (current_tabs.length >= 9){
        $('.tab_item').css('width', parseFloat(90/(current_tabs.length+1))+'%');
      }
  
      $('.tab').each(function(){
        var the_id = parseInt(this.id.match('\\d+'));
        var the_length = parseInt($(this).css('width').match('\\d+'))/12;
  
        if ($('#titletext'+the_id.toString()).text().length >= the_length){
  
  
          var new_text = $('#titletext'+the_id.toString()).text().substring(0, the_length-3) +'...';
          $('#titletext'+the_id.toString()).text(new_text);
  
          original_headers[the_id].push(new_text);
  
        }
      });
  
      current_clicked = null;
      $('#tab'+new_results).css('background-color', '#DEDEDE');
      for (var i = 0; i < current_tabs.length; i++){
        $('#tab'+current_tabs[i].toString()).css('background-color', '#C0C0C0');
        $('#tab'+current_tabs[i].toString()).css('border-right', 'none');
      }
      
  
    });
  
    $('.main_action_wrapper').on('click', '.tab', function(){
      if (!just_removed){
        var all_tabs = [];
        $('.tab').each(function(){
          all_tabs.push(parseInt(this.id.match('\\d+')));
        });
          $(this).css('background-color', '#DEDEDE');
          var clinked_id = this.id.match('\\d+');
          current_clicked = parseInt(clinked_id);
          $('.tab').each(function(){
            if (parseInt(this.id.match('\\d+')) !== parseInt(clinked_id)){
              $(this).css('background-color', '#C0C0C0');
            }
          });
      }
      just_removed = false;
  
  
  
  
    });
    $('.main_action_wrapper').on('click', '.delete_tab', function(){
      just_removed = true;
      var original = [];
      $('.tab').each(function(){
        original.push(parseInt(this.id.match('\\d+')));
      });
      var final_results = [];
      $('#tab'+this.id.match('\\d+')).remove();
      $('.tab').each(function(){
        final_results.push(this.id.match('\\d+'));
      });
      if (final_results.length >= 9){
        $('.tab_item').css('width', parseFloat(90/(final_results.length+1))+'%');
      }
      else{
        $('.tab_item').css('width', '10%');
      }
      if (parseInt(this.id.match('\\d+')) === current_clicked){
        $('#tab'+final_results[final_results.length-1].toString()).css('background-color', '#DEDEDE');
  
      }
      else if (parseInt(this.id.match('\\d+')) === original[original.length-1] && current_clicked === null){
        $('#tab'+original[original.length-2].toString()).css('background-color', '#DEDEDE');
        $('#tab'+original[original.length-2].toString()).css('border-right', 'solid');
        $('#tab'+original[original.length-2].toString()).css('border-right-width', '1px');
        $('#tab'+original[original.length-2].toString()).css('border-right-color', '#8E8E8E');
      }
  
        $('#tab'+final_results[final_results.length-1].toString()).css('border-right', 'solid');
        $('#tab'+final_results[final_results.length-1].toString()).css('border-right-width', '1px');
        $('#tab'+final_results[final_results.length-1].toString()).css('border-right-color', '#8E8E8E');
  
        $('.tab').each(function(){
          if (parseInt(this.id.match('\\d+')) !== 0){
              var _final_text_result = "";
              var _all_text_versions = original_headers[parseInt(this.id.match('\\d+'))];
              var _current_length = parseInt($(this).css('width').match('\\d+'))/12;
              for (var i = 0; i < _all_text_versions.length; i++){
                if (_all_text_versions[i].length <= _current_length){
                  if (_all_text_versions[i].length > _final_text_result.length){
                    _final_text_result = _all_text_versions[i];
                  }
                }
              }
              $('#titletext'+this.id.match('\\d+')).text(_final_text_result);
  
  
  
          }
        });
  
  
    });
    $('.controls').on('click', '.apps', function(){
      async function get_app_html() {
  
        let stuff = await eel.app_html()();
  
        $('.content_place').html(stuff);
        }
  
      get_app_html();
    });
    /************************************* */
    $('.main_input').on('click', '.next_action', function(){

      var vals = {"firstname":$('#firstname').val(), "lastname":$('#lastname').val(), "username":$('#username').val(), 'email':$('#email').val()};
      var headers = ["firstname", "lastname", "username"];
      var flag = true;
      for (var i = 0; i < headers.length; i++){
  
        if (vals[headers[i]] == ''){
          var the_html = `
          <p class="warning_text">${headers[i]} cannot be left blank</p>
          `
          $('#'+headers[i]+'warning').html(the_html);
          flag = false;
        }
      }
      if (flag){
        $( ".input_vals" ).toggle( "slide" );
        setTimeout(
          function()
          {
            var new_html = `
  
            <div class='get_passcode'>
              <p class='description_text' style='font-size:18px;'>Please enter your root passcode to enable jNet to make changes:</p>
              <div class='spacer' style='height:20px;'></div>
              <input type='password' class='jnet_input' id='passcode' style='width:450px;'>
              <div id='passcodeissue'></div>
              <div class='spacer' style='height:60px;'></div>
              <table>
                <tr>
                  <td><button class='setup_button go_back'>Back</button></td>
                  <td><button class='setup_button continue'>Finish</button></td>
                </tr>
              </table>
            </div>
            `;
            $('.main_input').append(new_html);
          }, 500);
  
        current_data = vals;
        $('.next_action').remove();
      }
  
    });
    $('.main_input').on('click', '.continue', function(){
      var the_password = $('#passcode').val();
      if (the_password === ''){
          $('#passcodeissue').html('<p class="warning_text">passcode cannot be blank</p>')
      }
      else{
          check_passcode(the_password);
      }
      
      
      
  });
  $('.main_input').on('click', '.go_back', function(){
    $('.get_passcode').remove();
    $( ".input_vals" ).toggle( "slide");
    setTimeout(
      function()
      {
        $('.main_input').append("<button class='setup_button next_action'>Next</button>");
      }, 500)
  });
  
  $('.browser_input').on('click', '.__signin__', function(){
    display_browsing_history();
    $('.url_input').val('jnet-browser:@history')

  });
  
  $('.browser_input').on('keydown', '.url_input', function(_key){
    if (_key.keyCode == 13){
      get_jnet_url($('.url_input').val());
    }
  });
  $('.content_place').on('click', '.__delete_all__', function(){

    $('.__history_item__').each(function(){
      $('#__listing_'+this.id.match('\\d+')+'__').remove();
    });
    $('.__delete_all__').css('display', 'none');
    $('.__no_history__').html('<div class="__spacer__" style="height:80px;"></div>\n<p><strong>No browser history</strong></p>')
    $('.__delete_selected__').css('display', 'none');
    delete_all_history();
  });
  $('.content_place').on('click', '.__select_delete__', function(){

    var flag = false;
    $('.__select_delete__').each(function(){
      if ($(this).is(":checked")){
        flag = true;

      }
    });
    if (flag){
      $('.__delete_selected__').css('display', 'block');
    }
    else{
      $('.__delete_selected__').css('display', 'none');
    }
  });
  $('.content_place').on('click', '.__delete_selected__', function(){
  
      var to_delete = [];
      $('.__select_delete__').each(function(){
        if ($(this).is(":checked")){
          to_delete.push(this.id.match('\\d+'));
        }
        

      });
      var deletion_count = 0
      for (var i = 0; i < to_delete.length; i++){
        $('#__listing_'+to_delete[i]+'__').remove();
        deletion_count += 1;

      }
      $('.__delete_selected__').css('display', 'none');
      var count = 0;
      $('.__history_item__').each(function(){
        count += 1;
      });
      if (count === 0){
        $('.__delete_all__').css('display', 'none');

        $('.__no_history__').html('<div class="__spacer__" style="height:80px;"></div>\n<p><strong>No browser history</strong></p>')

      }
      delete_selected_history(JSON.stringify(to_delete));

  });
  $('.content_place').on('input', '.__filter_history__', function(){
    filter_browser_history($('.__filter_history__').val());
  });
  $('.browser_input').on('click', '.__href__', function(){
    alert('in href browser input');
    var url = this.dataset.link;
    var datasettab = this.dataset.tab;
    if (url ===undefined || datasettab === undefined){
      get_jnet_url($(this).text());
    }
    else{
      if (datasettab === "true"){
        get_jnet_url(url);
      }
      else{
        get_jnet_url($(this).text());
      }
    }
  });

  $('.browser_input').on('click', '.__div_href__', function(){
    var url = this.dataset.link;
    var datasettab = this.dataset.tab;
    if (url ===undefined || datasettab === undefined){
      get_jnet_url($(this).text());
    }
    else{
      if (datasettab === "true"){
        get_jnet_url(url);
      }
      else{
        get_jnet_url($(this).text());
      }
    }
  });
  $('.content_place').on('click', '.__div_href__', function(){
    var url = this.dataset.link;
    var datasettab = this.dataset.tab;
    if (url ===undefined || datasettab === undefined){
      get_jnet_url($(this).text());
    }
    else{
      if (datasettab === "true"){
        get_jnet_url(url);
      }
      else{
        get_jnet_url($(this).text());
      }
    }
  });
  $('.content_place').on('click', '.__href__', function(){
    var url = this.dataset.link;
    var datasettab = this.dataset.tab;
    if (url ===undefined || datasettab === undefined){
      get_jnet_url($(this).text());
    }
    else{
      if (datasettab === "true"){
        get_jnet_url(url);
      }
      else{
        get_jnet_url($(this).text());
      }
    }
  });
  /*
  $('.content_place').on('click', '.__create_app__', function(){
    $('.__app_message__').toggle('slide', {direction:'left'});
  });
  $('.content_place').on('click', '.__get_started_app_creation__', function(){
    $('.__app_message__').toggle('slide', {direction:'left'});
  });
  
  $('.browser_input').on('click', '.apps', function(){
    $('.url_input').val('jnet-browser:@apps');
    get_app_listing_html();
  });
  */
 $('.content_place').on('input', '#__app_creation_description__', function(){
  var _dest_part = $(this).val();
  var colors = {5:'#FF3402', 10:'#F54406', 15:'#EC5B29', 20:'#DF6F48', 25:'#E16B45', 30:'#DB7655', 35:'#F67628', 40:'#DF7636', 45:'#EA964B', 50:'#EBA653', 55:'#E7B042', 60:'#EFC82B', 65:'#E8D729'};
  for (var i = 5; i < 70; i += 5){
    if (65-_dest_part.length <= i){

      var full_count = 65-_dest_part.length;
      if (65-_dest_part.length < 0){
        full_count = 0;
      }
      var _char_display = "characters";
      if (65-_dest_part.length === 1){
        _char_display = "character";
      }
      var _the_mention_html = `
        <p style='font-size:13px;color:${colors[i]}'>${full_count} ${_char_display} left</p>
      `;
      $('.__description_word_count_display__').html(_the_mention_html);
      break;
    }
  }
  if (_dest_part.length >= 65){
    $(this).val(_dest_part.substring(0, 66));
  }
  });
  $('.content_place').on('click', '.__submit_app_create_form__', function(){
    if ($('#__app_creation_name__').val().length === 0){
      var _error_message_html = `
      <p style="font-size:13px;color:#FF3402">Name cannot be left blank</p>
      `;
      $('.__on_app_name_error__').html(_error_message_html);
    }
    else{
      var __app_name__ = $('#__app_creation_name__').val();
      var __description__ = $('#__app_creation_description__').val();
      var __hosting_option__ = $('.__app_hosting_option__').find(":selected").text();
      var _payload = {'name':__app_name__, 'description':__description__, 'host':__hosting_option__};
      //get_jnet_url_form(this.dataset.link, _payload);
      create_jnet_app(this.dataset.link, _payload);
    }
  });
  $('.content_place').on('input', '#__app_creation_name__', function(){
    $('.__on_app_name_error__').html('');
  });
  $('.content_place').on('click', '.__app_title__', function(){
    
    var _app_title = this.id;
    if ($('#__display_settings_for_'+_app_title+'__').html() != ''){
      $('#__display_settings_for_'+_app_title+'__').html('');
    }
    else{
      var _visibility = $('#__app_visibility_'+_app_title+'__').text();

      var new_html_ = `
      <div class='__spacer__' style='height:20px;'></div>
        <div style='height:1.5px;width:600px;background-color:#CFCFCF;margin: 0 auto;'></div>
        <div class='__spacer__' style='height:40px;'></div>
        <button class='__disable_app__' id='__disable_${_app_title}__'>Disable app</button>
        <div class='__spacer__' style='height:40px;'></div>
        <button class='__delete_app__' id='__delete_${_app_title}__'>Delete</button>
        <div class='__app_deletion_verification__' id='__app_deletion_verification_for${_app_title}'></div>
        <div class='__spacer__' style='height:20px;'></div>
      `;
      if (_visibility === 'Not deployed'){
        var new_html_ = `
        <div class='__spacer__' style='height:20px;'></div>
        <div style='height:1.5px;width:600px;background-color:#CFCFCF;margin: 0 auto;'></div>
        <div class='__spacer__' style='height:40px;'></div>
        <button class='__enable_app__' id='__enable_${_app_title}__'>Enable app</button>
        <div class='__invalid_tag_display__' id='__display_invalid_tag_${_app_title}__'></div>
        <div class='__spacer__' style='height:40px;'></div>
        <div class='__app_deletion_verification__' id='__app_deletion_verification_for_${_app_title}__'></div>
        <table>
          <tr>
            <td><button class='__delete_app__' id='__delete_${_app_title}__'>Delete app</button></td>
            <td id='__cancel_delete_${_app_title}__'></td>
          </tr>
        </table>
        
        
        <div class='__spacer__' style='height:20px;'></div>
      `;
      }
      $('#__display_settings_for_'+_app_title+'__').html(new_html_);
     }
    
  });
  $('.content_place').on('click', '.__delete_app__', function(){
    var _full_id = this.id
    var _title = _full_id.substring(9, _full_id.length-2);
    if ($(this).text() === 'Confirm deletion'){
      if ($('#__confirmdelete_'+_title+'__').val() === _title){
        $('#__app_pannel_'+_title+'__').remove();
        var _current_count = parseInt($('.__app_num_display__').text()) - 1;
        $('.__app_num_display__').text(_current_count);
        delete_user_app(_title);

      }
      else{
        $('#__invalid_confirmation_for_'+_title+'__').html('<p style="font-size:13px;color:#FF3402;margin-left:70px;">App titles do not match</p>')
      }
    }
    else{
      var new_html =`

      <p style='margin-left:70px'><strong>Type the name of the app you wish to delete:</strong></p>
      <input type='text' class='__app_attribute_value__' id='__confirmdelete_${_title}__' style='margin-left:70px;width:320px;height:35px;font-size:19px' placeholder='app name'>
      <div id='__invalid_confirmation_for_${_title}__'></div>
      <div style='height:20px'></div>
    
      `
      $('#__app_deletion_verification_for_'+_title+'__').html(new_html);
      $('#__delete_'+_title+'__').text('Confirm deletion');
      var deletion_html = `
      <button class='__cancel_deletion__' id='__cancel_delete_${_title}__'>Cancel</button>
      `;
      $('#__cancel_delete_'+_title+'__').html(deletion_html);
    }
    
  });
  $('.content_place').on('input', '.__app_attribute_value__', function(){
    var _full_id = this.id
    var _title = _full_id.substring(16, _full_id.length-2);
    $('#__invalid_confirmation_for_'+_title+'__').html('');
  });
  $('.content_place').on('click', '.__cancel_deletion__', function(){
    var full_id = this.id;
    var _title = full_id.substring(16, full_id.length-2);
    $('#__app_deletion_verification_for_'+_title+'__').html('');
    $('#__delete_'+_title+'__').text('Delete app');
    $('#__cancel_delete_'+_title+'__').html('');
  });
  $('.content_place').on('click', '.__enable_app__', function(){
    var _full_id = this.id;
    var _app_title = _full_id.substring(9, _full_id.length-2);
    scan_enable_app(_app_title);
  });
});
