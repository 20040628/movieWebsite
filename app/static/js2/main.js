(function ($) {
  "use strict";
  
  // Start Document Ready function
  $(document).ready(function () {
    // Sidebar Open & Close Start
    $('.toggle-btn').on('click', function () {
      $('.sidebar').addClass('active')
      $('.side-overlay').addClass('show')
    });

    $('.side-overlay, .sidebar-close-btn').on('click', function () {
      $('.side-overlay').removeClass('show')
      $('.sidebar').removeClass('active')
    });
    // Sidebar Open & Close End

    // Count character Js Start
    $('.text-counter').on('input', function () {
      const characterCount = $(this).val().length;
      console.log(characterCount);
      $('#current').text(characterCount);
    });
    // Count character Js End

  });
  // End Document Ready function

  // Header Sticky Js Start
  $(window).on('scroll', function() {
    if ($(window).scrollTop() >= 260) {
      $('.header').addClass('fixed-header');
    }
    else {
        $('.header').removeClass('fixed-header');
    }
  });

})(jQuery);
