$(document).ready(function() {

  function init() {
    $('input[type=text]:first').focus();
    $('input[type=text]:first').on('keypress click', function() {
      $('.has-error').hide();
    });
  }

  // Bootstrap tooltip - required for popover
  $(function () {
    $('[data-toggle="tooltip"]').tooltip();
  });

  // Bootstrap popover
  $(function () {
    $('[data-toggle="popover"]').popover();
  });

  init();

  $.get( "/api/store/recover_streak/");

});
