<?php

namespace FossilFuelDivestmentMap;

if (!defined('ABSPATH')) {
    exit; // exit if accessed directly
}

/**
 * Code for displaying the Fossil Fuel Divestment Table shortcode
 *
 */
if(!class_exists('FossilFuelDivestmentMap\TableShortcode')) :

    /**
     * FossilFuelDivestmentMap\TableShortcode
     *
     * @class FossilFuelDivestmentMap\TableShortcode
     *
     */
    class TableShortcode {

        // Wordpress action key for the ajax call
        const AJAX_ACTION = 'fossil_fuel_divestment_table_data';

        const TABLE_ID = 'fossil-fuel-divestment-table';

        private $addScript = false;

        /**
         * constructor
         *
         */
        public function __construct() {
            // register shortcode
            add_shortcode(Plugin::PLUGIN_NAME . '-table', array($this, 'shortcode'));

            // register css
            add_action('wp_enqueue_scripts', array($this, 'register_css'));

            // register the javascripts
            add_action('wp_enqueue_scripts', array($this, 'register_scripts'));

            // display the handlebars template
            add_action('wp_footer', array($this, 'table_template'));

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
            wp_register_style(Plugin::PLUGIN_NAME, plugins_url('assets/css/styles.css', __FILE__), array(), filemtime(Plugin::getPluginPath() . '/assets/css/styles.css'));
        }

        /**
         * register_scripts
         *
         * Load the required JavaScripts for the shortcode
         *
         * @return void
         */
        public function register_scripts() {
            wp_register_script('stream-table', plugins_url('assets/js/vendor/stream_table.min.js', __FILE__));
            wp_register_script('handlebars', plugins_url('assets/js/vendor/handlebars-v3.0.3.js', __FILE__));
            wp_register_script(Plugin::PLUGIN_NAME . '-table', plugins_url('assets/js/table.js', __FILE__), array('jquery','handlebars', 'stream-table'), filemtime(Plugin::getpluginPath() . '/assets/js/app.js'), true);
        }

        /**
         * table_template
         *
         * Add a handlebars template for the Map popup see http://handlebarsjs.com/
         *
         * @return void
         */
        public function table_template() {
            if ($this->addScript) { ?>
                <!-- fossil fuel row template -->
                <script id="row-template" type="text/x-handlebars-template">
                    <tr>
                        <td>{{{name}}}</td>
                        <td>{{{fund_name}}}</td>
                        <td>{{formatNumber fund_value}}</td>
                        <td>{{formatNumber investment_value}}</td>
                        <td>{{percentage}}</td>
                        <td>{{formatNumber direct_investment}}</td>
                        <td>{{direct_percentage}}</td>
                        <td>{{formatNumber projected_indirect_investment}}</td>
                        <td>{{indirect_percentage}}</td>
                    </tr>
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

            // params
            $defaults = array(

            );

            $atts = shortcode_atts($defaults, $atts, Plugin::PLUGIN_NAME);

            // register the script params used in app.js
            wp_localize_script(Plugin::PLUGIN_NAME . '-table', 'fossil_fuel_table_settings', array(
                'id' => '#' . self::TABLE_ID,
                'ajaxLander' =>  sprintf("%s?action=%s&_ajax_nonce=%s", admin_url('admin-ajax.php'), self::AJAX_ACTION, wp_create_nonce(self::AJAX_ACTION)),
            ));

            // enque scripts / styles
            wp_enqueue_style(Plugin::PLUGIN_NAME);
            wp_enqueue_script(Plugin::PLUGIN_NAME . '-table');

            ob_start();

            ?>
            <div id="<?php echo self::TABLE_ID; ?>-wrapper">
                <input name="search" type="text" id="st_search" class="st_search placeholder" placeholder="<?php _e("Search for Local Authorities"); ?>">
                <table id="<?php echo self::TABLE_ID; ?>">
                    <thead>
                        <tr>
                            <th data-sort="name:asc"><?php _e("Local Authority", Plugin::PLUGIN_NAME); ?></th>
                            <th data-sort="fund_name:asc"><?php _e("Fund Name", Plugin::PLUGIN_NAME); ?></th>
                            <th data-sort="fund_value:desc:number"><?php _e("Total Fund Value", Plugin::PLUGIN_NAME); ?></th>
                            <th data-sort="investment_value:desc:number"><?php _e("Total Fossil Fuel Investments", Plugin::PLUGIN_NAME); ?></th>
                            <th data-sort="percentage:desc:number"><?php _e("Total", Plugin::PLUGIN_NAME); ?><br>&percnt;</th>
                            <th data-sort="direct_investment:desc:number"><?php _e("Direct Investments", Plugin::PLUGIN_NAME); ?></th>
                            <th data-sort="direct_percentage:desc:number"><?php _e("Direct", Plugin::PLUGIN_NAME); ?><br>&percnt;</th>
                            <th data-sort="projected_indirect_investment:desc:number"><?php _e("Projected Indirect Investments", Plugin::PLUGIN_NAME); ?><br>&pound; <?php _e("Millions", Plugin::PLUGIN_NAME); ?></th>
                            <th data-sort="indirect_percentage:desc:number"><?php _e("Indirect", Plugin::PLUGIN_NAME); ?><br>&percnt;</th>
                        </tr>
                    </thead>
                    <!-- stream-table renders rows here -->
                    <tbody>
                    </tbody>
                </table>
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
                'post_type' => Plugin::POST_TYPE,
                'post_status' => 'publish',
                'posts_per_page' => filter_input(INPUT_GET, 'limit', FILTER_SANITIZE_NUMBER_INT),
                'offset' => filter_input(INPUT_GET, 'offset', FILTER_SANITIZE_NUMBER_INT),
                's' => filter_input(INPUT_GET, 'q', FILTER_SANITIZE_NUMBER_INT),
            ));

            $data = array();

            foreach($map_authorities as &$map_authority) {

                $values = Plugin::get_custom_post_values($map_authority);

                foreach($values['companies'] as $key=> &$company) {
                    if(!$company['name']) {
                        unset($values['companies'][$key]);
                    }
                }

                $data[] = array(
                    'name' => esc_html($map_authority->post_title),
                    // 'content' => $map_authority->post_content,
                    'fund_name' => esc_html($values['fund_name']),
                    'fund_value' => preg_replace(array('/\.\d{2}$/', '/,/'), '', $values['fund_value']),
                    'investment_value' => preg_replace(array('/\.\d{2}$/', '/,/'), '', $values['investment_value']),
                    'percentage' => $values['fund_value'] ? bcmul(bcdiv(preg_replace('/,/', '', $values['investment_value']), preg_replace('/,/', '', $values['fund_value']), 4), 100, 2) : '0.00',
                    'direct_investment' => preg_replace(array('/\.\d{2}$/', '/,/'), '', $values['direct_investment']),
                    'direct_percentage' => $values['fund_value'] ? bcmul(bcdiv(preg_replace('/,/', '', $values['direct_investment']), preg_replace('/,/', '', $values['fund_value']), 4), 100, 2) : '0.00',
                    'projected_indirect_investment' => preg_replace(array('/\.\d{2}$/', '/,/'), '', $values['projected_indirect_investment']),
                    'indirect_percentage' => $values['fund_value'] ? bcmul(bcdiv(preg_replace('/,/', '', $values['projected_indirect_investment']), preg_replace('/,/', '', $values['fund_value']), 4), 100, 2) : '0.00',
                    // 'currency' => esc_attr($values['currency']),
                    // 'companies' => $values['companies'],
                );
            }

            echo json_encode($data);

            die();
        }
    }

endif;