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

function makePassword(length) {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }    
    return result;
}

var checkboxes = document.querySelectorAll('.form-check-input');
var categories = document.querySelectorAll('.category-item');
var thumbnails = document.querySelectorAll('.thumbnail');

const url = String(window.location.href).replaceAll('+', ' ');

let scheduled_function = false; 
const delay_by_in_ms = 500;
const results_div = $('.card-list');
const pagination_div = $('.pagination');
const endpoint = '/e-shop/';   

let ajax_call = function (endpoint, request_parameters) {
    $.getJSON(endpoint, request_parameters)
    .done(response => {  
        $('.search-button').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/></svg>');
        $('.infinite-container').css('display', 'grid');
        results_div.html(response['html_from_view']);
    })
}

function updateVariantDetails(event) {
    $('.product').addClass('disabled');

    var url = new URL(window.location);
    var id = url.href.substring(url.href.lastIndexOf('/') + 1);
    var selected_product = $('.thumbnail.selected').data('slug');

    url.searchParams.set('variant', selected_product);
    
    var request_parameters = {
        "variant_slug": selected_product,
    }

    window.history.pushState({}, '', url);

    $('#overlay').css('display', 'block');

    $.post({
		type: 'GET',
		url: '/products/' + id,
		data: request_parameters,
		headers: {'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function (response) {
            setTimeout(function() {
                $('#overlay').css('display', 'none');
                $('.product').removeClass('disabled');
                $('.product-info__wrapper').html(response['html_from_view']);
            }, delay_by_in_ms);
		},
        error: function (xhr, ajaxOptions, thrownError) {
            console.log("not working")
		}
	});
}

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

$(document).on('click', '.modal-btn', function(){
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

$(document).on('click', '.remove__notification', function(){
    $(this).parents('.card').removeClass('active');
})

$(document).on('click', '.cart-btn', function(){
    $('.cart-wrapper').css({'opacity': '1','z-index': '10'});
    $('.cart.card').addClass('open');
})

$(document).on('click', '.hide__cart', function(){
    $('.cart-wrapper').css({'opacity': '0','z-index': '-1'});
    $('.cart.card').removeClass('open');
})

// SAVE THE CHECKED CHECKBOX INPUTS TO THE LOCAL STORAGE
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

// SEARCH FUNCTIONALITY

$(document).on('click', '.close-badge', function(e){
    e.preventDefault();
    var value = $(this).parents('button').attr('data-val');
    var checked_input = $('input').filter(function() { return this.value == value });
    var selected_category = $('.category-item').filter(function() { return this.dataset.val == value });
    var unchecked = checked_input.prop("checked", false);
    selected_category.removeClass('selected');
    selected_category.css("--card-gradient", "66%");

    if (unchecked){
        $(this).parents('button').remove();
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


$(document).on('click', '.category-item, .close-badge', function(event){
	event.preventDefault(); 

    // Add button loader
    $('.search-button').html('<div class="lds-ring"><div></div><div></div><div></div><div></div></div>');

    // Disable eShop
    $('.infinite-container').css("display", 'block');
    $('.infinite-container').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');

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

    // Disable eShop
    $('.infinite-container').css("display", 'block');
    $('.infinite-container').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');

    // Initialize current url
    const url = new URL(window.location);

    // Disable eShop
    $('infinite-container').append('<div id="overlay"><div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div></div>');

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

$(window).on('load', function(){
    // Initialize current url
    const url = new URL(window.location);

    if (url.href.includes('e-shop/?')){
        // Disable eShop
        $('.infinite-container').css("display", 'block');
        $('.infinite-container').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');

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
            "is_ajax": "True"
        }

        if (scheduled_function) {
            clearTimeout(scheduled_function)
        } 
        window.history.pushState({}, '', url);
        scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters);
    }
})

// PRODUCT DETAILS

// PRODUCT GALLERY

thumbnails.forEach(function (thumbnail) {
    thumbnail.addEventListener('click', function () {
        var newSelection = thumbnail.dataset.big;
        $('.thumbnail').removeClass('selected');
        $(this).addClass('selected');
        var $img = $('.primary').css("background-image","url(" + newSelection + ")");
        $('.primary').empty().append($img.hide().fadeIn('slow'));
        if (url.includes(this.value)) {
            window.localStorage.setItem(this.id, this.dataset.slug);
        }
    });
});
// PRODUCT GALLERY END
  
// QUANTITY INCREMENT CONTROLS
$(document).ready(function(){
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

    function Guantity() {
        $(document).on('click', 'button[data-quantity-minus]', function(){
            document.querySelector('input[data-quantity-target]').value--;
        })
        $(document).on('click', 'button[data-quantity-plus]', function(){
            document.querySelector('input[data-quantity-target]').value++;
        })
    }
    $.fn.Guantity = jQueryPlugin("Guantity", Guantity);
    $("[data-quantity]").Guantity();
})
// QUANTITY INCREMENT CONTROLS END

$(document).on('click', '#down-slide', function(event){
    var windowSize = $(window).width();
    if (windowSize <= 768) {
        $('.img-list').animate({
            scrollLeft: "+=200px"
        }, "slow");
    }
    else {
        $('.img-list').animate({
            scrollTop: "+=200px"
        }, "slow");
    }
}) 

$(document).on('click', '#up-slide', function(event){
    var windowSize = $(window).width();
	event.preventDefault();
    if (windowSize <= 768) {
        $('.img-list').animate({
            scrollLeft: "-=200px"
        }, "slow");
    }
    else {
        $('.img-list').animate({
            scrollTop: "-=200px"
        }, "slow");
    }
}) 
// QUANTITY INCREMENT CONTROLS END


$(document).on('click', '.thumbnail', function(event){
	event.preventDefault(); 
    updateVariantDetails(event);
})

$(window).on('load', function(event){
    if (url.includes('products')){
        updateVariantDetails(event);
    }
})

// PRODUCT DETAILS END

// ADD TO CART
$(document).on('click', '#addCart', function(event){
    event.preventDefault();
    $(this).html('<div class="lds-ring" style="margin: auto"><div></div><div></div><div></div><div></div></div>');

    var url = new URL(window.location);
    var slug = url.href.substring(url.href.lastIndexOf('/') + 1);
    var selected_product = $('.thumbnail.selected').data('slug');
    var qty = $('input[data-quantity-target]').val();

    var request_parameters = {
        "variant_slug": selected_product,
        "quantity": qty,
    }

    $.post({
		type: 'POST',
		url: '/add-to-cart/' + slug,
		data: JSON.stringify(request_parameters),
		dataType: 'json',
		headers: {'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function (data) {
            // update cart notification product list
            if ($('price-item--discount').length) {
                var product_price = $('.price-item--discount').text();
            }
            else {
                var product_price = $('.price-item--regular').text();
            }
            $('.cart-notification__product').html(
                '<div class="cart-product__img border">'
                    + '<img src="' + $('.thumbnail.selected .thumbnail-image').css('background-image').replace(/^url\(['"](.+)['"]\)/, '$1') + '" alt="385w JA Solar - Solar Panel - Black Frame" width="80" height="auto" loading="lazy">' 
                + '</div>' +
                '<div class="cart-notification__product-info">' + 
                    '<h6>'+ $(".product__title h1").text() +'</h6>' +
                    '<span class="notification-product__feature">Qty: ' + qty + '</span>' + 
                    '<span class="notification-product__feature">Price: ' + product_price + '</span>'+
                    '<button class="plain-btn notification__product-remove" data-slug="'+ selected_product +'">Delete</button>' +
                '</div>'
            )
            setTimeout(function() {
                $('#addCart').html('Add to Cart');
                $('.cart-notification .card').addClass('active');
                // if error message length is more than 0    
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, delay_by_in_ms);
            setTimeout(function() {
                $('.cart-notification .card').removeClass('active');
            }, 10000); 
		},
        error: function (xhr, ajaxOptions, thrownError) {
            setTimeout(function() {
                $('#addCart').html('Add to Cart');
                $('.form__error').fadeIn('slow');
                $('.form__error').addClass('active');
                $('.error__content').html(xhr.responseJSON['err']);
            }, delay_by_in_ms);
            setTimeout(function() {
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, 10000); 
		}
	});
});
// ADD TO CART END

// UPDATE CART
$(document).on('change', 'input[data-update-quantity]', function(event){
    event.preventDefault();
    var new_quantity = $(this).val();
    var request_parameters = {'quantity': new_quantity}
    var slug = $(this).attr('data-update-quantity');

    // disable selected product
    $(this).parents('.cart-notification__product').addClass('disabled');

    $.post({
		type: 'POST',
		url: '/update-cart/' + slug,
		data: JSON.stringify(request_parameters),
		dataType: 'json',
		headers: {'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function (data) {
            setTimeout(function() {
                $('.cart-notification__product').removeClass('disabled');
                $("#cart-subtotal").load(location.href + " #cart-subtotal");

                // if error message length is more than 0
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, delay_by_in_ms);
		},
        error: function (xhr, ajaxOptions, thrownError) {
            $('.cart-notification__product').removeClass('disabled');
            setTimeout(function() {
                $('.form__error').fadeIn('slow');
                $('.form__error').addClass('active');
                $('.error__content').html(xhr.responseJSON['err']);
            }, delay_by_in_ms);
            setTimeout(function() {
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, 10000); 
		}
	});
})

$(document).on('click', 'button[data-remove-cart-item]', function(event){
    event.preventDefault();
    var $this = $(this);
    var slug = $this.attr('data-remove-cart-item');
    var request_parameters = {'slug': slug};
    $this.html('<div class="lds-ring" style="margin: auto"><div></div><div></div><div></div><div></div></div>');

    $.ajax({
		type: 'POST',
		url: '/remove-item/' + slug,
		data: JSON.stringify(request_parameters),
		dataType: 'json',
		headers: {'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function (data) {
            setTimeout(function() {
                $this.parents('.cart-notification__product').remove();
                $(".cart-quantity").load(location.href + " .cart-quantity");
                $("#cart-subtotal").load(location.href + " #cart-subtotal");

                if ($('.cart__body .cart-notification__product').length == 0) {
                    $('.cart__body').html('<div class="cart__empty-state">NO ITEMS FOUND</div>');
                    $('.cart__footer').remove();
                }

                // if error message length is more than 0
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, delay_by_in_ms);
		},
        error: function (xhr, ajaxOptions, thrownError) {
            $('.cart-notification__product').removeClass('disabled');
            setTimeout(function() {
                $('.form__error').fadeIn('slow');
                $('.form__error').addClass('active');
                $('.error__content').html("Something went wrong! Please try again.");
            }, delay_by_in_ms);
            setTimeout(function() {
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, 10000); 
		}
	});
})
// UPDATE CART END

// DOMContentLoaded
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

    thumbnails.forEach(function (el, i) {
        if (url.includes(el.dataset.slug)) {
            el.classList.add('selected');
            var newSelection = el.dataset.big;
            var $img = $('.primary').css("background-image","url(" + newSelection + ")");
            $('.primary').empty().append($img.hide().fadeIn('slow'));
            if ( i !== 0) {
                $('.thumbnail:first').removeClass('selected');
            }
        }
        else {
            window.localStorage.removeItem(el.id);
        }
    });
});

// DOMContentLoaded END

// LOCAL STORAGE 

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
// LOCAL STORAGE END

// SIGN UP & SIGN IN 
$(document).on('submit', '.login', function(event){
	event.preventDefault();
	var input_data = {
		'username': $('input[name="username"]').val(),
		'password': $('input[name="password"]').val(),
		'next': $('input[name="next"]').val(),
	}

    var $this = $(this);

	$this.addClass('disabled');

    $('.button-black').html('<div class="lds-ring"><div></div><div></div><div></div><div></div></div>');
  
	$.ajax({
		type: 'POST',
		url: '/login/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function (data) {
            setTimeout(function() {
                $this.removeClass('disabled');
                if (data['next_url']){
                    window.location.href = data['next_url'];
                }
                else {
                    window.location.href = '/';
                }
            }, delay_by_in_ms);
		},
        error: function (xhr, ajaxOptions, thrownError) {
            setTimeout(function() {
                $this.removeClass('disabled');
                $('.button-black').html('Sign in');
                var list_of_errors = xhr.responseJSON['error'];
                $('.form__error').fadeIn('slow');
                $('.form__error').addClass('active');

                for(let i = 0; i < list_of_errors.length; i++){
                    var newItem = list_of_errors[i];
                    $( ".error__content" ).html( newItem );
                }
            }, delay_by_in_ms);
            setTimeout(function() {
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, 10000); 
		}
	}); 
});

const account_types = []

$(document).on('click', '.local-account__type', function(event){
    event.preventDefault();
    var $this = $(this);
    
    account_types.push($this.data('account-type'));

    $('#flexibleSignup').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');
    setTimeout(function() {
        if ($this.data('account-type') == 'individual') {
            const inv_signup = '<form class="user signup">' +
                    '<h1>Create Account</h1>'+

                    '<div class="form__error small" role="alert">' +
                        '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="red" class="bi bi-exclamation-circle-fill" viewBox="0 0 16 16">' +
                            '<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>' +
                        '</svg>' +
                        '<span class="error__content">' +
                        '</span>' +
                    '</div>' +
                    '<div class="input-group">'+ 
                        '<div class="field">'+
                            '<input id="firstnameField" type="text" name="first_name" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="firstnameField">First Name</label>'+
                        '</div>'+
                    '</div>'+
                
                    '<div class="input-group">'+
                        '<div class="field">'+
                            '<input id="lastnameField" type="text" name="last_name" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="lastnameField">Last Name</label>'+
                        '</div>'+
                    '</div>'+
                
                    '<div class="input-group">'+
                        '<div class="field">'+
                            '<input id="emailuserField" type="email" name="email" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="emailuserField">Email</label>'+
                        '</div>'+
                    '</div>'+
                
                    '<div class="input-group">'+
                        '<div class="field">'+
                            '<input id="usernameField" type="text" name="username" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="usernameField">Username</label>'+
                        '</div>'+
                    '</div>'+
                    
                    '<div class="input-group">'+
                        '<div class="field">'+
                            '<input id="passwordField" type="password" name="password1" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="passwordField">Password</label>'+
                        '</div>'+
                    '</div>'+
                    '<div class="input-group">'+
                        '<div class="field">'+
                            '<input id="passwordField" type="password" name="password2" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="passwordField">Confirm Password</label>'+
                        '</div>'+
                    '</div>'+
                    '<div class="signup__agreement">'+
                        '<div class="choice-input-wrapper ">'+
                            '<input type="checkbox" name="agreement" class="form-check-input mt-0" autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true"> '+
                            '<label class="form-check-label small" for="">Yes, I understand and agree to the Upwork Terms of Service, including the User Agreement and Privacy Policy.</label>'+
                        '</div>'+
                    '</div>'+

                    '<div class="or or--x" aria-role="presentation"> OR </div>' +

                    '<div id="googlebtnDiv"></div>' +
                    '<div class="signup__recover">'+
                        '<a href="{% url "account_login" %}" class="recover small">Already have an account?</a>'+
                    '</div>'+
                    '<div id="signin">'+
                        '<button class="btn button-black">Sign Up</button>'+
                    '</div>'+
                '</form>'
            $('#flexibleSignup').html(inv_signup);
        }
        else if ($this.data('account-type') == 'business'){
            const  business_signup = '<form class="user signup">' +
                    '<h1>Create Account</h1>'+
                    '<div class="form__error small" role="alert">' +
                        '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="red" class="bi bi-exclamation-circle-fill" viewBox="0 0 16 16">' +
                            '<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>' +
                        '</svg>' +
                        '<span class="error__content">' +
                        '</span>' +
                    '</div>' +
                    '<div class="input-group">'+
                        '<div class="field">'+
                            '<input id="companynameField" type="text" name="company_name" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="companynameField">Company Name</label>'+
                        '</div>'+
                    '</div>'+

                    '<div class="input-group">'+
                        '<div class="field">'+
                            '<input id="emailuserField" type="email" name="email" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="emailuserField">Email</label>'+
                        '</div>' +
                    '</div>' +

                    '<div class="input-group">'+
                        '<div class="field">'+
                            '<input id="passwordField" type="password" name="password1" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="passwordField">Password</label>'+
                        '</div>'+
                    '</div>'+
                    '<div class="input-group">'+
                        '<div class="field">'+
                            '<input id="passwordField" type="password" name="password2" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true">'+
                            '<label for="passwordField">Confirm Password</label>'+
                        '</div>'+
                    '</div>'+
                    '<div class="signup__agreement">'+
                        '<div class="choice-input-wrapper ">'+
                            '<input type="checkbox" name="agreement" class="form-check-input mt-0">'+
                            '<label class="form-check-label small" for="">Yes, I understand and agree to the Upwork Terms of Service, including the User Agreement and Privacy Policy.</label>' +
                        '</div>' +
                    '</div>' +

                    '<div class="or or--x" aria-role="presentation"> OR </div>' +
                    
                    '<div id="googlebtnDiv"></div>' +
                    '<div class="signup__recover">' +
                        '<a href="{% url "account_login" %}" class="recover small">Already have an account?</a>' +
                    '</div>' +
                    '<div id="signin">' +
                        '<button class="btn button-black">Sign Up</button>' +
                    '</div>' +
                '</form>' 
            $('#flexibleSignup').html(business_signup);
        }
        // generate google button
        google.accounts.id.initialize({
            client_id: "86282417486-l5morm5n1a4pa39ftt9bllrdm9acfinv.apps.googleusercontent.com",
            callback: handleCredentialResponse
        });
        google.accounts.id.renderButton(
            document.getElementById("googlebtnDiv"),
            { theme: "outline", size: "large" }
        );
        google.accounts.id.prompt();
    }, delay_by_in_ms);
})

$(document).on('click', '.google-account__type', function(event){
    event.preventDefault();
    var $this = $(this);

    $('.user__type.selected').removeClass('selected');
    $this.addClass('selected');

    account_types.push($this.data('account-type'));
    $('.extra-fields').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');
    
    setTimeout(function() {
        if ($this.data('account-type') == 'individual') {
            console.log("individual");
            $('.extra-fields').html('<div class="input-group"><div class="field"><input id="usernameField" type="text" name="username" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true"><label for="usernameField">Username</label></div></div>')
        }
        else if ($this.data('account-type') == 'business'){
            $('.extra-fields').html('<div class="input-group"><div class="field"><input id="companynameField" type="text" name="company_name" placeholder=" " autocapitalize="off" autocomplete="off" autocorrect="off" aria-required="true"><label for="companynameField">Company Name</label></div></div>')
        }
    }, delay_by_in_ms);
})

$(document).on('submit', '.signup', function(event){
	event.preventDefault();

    if ($('input[name="agreement"]').is(":checked")) {
        var agreement = true
    }
    else {
        var agreement = false
    }
	var input_data = {
        'account_type': account_types[0],
		'first_name': $('input[name="first_name"]').val(),
		'last_name': $('input[name="last_name"]').val(),
		'username': $('input[name="username"]').val(),
		'email': $('input[name="email"]').val(),
		'password1': $('input[name="password1"]').val(),
		'password2': $('input[name="password2"]').val(),
		'company_name': $('input[name="company_name"]').val(),
        'provider': 'Email',
		'agreement': agreement,
	}

    var $this = $(this);

	$this.addClass('disabled');

    $('.button-black').html('<div class="lds-ring"><div></div><div></div><div></div><div></div></div>');
  
	$.ajax({
		type: 'POST',
		url: '/sign-up/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function (data) {
            setTimeout(function() {
                $this.removeClass('disabled');
                window.location.href = '/login/';
            }, delay_by_in_ms);
		},
        error: function (xhr, ajaxOptions, thrownError) {
            setTimeout(function() {
                $this.removeClass('disabled');
                $('.button-black').html('Sign up');
                var list_of_errors = xhr.responseJSON['error'];
                $('.form__error').fadeIn('slow');
                $('.form__error').addClass('active');

                for(let i = 0; i < list_of_errors.length; i++){
                    var newItem = list_of_errors[i];
                    $( ".error__content" ).html( newItem );
                }
            }, delay_by_in_ms);
            setTimeout(function() {
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, 10000); 
		}
	}); 
});
// SIGN UP & SIGN IN END


// GOOGLE AUTHENTICATION
function handleCredentialResponse(response) {
    var input_data = {
        'account_type': account_types[0],
        'auth_token': String(response.credential),
	}
    $.ajax({
		type: 'POST',
		url: '/google-login/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function (data) {
            setTimeout(function() {
                var url = String(new URL(window.location.href));
                if (url.includes('sign-up')) {
                    $('.user').removeClass('choose-account-type');
                    $('.user').html('<div class="user google-acc__card border card" style="display:none">' +
                        '<h4>Continue with Google</h4>' +
                        '<div class="form__error small" role="alert">' +
                            '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="red" class="bi bi-exclamation-circle-fill" viewBox="0 0 16 16">' +
                                '<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>' +
                            '</svg>' +
                            '<span class="error__content">' +
                            '</span>' +
                        '</div>' +
                        '<div class="google-acc-details">' +
                            '<img width="30" height="30" src="'+ data['data'].picture +'" alt="' + data['data'].email + '" style="border-radius: 50%;">' +
                            '<span class="google__username">' + data['data'].email + '</span>' +
                        '</div>' +
                        '<input type="hidden" name="first_name" value="'+ data['data'].given_name +'">' +
                        '<input type="hidden" name="last_name" value="'+ data['data'].family_name +'">' +
                        '<div class="choose-account-type">' +
                            '<button class="plain-btn border user__type google-account__type" data-account-type="individual" type="button">' +
                                '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" fill="currentColor" class="bi bi-person" viewBox="0 0 16 16">' +
                                    '<path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"></path>' +
                                '</svg>' +
                                '<h6>Individual User</h6>' +
                            '</button>' +
                            '<button class="plain-btn border user__type google-account__type" data-account-type="business" type="button">' +
                                '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" fill="currentColor" class="bi bi-briefcase" viewBox="0 0 16 16">' +
                                    '<path d="M6.5 1A1.5 1.5 0 0 0 5 2.5V3H1.5A1.5 1.5 0 0 0 0 4.5v8A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-8A1.5 1.5 0 0 0 14.5 3H11v-.5A1.5 1.5 0 0 0 9.5 1h-3zm0 1h3a.5.5 0 0 1 .5.5V3H6v-.5a.5.5 0 0 1 .5-.5zm1.886 6.914L15 7.151V12.5a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5V7.15l6.614 1.764a1.5 1.5 0 0 0 .772 0zM1.5 4h13a.5.5 0 0 1 .5.5v1.616L8.129 7.948a.5.5 0 0 1-.258 0L1 6.116V4.5a.5.5 0 0 1 .5-.5z"></path>' +
                                '</svg>' +
                                '<h6>Business User</h6>' +
                            '</button>' +
                        '</div>' +
                        '<div class="extra-fields"></div>' +
                        '<div class="signup__agreement">' +
                            '<div class="choice-input-wrapper ">' +
                                '<input type="checkbox" name="agreement" class="form-check-input mt-0">' +
                                '<label class="form-check-label small" for="">Yes, I understand and agree to the Upwork Terms of Service, including the User Agreement and Privacy Policy.</label>' +
                            '</div>' +
                        '</div>' +
                    
                        '<div id="signin">' +
                            '<button class="btn button-black" id="googleAuthenticationBtn">Create account</button>' +
                        '</div>' +
                    '</div>');
                    $('.google-acc__card').fadeIn('slow');
                }
                //var url = String(new URL(window.location.href));
                //if (url.includes('login')) {
                //    window.location.href = '/';
                //}
                //else {
                //    window.location.href = '/login/';
                //}
            }, delay_by_in_ms);
		},
        error: function (xhr, ajaxOptions, thrownError) {
            setTimeout(function() {
                var list_of_errors = xhr.responseJSON['error'];
                $('.form__error').fadeIn('slow');
                $('.form__error').addClass('active');

                for(let i = 0; i < list_of_errors.length; i++){
                    var newItem = list_of_errors[i];
                    $( ".error__content" ).html( newItem );
                }
            }, delay_by_in_ms);
            setTimeout(function() {
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, 10000); 
		}
	}); 
}

$(document).on('click', '#googleAuthenticationBtn', function(event){
    event.preventDefault();

    if ($('input[name="agreement"]').is(":checked")) {
        var agreement = true
    }
    else {
        var agreement = false
    }

    var password = makePassword(25);

    var input_data = {
        'account_type': $('.google-account__type.selected').data('account-type'),
        'first_name': $('input[name="first_name"]').val(),
        'last_name': $('input[name="last_name"]').val(),
        'company_name': $('input[name="company_name"]').val(),
        'username': $('input[name="username"]').val(),
        'email': $('.google__username').text(),
        'password1': password,
        'password2': password,
        'agreement': agreement,
        'provider': 'Google'
	}

    console.log(input_data);

    $('.button-black').html('<div class="lds-ring"><div></div><div></div><div></div><div></div></div>');

    $.ajax({
		type: 'POST',
		url: '/sign-up/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function (data) {
            setTimeout(function() {
                window.location.href = '/';
            }, delay_by_in_ms);
		},
        error: function (xhr, ajaxOptions, thrownError) {
            setTimeout(function() {
                var list_of_errors = xhr.responseJSON['error'];
                $('.button-black').html('Create account');
                $('.form__error').fadeIn('slow');
                $('.form__error').addClass('active');

                for(let i = 0; i < list_of_errors.length; i++){
                    var newItem = list_of_errors[i];
                    $( ".error__content" ).html( newItem );
                }
            }, delay_by_in_ms);
            setTimeout(function() {
                $('.form__error').fadeOut('slow');
                $('.form__error').removeClass('active');
            }, 10000); 
		}
	}); 
})

window.onload = function () {
    var url = String(new URL(window.location.href));
    if (url.includes('sign-up') || url.includes('login')) {
        google.accounts.id.initialize({
            client_id: "86282417486-l5morm5n1a4pa39ftt9bllrdm9acfinv.apps.googleusercontent.com",
            callback: handleCredentialResponse
        });
        google.accounts.id.renderButton(
            document.getElementById("googlebtnDiv"),
            { theme: "outline", size: "large" }
        );
        google.accounts.id.prompt();
    }
}
// GOOGLE AUTHENTICATION END