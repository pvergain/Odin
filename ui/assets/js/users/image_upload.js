$(document).ready(function(){
  if($('[data-toggle="popover"]').length > 0) {
    $('[data-toggle="popover"]').popover({ trigger: "focus"});
  }

  var regQuestion = document.getElementsByClassName("reg-img-container")[0];
  var regError =  document.getElementById('error_1_id_password');

  if (typeof(regError) != 'undefined' && regError != null){
     $(regQuestion).css({"margin-top" : "-26px"});
  }

  $(".edit-profile .editable-user-avatar").click(function(){
    $("#div_id_full_image input[type='file']").click()
  })})
