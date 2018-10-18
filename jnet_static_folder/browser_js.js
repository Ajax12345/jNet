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
  $('.signin').html(username);
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
});