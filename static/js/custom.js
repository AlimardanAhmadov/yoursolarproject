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

// GENERATE CSRF TOKEN

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
  
const csrftoken = getCookie('csrftoken');

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


$(document).on("click", function(e) {
    if(!$(e.target).is(".dropdown .plain-btn")) {
        if($(e.target).parents(".dropdown-card").length==0){
            $('.dropdown-box').removeClass('open');
        }
    }
    else {
        $('.dropdown-box').removeClass('open');
        if ($(e.target).next().hasClass('open')) {
            $(e.target).next().removeClass('open');
        }
        else {
            $(e.target).next().addClass('open');
        }
    }
});

// SAVE THE CHECKED CHECKBOX INPUTS TO THE LOCAL STORAGE

// SEARCH FUNCTIONALITY

$(document).on('click', '.close-badge', function(e){
    e.preventDefault();
    var value = $(this).parents('button').attr('data-val');
    var checked_input = $('input').filter(function() { return this.value == value });
    var unchecked = checked_input.prop("checked", false);
    if (unchecked){
        $(this).parents('button').remove()
    }
})

$(document).on('click', '.category-item', function(event){
    var index = $('.category-item').index($(this));

	if ($(this).hasClass('selected')) {
		$(this).removeClass('selected');
        $('.category-item').get(index).style.setProperty("--card-gradient", "66%");
	}
	else {
		$(this).addClass('selected');
        $('.category-item').get(index).style.setProperty("--card-gradient", "35%");
	}
})

let scheduled_function = false; 
const delay_by_in_ms = 500;
const results_div = $('.card-list');
const pagination_div = $('.pagination');
const endpoint = '/e-shop/';   

let ajax_call = function (endpoint, request_parameters) {
  	$.getJSON(endpoint, request_parameters)
    .done(response => {  
        $("#product-counter").load(location.href + " #product-counter");
        // remove loader class
        $('.search-button').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/></svg>')
        // Remove disabled class
        $('#eShop').removeClass('disabled');
        results_div.html(response['html_from_view']);
    })
}


let ajax_call_1 = function (endpoint, request_parameters) {
    $.getJSON(endpoint, request_parameters)
    .done(response => {  
        // remove loader class
        $('.search-button').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/></svg>')
        // Remove disabled class
        results_div.fadeTo('fast', 1);
    })
}

$(document).on('click', '.category-item, .close-badge', function(event){
	event.preventDefault(); 

    // Add button loader
    $('.search-button').html('<div class="lds-ring"><div></div><div></div><div></div><div></div></div>');

    // Disable eShop
    $('#eShop').addClass('disabled');

    // Initialize current url
    const url = new URL(window.location);

	var title = $('input[name="title"]').val();

    if (title){
        url.searchParams.set('q', title);
    }
    else {
        url.searchParams.delete('q');
    }

    var c_checkboxes = $('.category-item.selected').map(function(_, el) {
        return $(el).attr('data-val');
    }).get();

    if (c_checkboxes.length > 0){
        category = c_checkboxes
        url.searchParams.set('category', c_checkboxes);
    }
    else {
        url.searchParams.delete('category');
        category = $('.category-item').map(function(_, el) {
            return $(el).attr('data-val');
        }).get();
    }

    var av_checkboxes = $('input[name=availability]:checked').map(function(_, el) {
        return $(el).val();
    }).get();

    if (av_checkboxes.length > 0) {
        availability = av_checkboxes
        url.searchParams.set('availability', availability);
    }
    else {
        var availability = $('input[name="availability"]').map(function(_, el) {
            return $(el).val();
        }).get();
        url.searchParams.delete('availability');
    }

    var b_checkboxes = $('input[name="brand"]:checked').map(function(_, el) {
        return $(el).val();
    }).get();
    
    if (b_checkboxes.length > 0) {
        brand = b_checkboxes
        url.searchParams.set('brand', brand);
    }
    else {
        var brand = $('input[name="brand"]').map(function(_, el) {
            return $(el).val();
        }).get();
        url.searchParams.delete('brand');
    }

    var w_checkboxes = $('input[name="wattage"]:checked').map(function(_, el) {
        return $(el).val();
    }).get();
    
    if (w_checkboxes.length > 0) {
        wattage = w_checkboxes
        url.searchParams.set('wattage', wattage);
    }
    else {
        var wattage = $('input[name="wattage"]').map(function(_, el) {
            return $(el).val();
        }).get();
        url.searchParams.delete('wattage');
    }
	const request_parameters = {
		"availability[]": availability,
		"brand[]": brand,
		"wattage[]": wattage,
        "category[]": category,
        "q": title,
        "is_ajax": "True"
	}

    if (scheduled_function) {
        clearTimeout(scheduled_function)
    } 
    window.history.pushState({}, '', url);
    scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})

$(document).on('change', '.choice-input-wrapper .form-check-input, input[name="title"]', function(event){
	event.preventDefault(); 
    // Add button loader
    $('.search-button').html('<div class="lds-ring"><div></div><div></div><div></div><div></div></div>');

    // Initialize current url
    const url = new URL(window.location);

    // Disable eShop
    $('#eShop').addClass('disabled');

	var title = $('input[name="title"]').val();

    if (title){
        url.searchParams.set('q', title);
    }
    else {
        url.searchParams.delete('q');
    }

    var c_checkboxes = $('.category-item.selected').map(function(_, el) {
        return $(el).attr('data-val');
    }).get();

    if (c_checkboxes.length > 0){
        category = c_checkboxes
        url.searchParams.set('category', c_checkboxes);
    }
    else {
        url.searchParams.delete('category');
        category = $('.category-item').map(function(_, el) {
            return $(el).attr('data-val');
        }).get();
    }

    var av_checkboxes = $('input[name=availability]:checked').map(function(_, el) {
        return $(el).val();
    }).get();

    if (av_checkboxes.length > 0) {
        availability = av_checkboxes
        url.searchParams.set('availability', availability);
    }
    else {
        var availability = $('input[name="availability"]').map(function(_, el) {
            return $(el).val();
        }).get();
        url.searchParams.delete('availability');
    }

    var b_checkboxes = $('input[name="brand"]:checked').map(function(_, el) {
        return $(el).val();
    }).get();
    
    if (b_checkboxes.length > 0) {
        brand = b_checkboxes
        url.searchParams.set('brand', brand);
    }
    else {
        var brand = $('input[name="brand"]').map(function(_, el) {
            return $(el).val();
        }).get();
        url.searchParams.delete('brand');
    }

    var w_checkboxes = $('input[name="wattage"]:checked').map(function(_, el) {
        return $(el).val();
    }).get();
    
    if (w_checkboxes.length > 0) {
        wattage = w_checkboxes
        url.searchParams.set('wattage', wattage);
    }
    else {
        var wattage = $('input[name="wattage"]').map(function(_, el) {
            return $(el).val();
        }).get();
        url.searchParams.delete('wattage');
    }
    
	const request_parameters = {
		"availability[]": availability,
		"brand[]": brand,
		"wattage[]": wattage,
        "category[]": category,
        "q": title,
        "is_ajax": "True"
	}

	if (scheduled_function) {
		clearTimeout(scheduled_function)
	} 
    window.history.pushState({}, '', url);
	scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})

function hasQueryParams(url) {
    return url.includes('?');
}

$(window).on('load', function(){
    // Initialize current url
    const url = new URL(window.location);
    
    if (hasQueryParams(url.href)) {
        var title = $('input[name="title"]').val();

        var c_checkboxes = $('.category-item.selected').map(function(_, el) {
            return $(el).attr('data-val');
        }).get();

        if (c_checkboxes.length > 0){
            category = c_checkboxes
        }
        else {
            category = $('.category-item').map(function(_, el) {
                return $(el).attr('data-val');
            }).get();
        }

        var av_checkboxes = $('input[name=availability]:checked').map(function(_, el) {
            return $(el).val();
        }).get();

        if (av_checkboxes.length > 0) {
            availability = av_checkboxes
        }
        else {
            var availability = $('input[name="availability"]').map(function(_, el) {
                return $(el).val();
            }).get();
        }

        var b_checkboxes = $('input[name="brand"]:checked').map(function(_, el) {
            return $(el).val();
        }).get();
        
        if (b_checkboxes.length > 0) {
            brand = b_checkboxes
        }
        else {
            var brand = $('input[name="brand"]').map(function(_, el) {
                return $(el).val();
            }).get();
        }

        var w_checkboxes = $('input[name="wattage"]:checked').map(function(_, el) {
            return $(el).val();
        }).get();
        
        if (w_checkboxes.length > 0) {
            wattage = w_checkboxes
        }
        else {
            var wattage = $('input[name="wattage"]').map(function(_, el) {
                return $(el).val();
            }).get();
        }
        
        const request_parameters = {
            "availability[]": availability,
            "brand[]": brand,
            "wattage[]": wattage,
            "category[]": category,
            "q": title,
            "is_ajax": "False"
        }

        if (scheduled_function) {
            clearTimeout(scheduled_function)
        } 
        window.history.pushState({}, '', url);
        scheduled_function = setTimeout(ajax_call_1, delay_by_in_ms, endpoint, request_parameters)
    }
})


var checkboxes = document.querySelectorAll('.form-check-input');
var categories = document.querySelectorAll('.category-item');

const url = String(window.location.href).replaceAll('+', ' ');

document.addEventListener('DOMContentLoaded', function () {
    checkboxes.forEach(function (checkbox) {
        if (url.includes(checkbox.value)) {
            document.getElementById(checkbox.id).checked = true;
            html = '<button class="badge plain-btn" data-val="' + checkbox.value + '"><span>' + checkbox.value +'</span><div class="close close-badge"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg></div></button>';
            $('.filter-tags').append(html);
        }
        else{
            window.localStorage.removeItem(checkbox.id);
            $('.badge[data-val="' + checkbox.value + '"]').remove();
        }
    });
    categories.forEach(function (category) {
        if (url.includes(category.dataset.val)) {
            document.getElementById(category.id).classList.add('selected');
            document.getElementById(category.id).style.setProperty("--card-gradient", "35%");
            html = '<button class="badge plain-btn" data-val="' + category.dataset.val + '"><span>' + category.dataset.val +'</span><div class="close close-badge"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg></div></button>';
            $('.filter-tags').append(html);
        }
        else{
            window.localStorage.removeItem(category.id);
            $('.badge[data-val="' + category.dataset.val + '"]').remove();
        }
    });
});

checkboxes.forEach(function (checkbox) {
    checkbox.addEventListener('change', function () {
        if (url.includes(this.value)) {
            window.localStorage.setItem(this.id, this.value);
        }
        if ($('.badge[data-val="' + this.value + '"]').length){
            $('.badge[data-val="' + this.value + '"]').remove();
        }
        else {
            html = '<button class="badge plain-btn" data-val="' + this.value + '"><span>' + this.value +'</span><div class="close close-badge"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg></div></button>';
            $('.filter-tags').append(html);
        }
    });
});


categories.forEach(function (category) {
    category.addEventListener('click', function () {
        if (url.includes(this.dataset.val)) {
            window.localStorage.setItem(this.id, this.value);
        }
        if ($('.badge[data-val="' + this.dataset.val + '"]').length){
            $('.badge[data-val="' + this.dataset.val + '"]').remove();
        }
        else {
            html = '<button class="badge plain-btn" data-val="' + this.dataset.val + '"><span>' + this.dataset.val +'</span><div class="close close-badge"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg></div></button>';
            $('.filter-tags').append(html);
        }
    });
});


// PRODUCT GALLERY

const thumbnails = document.querySelectorAll('.thumbnail');

thumbnails.forEach(function (thumbnail) {
    thumbnail.addEventListener('click', function () {
        var newSelection = thumbnail.dataset.big;
        $('.thumbnail').removeClass('selected');
    
        $(this).addClass('selected');
        var $img = $('.primary').css("background-image","url(" + newSelection + ")");
        $('.primary').empty().append($img.hide().fadeIn('slow'));
    });
});
// PRODUCT GALLERY END

// QUANTITY INCREMENT CONTROLS
(function () {
    "use strict";
    var jQueryPlugin = (window.jQueryPlugin = function (ident, func) {
        return function (arg) {
            if (this.length > 1) {
            this.each(function () {
                var $this = $(this);
    
                if (!$this.data(ident)) {
                $this.data(ident, func($this, arg));
                }
            });
    
            return this;
            } else if (this.length === 1) {
            if (!this.data(ident)) {
                this.data(ident, func(this, arg));
            }
    
            return this.data(ident);
            }
        };
        });
    })();
  
    (function () {
        "use strict";
        function Guantity($root) {
        const element = $root;
        const quantity = $root.first("data-quantity");
        const quantity_target = $root.find("[data-quantity-target]");
        const quantity_minus = $root.find("[data-quantity-minus]");
        const quantity_plus = $root.find("[data-quantity-plus]");
        var quantity_ = quantity_target.val();
        $(quantity_minus).click(function () {
            quantity_target.val(--quantity_);
        });
        $(quantity_plus).click(function () {
            quantity_target.val(++quantity_);
        });
        }
        $.fn.Guantity = jQueryPlugin("Guantity", Guantity);
        $("[data-quantity]").Guantity();
})();
  

// QUANTITY INCREMENT CONTROLS END