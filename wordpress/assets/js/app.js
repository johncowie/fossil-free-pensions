/**
 * Fossil Fuel Divestment Map JS Plugin
 *
 * - Uses leaflet JS API to display a custom map http://leafletjs.com/
 * - Can support MapBox Layers https://www.mapbox.com/ if a MapBox ID and Token is supplied in the shortcode params
 * - Displayed data using geoJSON format http://geojson.org/
 * - Shows an AJAX spinner using http://fgnass.github.io/spin.js/
 * - Popup template uses http://handlebarsjs.com/
 * - Uses chroma-js for color scales of https://github.com/gka/chroma.js/blob/master/doc/api.md of choropleth https://en.wikipedia.org/wiki/Choropleth_map
 *
 */
(function($) {

    var fossil_fuel_map = function(settings) {

        var geojson, map;

        // register handlebars helper for incrementing table index col
        Handlebars.registerHelper("inc", function(value){ return parseInt(value) + 1;});

        // compile the handlebars template
        var template = Handlebars.compile($("#popup-template").html());

        // create the leafletjs map using shortcode atts
        map = L.map(settings.id, settings.leaflet);

        // add a mapbox tile layer if the access ID and Token is supplied in shortcode
        if (settings.mapBox.id && settings.mapBox.token) {
            L.tileLayer('https://{s}.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=' + settings.mapBox.token, {
                id: settings.mapBox.id
            }).addTo(map);
        }

        // get the inventory data for the map
        $.getJSON(settings.ajaxLander, function(data) {

            setColorScale(data.features);

            geojson = L.geoJson(data, {
                style: style,
                onEachFeature: fossil_fuel_map.onEachFeature
            }).addTo(map);

        }).done(function() {
            map.spin(false);
        });

        // start the spinner
        map.spin(true);

        /**
         * Set the basic color scale
         */
        var color = chroma(settings.style.fillColor);
        var colorScale = chroma.scale([color.brighten(2), color.darken()]);

        /**
         * setColorScale
         *
         * Chormajs color scale
         *
         */
        var setColorScale = function(features) {
            var min = 1;
            var max = 0;

            for(var i in features) {
                var percentage = features[i]['properties']['percentage'] / 100;
                min = percentage < min ? percentage : min;
                max = percentage > max ? percentage : max;
            }

            // set the scale domain
            colorScale.domain([min,max]);
        }

        /**
         * Get the feature style
         *
         * @private
         * @param feature
         * @returns {*}
         */
        var style = function(feature) {
            if (!feature.properties.fund_value) {
                settings.style.fillColor = 'transparent';
            } else {
                settings.style.fillColor = colorScale(feature.properties.percentage / 100).hex();
            }
            return settings.style;
        }

        /**
         * Decode entities
         *
         * see - http://stackoverflow.com/questions/1147359/how-to-decode-html-entities-using-jquery#answer-1395954
         *
         * @param encodedString
         * @returns {*}
         */
        var decodeEntities = function(encodedString) {
            var textArea = document.createElement('textarea');
            textArea.innerHTML = encodedString;
            return textArea.value;
        }

        return {

            /**
             * highlightFeature
             *
             * Use the settings.highlight shortcode params to style the feature
             *
             * @param e
             */
            highlightFeature: function(e) {
                var layer = e.target;

                layer.setStyle(settings.highlight);

                // handle IE and opera bugs
                if (!L.Browser.ie && !L.Browser.opera) {
                    layer.bringToFront();
                }
            },

            /**
             * resetHighlight
             *
             * Reset feature styles on mouseout
             *
             * @param e
             */
            resetHighlight: function(e) {
                geojson.resetStyle(e.target);
            },

            /**
             * zoomToFeature
             *
             * Zoom to the feature on click
             *
             * @param e
             */
            zoomToFeature: function(e) {
                var layer = e.target;

                var context = layer.feature.properties;
                var html = decodeEntities(template(context));

                var popup = L.popup()
                    .setLatLng(layer.getBounds().getCenter())
                    .setContent(html)
                    .openOn(map);

                // map.fitBounds(layer.getBounds());
            },

            /**
             * onEachFeature callback
             *
             * Set event handlers for each feature on map creation
             *
             * @param feature
             * @param layer
             */
            onEachFeature: function(feature, layer) {
                layer.on({
                    mouseover: fossil_fuel_map.highlightFeature,
                    mouseout: fossil_fuel_map.resetHighlight,
                    click: fossil_fuel_map.zoomToFeature
                });
            }
        }
    }(fossil_fuel_map_settings);

}(jQuery));