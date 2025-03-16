(function ($) {
	"use strict";

	jQuery(document).ready(function ($) {
		/*
		=================================================================
		Count characters
		=================================================================
		*/
		$('.text-counter').on('input', function () {
		  const characterCount = $(this).val().length;
		  console.log(characterCount);
		  $('#current').text(characterCount);
		});


		/* 
		=================================================================
		Carousel animation
		=================================================================	
		*/

		$(".filmoja-slide").owlCarousel({
			animateOut: 'fadeOutLeft',
			animateIn: 'fadeIn',
			items: 3,
			nav: true,
			dots: false,
			autoplayTimeout: 7000,
			autoplaySpeed: 2000,
			autoplay: false,
			loop: true,
			navText: ["<i class='fa fa-long-arrow-left white'></i> <span class='white'>Previous</span>", "<span class='white'>Next</span> <i class='fa fa-long-arrow-right white'></i>"],
			mouseDrag: false,
			touchDrag: false,
			responsive: {
				0: {
					items: 1
				},
				480: {
					items: 1
				},
				600: {
					items: 1
				},
				750: {
					items: 1
				},
				1000: {
					items: 1
				},
				1200: {
					items: 1
				}
			}
		});

		$(".filmoja-slide").on("translate.owl.carousel", function () {
			$(".filmoja-main-slide span").removeClass("animated fadeInDown").css("opacity", "0");
			$(".filmoja-main-slide h2, .filmoja-main-slide p").removeClass("animated fadeInLeft").css("opacity", "0");
			$(".filmoja-main-slide .slider-play").removeClass("animated fadeInUp").css("opacity", "0");
		});
		$(".filmoja-slide").on("translated.owl.carousel", function () {
			$(".filmoja-main-slide span").addClass("animated fadeInDown").css("opacity", "1");
			$(".filmoja-main-slide h2, .filmoja-main-slide p").addClass("animated fadeInLeft").css("opacity", "1");
			$(".filmoja-main-slide .slider-play").addClass("animated fadeInUp").css("opacity", "1");
		});


		/* 
		=================================================================
		Popup JS
		=================================================================	
		*/

		$('.popup-youtube, .play-video').magnificPopup({
			disableOn: 700,
			type: 'iframe',
			mainClass: 'mfp-fade',
			removalDelay: 160,
			preloader: false,
			fixedContentPos: false
		});

		/*
		=================================================================
		Responsive Menu
		=================================================================	
		*/
		$("ul#responsive_navigation").slicknav({
			prependTo: ".filmoja-responsive-menu"
		});
	});

	   /* 
		=================================================================
		Btn To Top
		=================================================================	
		*/
	if ($("body").length) {
		var btnUp = $('<div/>', {
			'class': 'btntoTop'
		});
		btnUp.appendTo('body');
		$(document).on('click', '.btntoTop', function () {
			$('html, body').animate({
				scrollTop: 0
			}, 700);
		});
		$(window).on('scroll', function () {
			if ($(this).scrollTop() > 200) $('.btntoTop').addClass('active');
			else $('.btntoTop').removeClass('active');
		});
	}
}(jQuery));

// Get three rotograph images
document.addEventListener('DOMContentLoaded', function() {
	const slideItems = document.querySelectorAll('.filmoja-main-slide');
	slideItems.forEach(function(item) {
		const backdropPath = item.getAttribute('data-backdrop');
		item.style.backgroundImage = `url('https://image.tmdb.org/t/p/original${backdropPath}')`;
	});
});