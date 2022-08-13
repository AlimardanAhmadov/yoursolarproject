var swiper = new Swiper(".slide-content", {
    slidesPerView: 3,
    spaceBetween: 25,
    loop: true,
    centerSlide: 'true',
    fade: 'true',
    grabCursor: 'true',
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
      dynamicBullets: true,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },

    breakpoints:{
        0: {
            slidesPerView: 1,
        },
        520: {
            slidesPerView: 2,
        },
        950: {
            slidesPerView: 3,
        },
    },
});


$(document).on('click', '.service-item .plain-btn', function(){
    var id = '#' + $(this).data('modal');
    $(id).css({
        'visibility': 'visible',
        'opacity': 1,
        'pointer-events': 'auto',
    });
})

$(document).on('click', '.modal-close', function(){
    var id = '#' + $(this).data('modal');
    $(id).css({
        'visibility': 'hidden',
        'opacity': 0,
        'pointer-events': 'none',
    });
})

