$(document).on('submit', ".get_weather", function (e) {
    e.preventDefault();

    var city = $('#city-input').val();
    var country = $('#country-input').val();
    var baseUrl = $(this).attr('action');
    var url = baseUrl + city + '/' + country + '/';

    $.ajax({
        type: 'GET',
        url: url,
        dataType: 'json',
        success: function (data) {
            $('#city-name').text(data.city);
            $('#temperature').text(data.temperature);
            $('#description').text(data.description);
            $('#weather-icon').attr('src', `http://openweathermap.org/img/w/${data.icon}.png`);
            $('#weather-icon').attr('alt', data.description);
            $('#response').show();
        },
        error: function () {
            console.log('ERROR with ajax request');
        },
    });
});



