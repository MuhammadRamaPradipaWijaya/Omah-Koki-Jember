$(document).ready(function() {
  $(window).scroll(function() {
    var usernameText = $('.username-text');
    if ($(this).scrollTop() > 1) { 
      usernameText.addClass('black');
    } else {
      usernameText.removeClass('black');
    }
  });
});
