<?php

namespace FossilFuelDivestmentMap;

if (!defined('ABSPATH')) {
    exit; // exit if accessed directly
}

/**
 * Code for displaying the Fossil Fuel Divestment Map shortcode
 *
 */
if(!class_exists('FossilFuelDivestmentMap\MapShortcode')) :

    /**
     * FossilFuelDivestmentMap\MapShortcode
     *
     * @class FossilFuelDivestmentMap\MapShortcode
     *
     */
    class MapShortcode {

        // HTML ID for the map div
        const MAP_ID = 'fossil-fuel-divestment-map';

        // Wordpress action key for the ajax call
        const AJAX_ACTION = 'fossil_fuel_divestment_map_data';

        private $addScript = false;

        /**
         * constructor
         *
         */
        public function __construct() {
            // remove emojis which conflict with leaflet.js
            // see - https://wordpress.org/support/topic/version-422-wp-emoji-releaseminjs-error
            // TODO - better to disable only if shortcode displayed?
            remove_action('wp_head', 'print_emoji_detection_script', 7);
            remove_action('wp_print_styles', 'print_emoji_styles');

            // register shortcode
            add_shortcode(Plugin::PLUGIN_NAME, array($this, 'shortcode'));

            // register css
            add_action('wp_enqueue_scripts', array($this, 'register_css'));

            // register the javascripts
            add_action('wp_enqueue_scripts', array($this, 'register_scripts'));

            // display the handlebars template
            add_action('wp_footer', array($this, 'popup_template'));

            // register ajax handlers
            add_action('wp_ajax_' . self::AJAX_ACTION, array($this, 'inventory'));
            add_action('wp_ajax_nopriv_' . self::AJAX_ACTION, array($this, 'inventory'));
        }

        /**
         * register_css
         *
         * Loads the CSS file for the shortcode
         *
         * @return void
         */
        public function register_css () {
            wp_register_style('leaflet', 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/leaflet.css');
            wp_register_style(Plugin::PLUGIN_NAME, plugins_url('assets/css/styles.css', __FILE__), array('leaflet'), filemtime(Plugin::getPluginPath() . '/assets/css/styles.css'));
        }

        /**
         * register_scripts
         *
         * Load the required JavaScripts for the shortcode
         *
         * see default scripts included in wordpress
         * http://codex.wordpress.org/Function_Reference/wp_enqueue_script#Default_Scripts_Included_and_Registered_by_WordPress
         *
         * @return void
         */
        public function register_scripts() {
            wp_register_script('leaflet', plugins_url('assets/js/vendor/leaflet.js', __FILE__));
            wp_register_script('spinner', plugins_url('assets/js/vendor/spin.min.js', __FILE__));
            wp_register_script('leaflet-spin', plugins_url('assets/js/vendor/leaflet.spin.js', __FILE__));
            wp_register_script('handlebars', plugins_url('assets/js/vendor/handlebars-v3.0.3.js', __FILE__));
            wp_register_script('chroma', plugins_url('assets/js/vendor/chroma.min.js', __FILE__));
            wp_register_script(Plugin::PLUGIN_NAME, plugins_url('assets/js/app.js', __FILE__), array('jquery', 'leaflet', 'spinner', 'leaflet-spin', 'chroma', 'handlebars'), filemtime(Plugin::getpluginPath() . '/assets/js/app.js'), true);
        }

        /**
         * popup_template
         *
         * Add a handlebars template for the Map popup see http://handlebarsjs.com/
         *
         * @return void
         */
        public function popup_template() {
            if ($this->addScript) { ?>
                <!-- fossil fuel map template -->
                <script id="popup-template" type="text/x-handlebars-template">
                    <h2>{{name}}</h2>
                    {{#if fund_name}}
                    <h3>{{fund_name}}</h3>
                    {{/if}}
                    <dl>
                        {{#if fund_value}}
                        <dt class="fund-total"><?php echo ("Fund Total"); ?></dt>
                        <dd>&pound;{{fund_value}}</dd>
                        {{/if}}
                        {{#if investment_value}}
                        <dt class="investment-value"><?php echo ("Total Fossil Fuel Investments"); ?></dt>
                        <dd>&pound;{{investment_value}} {{#if percentage}}<span class="percentage">({{percentage}}&percnt;){{/if}}</span></dd>
                        {{/if}}
                        {{#if direct_investment}}
                        <dt class="direct-investment"><?php echo ("Direct Investments"); ?></dt>
                        <dd>&pound;{{direct_investment}} {{#if direct_percentage}}<span class="percentage">({{direct_percentage}}&percnt;){{/if}}</span></dd>
                        {{/if}}
                        {{#if projected_indirect_investment}}
                        <dt class="projected-indirect-investment"><?php echo ("Projected Indirect Investments"); ?></dt>
                        <dd>&pound;{{projected_indirect_investment}} {{#if indirect_percentage}}<span class="percentage">({{indirect_percentage}}&percnt;){{/if}}</span></dd>
                        {{/if}}
                    </dl>
                    {{#if companies}}
                    <h4><?php echo ("Top Fossil Fuel Investments"); ?></h4>
                    <table>
                        <tbody>
                        {{#each companies}}
                        {{#if name}}
                        <tr>
                            <td>{{inc @index}}</td>
                            <td>{{name}}</td>
                            <td>&pound;{{value}}</td>
                        </tr>
                        {{/if}}
                        {{/each}}
                        </tbody>
                    </table>
                    {{/if}}
                    {{#if google_doc_url}}
                    <a href="{{google_doc_url}}" target="_blank" rel="nofollow"><?php echo ("View Data in Google Doc Spreadsheet"); ?></a>
                    {{else if download}}
                    <a href="{{download}}" target="_blank" rel="nofollow"><?php echo ("Download"); ?></a>
                    {{/if}}
                    {{#if content}}
                    <div class="authority-content">
                        {{content}}
                    </div>
                    {{/if}}
                </script>
            <?php
            }
        }

        /**
         * shortcode
         *
         * Add a shortcode [fossil_fuel_divestment_map] to display the map
         *
         * @atts - shortcode attributes array
         * @return string
         */
        public function shortcode ($atts) {

            $this->addScript = true;

            // javascript params
            $defaults = array(
                'fund_value' => 0,
                'investment_value' => 0,
                'center' =>  '[55.0, -4.7]',
                'zoom' => 6,
                'max_zoom' => 12,
                'min_zoom' => 6,
                'max_bounds' => '[[70.0, 9.0], [48.0, -19.0]]', // NE x SW
                'mapbox_id' => '',
                'mapbox_token' => '',
                'attribution_control' => false,
                'fill_color' => '#ffa017',
                'color' => '#777',
                'weight' => 2,
                'opacity' => 0.8,
                'dash_array' => '',
                'fill_opacity' => 0.7,
                'highlight_weight' => 3,
                'highlight_dash_array' => '',
                'highlight_fill_opacity' => 1,
                'highlight_opacity' => 1,
            );

            $atts = shortcode_atts($defaults, $atts, Plugin::PLUGIN_NAME);

            // register the script params used in app.js
            wp_localize_script(Plugin::PLUGIN_NAME, 'fossil_fuel_map_settings', array(
                'id' => self::MAP_ID,
                'ajaxLander' =>  sprintf("%s?action=%s&_ajax_nonce=%s", admin_url( 'admin-ajax.php'), self::AJAX_ACTION, wp_create_nonce(self::AJAX_ACTION)),
                'leaflet' => array(
                    'center' => json_decode($atts['center'], true),
                    'zoom' =>  $atts['zoom'],
                    'maxZoom' => $atts['max_zoom'],
                    'minZoom' => $atts['min_zoom'],
                    'maxBounds' => json_decode($atts['max_bounds'], true),
                    'attributionControl' => false,
                ),
                'mapBox' => array(
                    'id' => $atts['mapbox_id'],
                    'token' => $atts['mapbox_token'],
                ),
                'style' => array(
                    'fillColor' => $atts['fill_color'],
                    'color' => $atts['color'],
                    'weight' => $atts['weight'],
                    'opacity' => $atts['opacity'],
                    'dashArray' => $atts['dash_array'],
                    'fillOpacity' => $atts['fill_opacity'],
                ),
                'highlight' => array(
                    'weight' => $atts['highlight_weight'],
                    'dashArray' => $atts['highlight_dash_array'],
                    'opacity' => $atts['highlight_opacity'],
                    'fillOpacity' => $atts['highlight_fill_opacity'],
                ),
            ));

            // enque scripts / styles
            wp_enqueue_style(Plugin::PLUGIN_NAME);
            wp_enqueue_script(Plugin::PLUGIN_NAME);

            ob_start();
            ?>
            <div id="<?php echo self::MAP_ID; ?>-wrapper">
                <?php if ($atts['fund_value'] && $atts['investment_value']) : ?>
                <table id="<?php echo self::MAP_ID; ?>-box">
                    <tbody>
                    <tr>
                        <td><strong><?php _e("Total Value of Pension Funds:", Plugin::PLUGIN_NAME); ?></strong></td>
                        <td><?php echo esc_html($atts['fund_value']); ?></td>
                    </tr>
                    <tr>
                        <td><strong><?php _e("Total Fossil Fuel Investments", Plugin::PLUGIN_NAME); ?></strong></td>
                        <td><?php echo esc_html($atts['investment_value']); ?></td>
                    </tr>
                    </tbody>
                </table>
                <?php endif ?>
                <div id="<?php echo esc_attr(self::MAP_ID); ?>"></div>
            </div>
            <?php

            $output = ob_get_contents();
            ob_end_clean();
            return $output;
        }

        /**
         * inventory
         *
         * AJAX Lander for the map data
         *
         * Query the DB for the information to display on the map.
         *
         * @return json
         */
        public function inventory() {

            header("content-type:application/x-javascript");

            check_ajax_referer(self::AJAX_ACTION);

            $map_authorities = get_posts(array(
                'numberposts' => -1,
                'post_type' => Plugin::POST_TYPE,
                'post_status' => 'publish',
            ));

            $geojson = array(
                'type' => 'FeatureCollection',
                'features' => array(),
            );

            foreach($map_authorities as &$map_authority) {

                $values = Plugin::get_custom_post_values($map_authority);

                foreach($values['companies'] as $key=> &$company) {
                    if(!$company['name']) {
                        unset($values['companies'][$key]);
                    } else {
                        $company['value'] = preg_replace('/\.\d{2}$/', '', $company['value']);
                    }
                }

                $geojson['features'][] = array(
                    'type' => 'Feature',
                    'properties'=> array (
                        'name' => esc_html($map_authority->post_title),
                        'content' => str_replace(']]>', ']]&gt;', apply_filters('the_content', $map_authority->post_content)),
                        'fund_name' => esc_html($values['fund_name']),
                        'fund_value' => esc_html(preg_replace('/\.\d{2}$/', '', $values['fund_value'])),
                        'investment_value'=> esc_html(preg_replace('/\.\d{2}$/', '', $values['investment_value'])),
                        'percentage'=> esc_html($values['fund_value'] ? bcmul(bcdiv(preg_replace('/,/', '', $values['investment_value']), preg_replace('/,/', '', $values['fund_value']), 4), 100, 2) : ''),
                        'direct_investment'=> esc_html(preg_replace('/\.\d{2}$/', '', $values['direct_investment'])),
                        'direct_percentage'=> esc_html($values['fund_value'] ? bcmul(bcdiv(preg_replace('/,/', '', $values['direct_investment']), preg_replace('/,/', '', $values['fund_value']), 4), 100, 2) : ''),
                        'projected_indirect_investment'=> esc_html($values['projected_indirect_investment']),
                        'indirect_percentage'=> esc_html($values['fund_value'] ? bcmul(bcdiv(preg_replace('/,/', '', $values['projected_indirect_investment']), preg_replace('/,/', '', $values['fund_value']), 4), 100, 2) : ''),
                        'currency' => esc_html($values['currency']),
                        'companies' => $values['companies'],
                        'download' => esc_html($values['file']),
                        'google_doc_url' => esc_html($values['google_doc_url']),
                    ),
                    'geometry' => json_decode($values['geojson_geometry']),
                );
            }

            echo json_encode($geojson);

            die();
        }
    }

endif;