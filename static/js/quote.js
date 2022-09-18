// Switch pages
$(document).on('click', '.btn-next', function(event){
    event.preventDefault();
    var $this = $(this);
    var $href = $this.data('href');
    var $nextpageName = $this.data('next-page');
    var steps = document.querySelectorAll('.step');

    // change url 
    if ($href) {
        if (!$('.form__error.active').length) {
            var url = new URL(window.location);

            url.searchParams.set('name', $href);
            if ($nextpageName) {
                url.searchParams.set('page', $nextpageName);
            }
            window.history.pushState({}, '', url);
            $("html, body").animate({ scrollTop: 0 }, "fast");
        }
    }

    // update progress bar on switching page
    if ($href) { 
        if (!$('.form__error.active').length) {
            steps.forEach(function (item, index) {
                if (item.dataset.step == $href) {
                    // complete the previous step
                    steps[index-1].classList.remove('active');
                    steps[index-1].className += " step-completed";

                    // switch to the current step
                    item.classList.add('active')
                }
            });
        }
    }

    if ($this.is("#validatePersonalInfo")) {
        validatePersonalInformation();
    }
    else if ($this.is("#validateElectricityBill")){
        validateElectricityBill();
    }
    else if ($this.is("#validateInstallationType")) {
        validateInstallationType();
    }
    else if ($this.is("#validateRoofStyle")) {
        validateRoofStyle();
    }
    else if ($this.is("#confirmSelectedPanel")) {
        confirmSelectedPanel();
    }
    else if ($this.is("#confirmSelectedFitting")) {
        confirmSelectedFitting();
    }
    else if ($this.is("#confirmSelectedInverter")) {
        confirmSelectedInverter();
    }
    else if ($this.is("#validateCableLength")) {
        validateCableLength();
    }
    else if ($this.is("#confirmInvBatteryLength")) {
        confirmInvBatteryLength();
    }
    else if ($this.is("#confirmStorageCable")) {
        confirmStorageCable();
    }
    else if ($this.is("#validateRoofDimensions")) {
        validateRoofDimensions();
    }

    // remove error content after 10 seconds
    setTimeout(function() {
        $('.form__error').fadeOut('slow');
        $('.form__error').removeClass('active');
    }, 10000); 
})

$(document).on("click", ".skip-btn", function(){
    var $this = $(this);
    var $href = $this.data('href');
    var $nextpage = $this.data('skip');
    var $nextpageName = $this.data('next-page');
    var steps = document.querySelectorAll('.step');
    
    // change url 
    if ($href) {
        var url = new URL(window.location);

        url.searchParams.set('name', $href);
        url.searchParams.set('page', $nextpageName);
        window.history.pushState({}, '', url);
        $("html, body").animate({ scrollTop: 0 }, "fast");
    }
    
    // update progress bar on skipping page
    if ($href) { 
        if (!$('.form__error.active').length) {
            steps.forEach(function (item, index) {
                if (item.dataset.step == $href) {
                    // complete the previous step
                    steps[index-1].className += " step-completed";

                    // switch to the current step
                    item.classList.add('active')
                }
            });
        }
    }

    var html = "/templates/quote/quote_pages/" + $nextpage + ".html"
    $.get(html, function(html_string)
    {
        $("#content").html(html_string);
    },'html');
})

$(document).on("click", ".btn-back", function(){
    var $this = $(this);
    var $href = $this.data('href');
    var $previouspage = $this.data('back');
    var url = new URL(window.location);
    var steps = document.querySelectorAll('.step');
    
    // change url 
    if ($href) {
        url.searchParams.set('name', $href);
        url.searchParams.set('page', $previouspage);
        window.history.pushState({}, '', url);

        if (!$('.form__error.active').length) {
            steps.forEach(function (item, index) {
                if (item.dataset.step == $href) {
                    // complete the previous step
                    if (index != 0) {
                        steps[index-1].classList.remove('active');
                    }
                    steps[index + 1].classList.remove('active');
                    //steps[index].className += " step-completed";

                    // switch to the current step
                    item.classList.add('active')
                }
            });
        }
    }

    if(url.href.includes('section?name') && (url.searchParams.get('page')) != 'parts') {
        var html = "/templates/quote/quote_pages/" + $previouspage + ".html"
        $.get(html, function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
    else if ((url.searchParams.get('page')) == 'parts') {
        loadProducts();
    }
})

$(document).on('click', '.choice-card, .product-choice', function(){
    // uncheck other card(s)
    $('.choice-card').removeClass('selected');
    $('.product-choice').removeClass('selected');
    $(this).addClass('selected');
})


$(document).on('click', '#installation__type .choice-card', function(){
    var $this = $(this).find('.choice-text');
    var url = new URL(window.location);
    if ($this.text() == 'Roof') {
        url.searchParams.set('page', "single-phase");
        $.get("/templates/quote/quote_pages/single-phase.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
    else if ($this.text() == 'Standalone') {
        var url = new URL(window.location);
        url.searchParams.set('page', "standalone-installation");
        $.get("/templates/quote/quote_pages/standalone-installation.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
    window.history.pushState({}, '', url);
})

$(document).on('click', '#standalone__installation .choice-card', function(){
    //if ($('.choice-card.selected .choice-text').text() == 'Campervan') {
    if ($(this).find('.choice-text').text() == 'Campervan') {
        $('#content').html(
            '<div class="page-title-wrap text-center">' +
                '<h4 class="sub-title">Please see the campervan bundles in our shop</h4>' +
            '</div>' +
            '<div class="btn-group-footer">' +
                '<a data-back="standalone-installation" type="button" class="btn primary-btn btn-back">' +
                    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">' +
                        '<path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"></path>' +
                    '</svg>' +
                    'Back' +
                '</a>' +
            '</div>'
        );
    }
    else {
        $('#content').html(
            '<div class="page-title-wrap text-center">' +
                '<h4 class="sub-title">Please call us directly on 08000016802</h4>' +
                '<a href="{% url "shop" %}" type="button" class="btn button-black" style="width: 150px;margin: 2rem auto auto;">Shop</a>' +
            '</div>' +
            '<div class="btn-group-footer">' +
                '<a data-back="standalone-installation" type="button" class="btn primary-btn btn-back">' +
                    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">' +
                        '<path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"></path>' +
                    '</svg>' +
                    'Back' +
                '</a>' +
            '</div>'
        );
    }
})

$(document).on('click', '#singlePhase button', function(){
    var $this = $(this);
    if ($this.text() == 'No') {
        $('#content').html(
            '<div class="page-title-wrap text-center">' +
                '<h4 class="sub-title">Please call us directly on 08000016802</h4>' +
            '</div>' +
            '<div class="btn-group-footer">' +
                '<a data-back="single-phase" type="button" class="btn primary-btn btn-back">' +
                    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">' +
                        '<path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"></path>' +
                    '</svg>' +
                    'Back' +
                '</a>' +
            '</div>'
        );
    }
    else {
        var url = new URL(window.location);
        url.searchParams.set('page', "spare-way");
        window.history.pushState({}, '', url);
        $.get("/templates/quote/quote_pages/spare-way.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
})

$(document).on('click', '#spareWay button', function(){
    var $this = $(this);
    var url = new URL(window.location);
    if ($this.text() == 'No') {
        $('#content').html(
            '<div class="page-title-wrap text-center">' +
                '<h4 class="sub-title">Please call us directly on 08000016802</h4>' +
            '</div>' +
            '<div class="btn-group-footer">' +
                '<a data-back="single-phase" type="button" class="btn primary-btn btn-back">' +
                    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">' +
                        '<path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"></path>' +
                    '</svg>' +
                    'Back' +
                '</a>' +
            '</div>'
        );
    }
    else {
        url.searchParams.set('page', "roof-style");
        window.history.pushState({}, '', url);
        $.get("/templates/quote/quote_pages/roof-style.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
})

$(document).on('click', '#storageSystem button', function() {
    var $this = $(this);
    if ($this.text() == 'Yes') {
        $.get("/templates/quote/quote_pages/storage-system-size.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
    else {
        $.get("/templates/quote/quote_pages/summary.html", function(html_string)
        {
            $(".quote-builder-container").html(html_string);
        },'html');
    }
})

$(document).on('click', '#extraRequiremet button, #skipSummary', function() {
    var $this = $(this);
    var url = new URL(window.location);
    if ($this.hasClass('primary-btn')) {
        var extra_requirement = $this.text();
        localStorage.setItem("extra_requirement", extra_requirement);
    }
    $.get("/templates/quote/quote_pages/summary.html", function(html_string)
    {
        $(".quote-builder-container").html(html_string);
    },'html');
    url.searchParams.set('name', "Summary");
    url.searchParams.set('page', "summary");
    window.history.pushState({}, '', url);
})

// upload products on window load

const quote_url = '/upload-products/';
const content = $('#content');
const delay_100_ms = 100

const ajax_func = function (quote_url, request_parameters) {
    $.getJSON(quote_url, request_parameters)
    .done(response => {  
        setTimeout(function() {
            content.html(response['html_from_view']);
        }, delay_100_ms);
    })
}

function loadProducts() {
    var url = new URL(window.location);
	const request_parameters = {
		"product_type": url.searchParams.get('name'),
	}
    $('#content').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');

    if (scheduled_function) {
        clearTimeout(scheduled_function)
    } 
    scheduled_function = setTimeout(ajax_func, delay_100_ms, quote_url, request_parameters);
}

$(document).on('click', '.step.step-completed', function(e){
    e.preventDefault();
    var url = new URL(window.location);
    var $this = $(this);
    var $last_completed_step = $('.step.step-completed').last();
    $last_completed_step.next().removeClass('active');
    $last_completed_step.prevAll().removeClass('active');
    $this.nextAll('.step-completed').removeClass('active');
    $this.prevAll('.step').removeClass('active');
    $this.addClass('active');
    url.searchParams.set('name', $this.data('step'));
    url.searchParams.set('page', $this.data('page'));
    window.history.pushState({}, '', url);

    updateCurrentSection();
})

function updateCurrentSection() {
    var url = new URL(window.location);
    if (url.href.includes("build-quote") && !url.href.includes("page") || !url.href.includes("section?name")){
        url.searchParams.set('name', "Personal Information");
        url.searchParams.set('page', "personal-information");
        window.history.pushState({}, '', url);
        $('#content').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');
        setTimeout(function() {
            $.get("/templates/quote/quote_pages/personal-information.html", function(html_string)
            {
                $('#content').html(html_string);
            },'html');
        }, delay_by_in_ms);
    }
    else if ((url.searchParams.get('page')) == 'summary') {
        $('.quote-builder-container').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');
        setTimeout(function() {
            $.get("/templates/quote/quote_pages/summary.html", function(html_string)
            {
                $(".quote-builder-container").html(html_string);
            },'html');
        }, delay_by_in_ms);
    }
    else if ((url.searchParams.get('page')) == 'parts') {
        loadProducts();
    }
    else if(url.href.includes('section?name') && (url.searchParams.get('page')) != 'parts') {
        $('#content').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');
        var html = "/templates/quote/quote_pages/" + url.searchParams.get('page') + ".html"
        setTimeout(function() {
            $.get(html, function(html_string)
            {
                $("#content").html(html_string);
            },'html');
        }, delay_by_in_ms);
    }
    else if ((url.searchParams.get('page')) == 'Summary') {
        $('#content').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');
        setTimeout(function() {
            $.get("/templates/quote/quote_pages/summary.html", function(html_string)
            {
                $('.quote-builder').html(html_string);
            },'html');
        }, delay_by_in_ms);
    }

    // update progress bar on page reload
    var current_step = $('.step[data-step="' + url.searchParams.get('name') + '"');
    $(current_step).addClass('active');
    $(current_step).prevAll('.step').addClass('step-completed').removeClass('active');
}

$(window).on('load popstate hashchange', function(){
    updateCurrentSection();
})

// display data saved with localStorage 
$(document).on("DOMSubtreeModified", "#content", function(){
    var inputs = document.querySelectorAll('input');
    
    // fill in inputs
    inputs.forEach(function (item, index) {
        var saved_data = localStorage.getItem(item.id);
        if (saved_data !== null) {
            document.getElementById(item.id).value = saved_data;
        }
    });
})

$(document).on("DOMNodeInserted", ".card-list", function(){
    var productCards = document.querySelectorAll('.product-choice');

    // auto-select products
    productCards.forEach(function (item, index) {
        var selected_panel = localStorage.getItem('panel_slug');
        var selected_fitting = localStorage.getItem('fitting_slug');
        var selected_inverter = localStorage.getItem('inverter_slug');

        if (item.dataset.slug == selected_panel || (item.dataset.slug == selected_fitting) || (item.dataset.slug == selected_inverter)) {
            item.classList.add('selected');
        }
    })
})

function displayError(){
    $('.form__error').fadeIn('slow');
    $('.form__error').css('display', 'flex');
    $('.form__error').addClass('active');
}

function validateEmail($email) {
    var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
    return emailReg.test($email);
}

function validatePersonalInformation(){
    if (!$("#housetypeField").val()) {
        displayError()
        $('.error__content').html("Type of house: This field cannot be blank")
    }
    else if (!$("#nobedroomsField").val()) {
        displayError()
        $('.error__content').html("Number of bedrooms: This field cannot be blank")
    }
    else if (!$("#nofloorsField").val()) {
        displayError()
        $('.error__content').html("Number of floors: This field cannot be blank")
    }
    else if (!$("input[name='agreement']").is(':checked')) {
        displayError()
        $('.error__content').html("You must agree to Solar Panels Terms of Service, including the User Agreement and Privacy Policy.")
    }
    else if (!(validateEmail($('input[name="email"]').val()))) {
        displayError()
        $('.error__content').html("You have entered an invalid email address!")
    }
    else{
        var inputs = document.querySelectorAll('input');
        inputs.forEach(function (item, index) {
            localStorage.setItem(item.id, item.value);
        });
        var url = new URL(window.location);
        url.searchParams.set('name', 'monthly-bill-rate');
        url.searchParams.set('page', 'bill-rate');
        window.history.pushState({}, '', url);
        $.get("/templates/quote/quote_pages/bill-rate.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
}

function validateElectricityBill(){
    if (parseInt($("#billrateField").val()) <= 0) {
        displayError()
        $('.error__content').html("Amount cannot be less than or equal to 0 USD")
    }
    else{
        var input = document.getElementById('billrateField');
        localStorage.setItem(input.id, input.value);

        var url = new URL(window.location);
        url.searchParams.set('page', "installation-type");
        window.history.pushState({}, '', url);
        $.get("/templates/quote/quote_pages/installation-type.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
}
$(document).on('submit', '#billRateForm', function(e){
    e.preventDefault();
    validateElectricityBill();
})

function validateInstallationType(){
    if (!$('.choice-card.selected').length) {
        displayError()
        $('.error__content').html("You should choose one of the options");
    }
    else {
        var url = new URL(window.location);
        if ($('.choice-card.selected .choice-text').text() == 'Standalone') {
            url.searchParams.set('page', "single-phase");
            $.get("/templates/quote/quote_pages/standalone-installation.html", function(html_string)
            {
                $("#content").html(html_string);
            },'html');
        }
        else if ($('.choice-card.selected .choice-text').text() == 'Roof') {
            url.searchParams.set('page', "standalone-installation");
            var selected_choice = $('.choice-card.selected .choice-text').text();
            localStorage.setItem("installation_type", selected_choice);
            $.get("/templates/quote/quote_pages/single-phase.html", function(html_string)
            {
                $("#content").html(html_string);
            },'html');
        }
        window.history.pushState({}, '', url);
    }
}

function validateRoofStyle(){
    if (!$('.choice-card.selected').length) {
        displayError()
        $('.error__content').html("You should choose one of the options");
    }
    else {
        var selected_choice = $('.choice-card.selected .choice-text').text();
        localStorage.setItem("roof_style", selected_choice);
        var url = new URL(window.location);
        url.searchParams.set('page', 'roof-dimensions');
        window.history.pushState({}, '', url);
        $.get("/templates/quote/quote_pages/roof-dimensions.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
}

function validateRoofDimensions(){
    if (!$("#widthField").val()) {
        displayError();
        $('.error__content').html("This field cannot be blank");
    }
    else if (!$("#heightField").val()) {
        displayError();
        $('.error__content').html("This field cannot be blank");
    }
    else if (parseInt($("#heightField").val()) <= 0) {
        displayError();
        $('.error__content').html("Roof's height cannot be less than or equal to zero");
    }
    else if (parseInt($("#widthField").val()) <= 0) {
        displayError();
        $('.error__content').html("Roof's width cannot be less than or equal to zero");
    }
    else {
        var inputs = document.querySelectorAll('input');
        inputs.forEach(function (item, index) {
            localStorage.setItem(item.id, item.value);
        });
        var url = new URL(window.location);
        url.searchParams.set('page', 'parts');
        window.history.pushState({}, '', url);
        loadProducts();
    }
}

$(document).on('change', '#cablelengthField', function(){
    var $this = $(this);
    var input_val = $this.val();
    localStorage.setItem($this.attr('id'), input_val);

    // add %20 fat
    var fattened_value = parseFloat(input_val) + parseFloat((input_val*0.2));
    localStorage.setItem("fattened_consumer_cable_length", fattened_value);
})

function validateCableLength(){
    if (!$("#cablelengthField").val()) {
        displayError()
        $('.error__content').html("This field cannot be blank")
    }
    else if (parseInt($("#cablelengthField").val()) <= 0) {
        displayError();
        $('.error__content').html("Invalid length value!");
    }
    else{
        var url = new URL(window.location);
        url.searchParams.set('name', 'Storage System');
        url.searchParams.set('page', 'storage-system');
        window.history.pushState({}, '', url);
        $.get("/templates/quote/quote_pages/storage-system.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
}

function possibleMaxPanels() {
    var panel_height = Math.round(parseFloat($('#panel-height').text()));
    var panel_width = Math.round(parseFloat($('#panel-width').text()));
    var roof_width = Math.round(parseFloat(localStorage.getItem("widthField")));
    var roof_height = Math.round(parseFloat(localStorage.getItem("heightField")));

    var row = roof_height/panel_height;
    var column = roof_width/panel_width;

    return (row * column).toFixed(2)
}

function confirmSelectedPanel() {
    if ($('.quantity-input').val() > $('.quantity-input').attr('max')) {
        displayError()
        $('.error__content').html("You cannot order more than the maximum quantity");
    }
    else if ($('.quantity-input').val() > possibleMaxPanels()) {
        displayError()
        $('.error__content').html("Based on your roof dimensions, max amount of panels you can order is "+ possibleMaxPanels() +"");
    }
    else {
        var slug = $('.product-choice.selected').data('slug');
        var quantity = $('input[name="quantity-input"]').val();

        localStorage.setItem("panel_slug", slug);
        localStorage.setItem("quantity", quantity);
        
        var url = new URL(window.location);
        url.searchParams.set('page', 'parts');
        window.history.pushState({}, '', url);
        loadProducts();
    }
}

function confirmSelectedFitting() {
    var slug = $('.product-choice').data('slug');
    localStorage.setItem("fitting_slug", slug);
    var url = new URL(window.location);

    url.searchParams.set('page', 'parts');
    window.history.pushState({}, '', url);
    loadProducts();
}

$(document).on('click', '#storageSystemSize button', function() {
    var $this = $(this);
    localStorage.setItem("storage_size", $this.text());

    var url = new URL(window.location);
    url.searchParams.set('name', "Cable Length from Battery to Inverter");
    url.searchParams.set('page', "cable-length-battery-inverter");
    window.history.pushState({}, '', url);
    $.get("/templates/quote/quote_pages/cable-length-battery-inverter.html", function(html_string)
    {
        $("#content").html(html_string);
    },'html');
})

function confirmSelectedInverter(){
    if (!$('.product-choice.selected').length) {
        displayError()
        $('.error__content').html("You should choose an inverter");
    }
    else {
        var slug = $('.product-choice').data('slug');
        localStorage.setItem("inverter_slug", slug);
        var url = new URL(window.location);
        url.searchParams.set('page', 'cable-length');
        window.history.pushState({}, '', url);
        $.get("/templates/quote/quote_pages/cable-length.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
}

$(document).on('change', '#cablelengthbtoinvField', function(){
    console.log("Asd");
    var $this = $(this);
    var input_val = $this.val();
    console.log(input_val);
    localStorage.setItem($this.attr('id'), input_val);

    // add %20 fat
    var fattened_value = parseFloat(input_val) + parseFloat((input_val*0.2));
    localStorage.setItem("fattened_cable_length", fattened_value);
})

function confirmInvBatteryLength(){
    if (parseInt($("#cablelengthbtoinvField").val()) <= 0) {
        displayError();
        $('.error__content').html("Invalid length value!");
    }
    else if (!($("#cablelengthbtoinvField").val()).length) {
        displayError();
        $('.error__content').html("This field cannot be blank!");
    }
    else {
        var url = new URL(window.location);
        url.searchParams.set('page', 'storage-cable');
        window.history.pushState({}, '', url);
        $.get("/templates/quote/quote_pages/storage-cable.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
}

function confirmStorageCable(){
    if (parseInt($("#storagecableField").val()) <= 0) {
        displayError();
        $('.error__content').html("Invalid length value!");
    }
    else if (!$("#storagecableField").val().length) {
        displayError();
        $('.error__content').html("This field cannot be blank");
    }
    else {
        var input = document.getElementById("storagecableField");
        localStorage.setItem(input.id, input.value);
        var url = new URL(window.location);
        url.searchParams.set('page', 'extra-help');
        window.history.pushState({}, '', url);
        $.get("/templates/quote/quote_pages/extra-help.html", function(html_string)
        {
            $("#content").html(html_string);
        },'html');
    }
}

$(document).on('click', '.quote-builder .modal-btn', function(e){
    e.preventDefault();
    var $this = $(this);
    var slug = $('.product-choice.selected').data('slug');
    $(this).html('<div class="lds-ring"><div></div><div></div><div></div><div></div></div>');

    $.ajax({
		type: 'GET',
		url: '/variant-details/' + slug,
		dataType: 'json',
		headers: {'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function (response) {
            $this.html('Choose Panel');
            $('.modal-window').css({
                'visibility': 'visible',
                'opacity': 1,
                'pointer-events': 'auto',
            });
            $('.modal-content').html('<div class="lds-ellipsis" style="display: flex;-webkit-box-pack: center;justify-content: center;margin: auto;"><div></div><div></div><div></div><div></div></div>');
        
            setTimeout(function() {
                $('.modal-content').html(response['html_from_view']);
            }, delay_by_in_ms);
		},
        error: function () {
            $this.html('Choose Panel');
		}
	}); 
})


$(document).on('click', '.step-btn', function(){
    var $this = $(this);
    var tab_id = $this.data('tab');
    $('.step-btn').removeClass('active');
    
    $this.addClass('active');
    $('.section-content').hide();
    $('#' + tab_id).css('visibility', 'visible').show();
})


$(document).on('click', '#loadpreviousProducts', function(){
    loadProducts();
})