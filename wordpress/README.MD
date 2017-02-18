# Fossil Fuel Map Wordpress Plugin #

A Wordpress plugin for displaying Fossil Fuel Investments for UK Pension Authorities for http://gofossilfree.org/

###BEFORE ACTIVATING THE PLUGIN IN WORDPRESS BACKUP THE DATABASE!###

On first activation the plugin attempts to import new Custom Posts of type "map_authority" into Wordpress. By default from the docs/GBR_adm2/GBR_adm2.min.json file, created from data at http://www.gadm.org/, this inserts a new post for each local authority, which the geometry data as a post_meta field and the post_title from the feature name property.

See here for info on creating geoJSON files from shape files  
http://stackoverflow.com/questions/13455842/where-to-find-the-uks-regions-map-on-geojson-format

GeoJSON (http://geojson.org/) can be minimized using http://mapshaper.org/

See also http://leafletjs.com/examples/geojson.html

###Map Authorities###
The plugin adds a "map_authority" Custom Post Type with custom fields for the data displayed on the map front end when a shape is clicked.

NB. Only published posts will be displayed as shapes on the map. 

###Shortcode###
The [fossil-fuel-divestment-map] short code renders the map on a Wordpress page.

Additional attributes for the shortcode control map behaviour displayed below with defaults:
```php
'center' => [55.0, -4.7], // map center lon-lat  
'zoom' => 6, // map zoom
'max_zoom' => 8, //map max zoom
'min_zoom' => 6, // map min zoom
'max_bounds' => [[70.0, 9.0], [48.0, -19.0]], // map boundary co-ordinates [NE x SW]
'mapbox_id' => '', // https://www.mapbox.com/help/define-map-id/
'mapbox_token' => '', // https://www.mapbox.com/help/create-api-access-token/
'fill_color' => '#7d959b', // map shape fill colour
'color' => '#777', // map shape outline colour 
'weight' => 2, // map shape line weight
'dash_array' => '', // map shape line dashes
'opacity' => 0.8, // map shape line opacity
'fill_opacity' => 0.7, // map shape fill opactity
'highlight_weight' => 3, // highlight shape line weight
'highlight_dash_array' => '', // highlight shape dashes
'highlight_opacity' => 1, // map shape line opacity
'highlight_fill_opacity' => 1, // map shape fill opactity
```

###Uploads###
To allow a file to be uploaded for the spreadsheet download on Multi Site networks the file extension should be added to the allowed list under Network Settings

###Emojis###
The plugin disables Wordpress emojiis which cause conflicts with leaflet.js

##Importer##
The plugin makes a custom Map Authorities importer available from the Wordpress admin screen.
This allows a csv file to be imported with the following headers to match the post_meta:

```
post_title
fund_name
fund_value
investment_value
companies[0]['name']
companies[0]['value']
companies[1]['name']
companies[1]['value']
companies[2]['name']
companies[2]['value']
companies[3]['name']
companies[3]['value']
companies[4]['name']
companies[4]['value']
pool_funds[0]['name']
pool_funds[0]['value']
pool_funds[1]['name']
pool_funds[1]['value']
pool_funds[2]['name']
pool_funds[2]['value']
pool_funds[3]['name']
pool_funds[3]['value']
pool_funds[4]['name']
pool_funds[4]['value']
```
Note the `post_title` field must match an existing post_title for the data to be imported

##Table##
A table displaying all the data can be added using the shortcode [fossil-fuel-divestment-map-table] 

