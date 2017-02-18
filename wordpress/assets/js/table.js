/**
 * Fossil Fuel Divestment Table Shorcode
 *
 * See:
 *  - http://handlebarsjs.com/
 *  - https://github.com/jiren/StreamTable.js
 *
 */
(function($) {

    Handlebars.registerHelper('formatNumber', function(value) {
        return $.isNumeric(value) ? parseInt(value).toLocaleString() : '-';
    });

    var fossil_fuel_table = function(settings) {

        // compile the handlebars template
        var template = Handlebars.compile($("#row-template").html());

        // render each row
        var row = function(data) {
            return template(data);
        }
        // set up stream-table
        $(settings.id).stream_table({
            view: row,
            data_url: settings.ajaxLander,
            stream_after: 1,
            auto_sorting: true,
            fetch_data_limit: 200,
            search_box: '#st_search',
            pagination: {
                next_text: '&rarr;',
                prev_text: '&larr;'
            }
        }, []);

        // remove the other th sort classes
        $(settings.id)
            .on('click th', function(e) {
                $(e.target).siblings().removeClass('asc desc')
            });


    }(fossil_fuel_table_settings);

}(jQuery));