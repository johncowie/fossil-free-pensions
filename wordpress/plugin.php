<?php
/**
 * Plugin Name: Fossil Fuel Divestment Map
 * Description: A plugin for displaying Fossil Fuel Investments for UK Pension Authorities
 * Version: 1.01
 * Author: Ben Wallis
 * Author URI: http://www.benedict-wallis.com
 */

namespace FossilFuelDivestmentMap;

if (!defined('ABSPATH')) {
    exit; // exit if accessed directly
}

require_once('importer.php');
require_once('shortcode.map.php');
require_once('shortcode.table.php');
require_once('shortcode.box.php');

if(!class_exists('FossilFuelDivestmentMap\Plugin')) :

    /**
     * FossilFuelDivestmentMap\Plugin
     *
     * @class FossilFuelDivestmentMap\Plugin
     *
     */
    class Plugin {

        // paths
        public static $pluginPath;

        // custom post type
        const POST_TYPE = 'map_authority';

        // plugin name
        const PLUGIN_NAME = "fossil-fuel-divestment-map";

        protected $currencies = array(
            'gbp' => "GBP",
        );

        // set the file to import the geo json data from when the plugin is activated
        // nb - relative to plugin path
        const IMPORT_GEOJSON = '/docs/GBR_adm/GBR_adm2.min.json';


        /**
         * getPluginPath
         *
         * @return mixed
         */
        public static function getPluginPath() {
            if (!static::$pluginPath) {
                static::$pluginPath = dirname(__FILE__);
            }
            return static::$pluginPath;
        }

        /**
         * __constructor
         *
         */
        public function __construct() {

            // add custom post type
            add_action('init', array($this, 'add_custom_post_type'));

            // save post meta
            add_action('save_post', array($this, 'save_post_meta'), 10, 2);

            // output errors on activation to a log file
            add_action('activated_plugin', array($this, 'activation_error'));

            // overwrite existing posts on activation - use with care!
            /* register_activation_hook(__FILE__, array($this, 'delete_existing_posts')); */

            // we may need to insert data when the plugin is first activated
            register_activation_hook(__FILE__, array($this, 'activate'));

            // add admin styles
            add_action('admin_print_styles-post-new.php', array($this, 'enqueue_admin_styles'));
            add_action('admin_print_styles-post.php', array($this, 'enqueue_admin_styles'));

            // enable file uploads in the post edit form
            add_action('post_edit_form_tag', array($this, 'post_edit_form_tag'));

            // check for post form errors
            add_action('admin_notices', array($this, 'get_post_errors'));

            // register the custom csv importer
            add_action('plugins_loaded', array($this, 'register_importer'));
        }

        /**
         * enqueue_admin_styles
         *
         * @return void
         */
        function enqueue_admin_styles() {
            global $post_type;
            if ($post_type === self::POST_TYPE){
                wp_enqueue_style(self::PLUGIN_NAME . '-admin-style', plugins_url('assets/css/admin.css', __FILE__));
            }
        }

        /**
         * post_edit_form_tag
         *
         * enable file uploads in the post edit form
         */
        function post_edit_form_tag() {
            echo ' enctype="multipart/form-data"';
        }

        /**
         * add_custom_post_type
         *
         * Register a custom post type for the map data
         *
         */
        public function add_custom_post_type() {
            register_post_type(self::POST_TYPE,
                array(
                    'labels' => array(
                        'name' => __( "Map Authorities", self::PLUGIN_NAME ),
                        'singular_name' => __( "Map Authority", self::PLUGIN_NAME )
                    ),
                    'supports' => array('title', 'editor'),
                    'public' => false,
                    'show_ui' => true,
                    'has_archive' => false,
                    'exclude_from_search' => true,
                    'publicly_queryable' => false,
                    'show_in_nav_menus' => false,
                    'rewrite' => false,
                    'register_meta_box_cb' => array($this, 'add_meta_boxes'),
                )
            );
        }

        /**
         * render_meta_box_content
         *
         * @param $post
         */
        public function render_meta_box_content($post) {

            // add a nonce
            wp_nonce_field(self::PLUGIN_NAME, self::PLUGIN_NAME . '_nonce');

            // get existing values
            $values = self::get_custom_post_values($post);

            $values['companies'] = $values['companies'] + array_fill(0, 5, array('name' => '', 'value' => ''));

            ?>
            <!-- fund name-->
            <div>
                <label for="fund-name">
                    <?php _e("Pension Fund Name", self::PLUGIN_NAME); ?>
                </label>
                <input id="fund-name" name="_fund_name" type="text" value="<?php echo esc_attr($values['fund_name']); ?>" placeholder="<?php _e("Pension Fund Name", self::PLUGIN_NAME); ?>" />
                <p>
                    <?php _e("Name of Local Authority Pension Fund", self::PLUGIN_NAME); ?>
                </p>
            </div>
            <!-- fund value -->
            <div>
                <label for="fund-value">
                    <?php _e("Pension Fund Value", self::PLUGIN_NAME); ?>
                </label>
                <input id="fund-value" name="_fund_value" type="text" value="<?php echo esc_attr($values['fund_value']); ?>" placeholder="0.00" />
                <p>
                    <?php _e("Value of Local Authority Pension Fund total investment", self::PLUGIN_NAME) ?>
                </p>
            </div>
            <!-- investment value -->
            <div>
                <label for="investment-value">
                    <?php _e("Fossil Fuel Investment", self::PLUGIN_NAME); ?>
                </label>
                <input id="investment-value" name="_investment_value" type="text" value="<?php echo esc_attr($values['investment_value']); ?>" placeholder="0.00" />
                <p>
                    <?php _e("Value of Fossil Fuel Investment", self::PLUGIN_NAME) ?>
                </p>
            </div>
            <!-- direct investments -->
            <div>
                <label for="direct-investments">
                    <?php _e("Direct Investments", self::PLUGIN_NAME); ?>
                </label>
                <input id="direct-investments" name="_direct_investment" type="text" value="<?php echo esc_attr($values['direct_investment']); ?>" placeholder="0.00" />
                <p>
                    <?php _e("Value of Direct Fossil Fuel Investment", self::PLUGIN_NAME) ?>
                </p>
            </div>
            <!-- projected indirect investments -->
            <div>
                <label for="projected-indirect-investments">
                    <?php _e("Projected Indirect Investments", self::PLUGIN_NAME); ?>
                </label>
                <input id="projected-indirect-investments" name="_projected_indirect_investment" type="text" value="<?php echo esc_attr($values['projected_indirect_investment']); ?>" placeholder="0.00" />
                <p>
                    <?php _e("Value of Projected Indirect Fossil Fuel Investment", self::PLUGIN_NAME) ?>
                </p>
            </div>
            <!-- currency -->
            <div>
                <label for="currency">
                    <?php _e("Currency", self::PLUGIN_NAME); ?>
                </label>
                <select id="currency" name="_currency">
                    <?php foreach($this->currencies as $key=>$value) : ?>
                        <option value="<?php echo esc_attr($key); ?>"<?php if($values['currency'] == $key) : ?> selected<?php endif?>><?php echo esc_html($value); ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <!-- google url download -->
            <div>
                <label for="file">
                    <?php _e("Google Doc URL", self::PLUGIN_NAME); ?>
                </label>
                <input id="text" name="_googl_doc_url" type="text" />
                <p>
                    <?php _e("Google Doc URL", self::PLUGIN_NAME) ?>
                </p>
            </div>
            <!-- file download -->
            <div>
                <label for="file">
                    <?php _e("Spreadsheet File", self::PLUGIN_NAME); ?>
                </label>
                <?php if(isset($values['file']) && $values['file']) : ?>
                <a href="<?php esc_url($values['file']) ?>" class="investment-attachment"><?php echo esc_url($values['file']) ?></a>
                <?php endif; ?>
                <input id="file" name="_file" type="file" />
                <p>
                    <?php _e("Attach spreadsheet file for download, used only if no Google Doc URL", self::PLUGIN_NAME) ?>
                </p>
            </div>
            <!-- top 5 companies -->
            <h4><?php _e("Top 5 Companies", self::PLUGIN_NAME); ?></h4>
            <table class="form-table">
                <thead>
                <tr>
                    <th>#</th>
                    <th><?php _e("Company Name", self::PLUGIN_NAME); ?></th>
                    <th><?php _e("Investment Value", self::PLUGIN_NAME); ?></th>
                </tr>
                </thead>
                <tbody>
                <?php foreach($values['companies'] as $i=>$company) : ?>
                    <tr>
                        <td><?php echo $i + 1?>.</td>
                        <td><input type="text" name="_companies[<?php echo $i; ?>][name]" value="<?php echo esc_attr($company['name']); ?>" placeholder="<?php _e("Company Name", self::PLUGIN_NAME); ?>" /></td>
                        <td><input type="text" name="_companies[<?php echo $i; ?>][value]" value="<?php echo esc_attr($company['value']); ?>" placeholder="0.00" /></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
            <!-- geojson geometry -->
            <div>
                <label for="geojson_geometry">
                    <?php _e("GeoJSON Geometry", self::PLUGIN_NAME); ?>
                </label>
                <textarea id="geojson_geometry" name="_geojson_geometry" cols="40" rows="10"><?php echo esc_html($values['geojson_geometry']); ?></textarea>
                <p>
                    <?php _e("Only change this if you know what you are doing!", self::PLUGIN_NAME) ?>
                </p>
            </div>
        <?php
        }

        /**
         * Adds the meta box container.
         *
         * @string $post_type
         */
        public function add_meta_boxes($post_type) {
            add_meta_box(sprintf("metabox_%s", self::POST_TYPE), __("Investments Data", self::PLUGIN_NAME), array($this, 'render_meta_box_content'), self::POST_TYPE, 'normal');
        }

        /**
         * save_meta
         *
         * Save the meta box's post metadata.
         *
         * @param $post_id
         * @param $post
         */
        public function save_post_meta( $post_id, $post ) {
            // check post type
            if (get_post_type_object($post->post_type) !== self::POST_TYPE) {
                // verify nonce
                if (isset($_POST[self::PLUGIN_NAME . '_nonce']) && wp_verify_nonce( $_POST[self::PLUGIN_NAME . '_nonce'], self::PLUGIN_NAME)) {
                    // check user can edit
                    if (current_user_can('edit_posts', $post_id)) {

                        // get the existing data
                        $old = self::get_custom_post_values($post);

                        // get the new data
                        $new = $this->sanitize_custom_input();

                        // add new values that did not previously exist
                        foreach($new as $key=>$new_value) {
                            if($new_value && (!isset($old[$key]) || !$old[$key])) {
                                add_post_meta($post_id, "_{$key}", $new_value);
                            }
                        }

                        foreach($old as $key=>$old_value) {
                            // update existing value where the data has changed
                            if(isset($new[$key])) {
                                if($new[$key] && $new[$key] != $old_value) {
                                    update_post_meta($post_id, "_{$key}", $new[$key]);
                                }
                            }
                            // delete existing value where it is no longer present
                            else {
                                // delete_post_meta($post_id,  "_{$key}", $old_value);
                            }
                        }

                        // save the spreadsheet file
                        $this->save_attachment($post_id);
                    }
                }
            }

            return $post_id;
        }

        /**
         * save_attachment
         *
         * saves the spreadsheet file '_download'
         *
         * @param $post_id
         * @return int|bool false on failure
         */
        private function save_attachment($post_id) {
            $message = '';

            if(isset($_FILES['_file'])) {
                if ($uploaded_file = wp_handle_upload($_FILES['_file'], array('test_form' => false))) {
                    if (!isset($uploaded_file['error']) && isset($uploaded_file['file'])) {
                        $attachment = array(
                            'post_title' => $_FILES['_file']['name'],
                            'post_content' => '',
                            'post_type' => 'attachment',
                            'post_parent' => $post_id,
                            'post_mime_type' => $_FILES['_file']['type'],
                            'guid' => $uploaded_file['url'],
                        );
                        // save the data
                        $id = wp_insert_attachment($attachment, $uploaded_file['file'], $post_id);
                        wp_update_attachment_metadata($id, wp_generate_attachment_metadata($id, $uploaded_file['file']));
                        update_post_meta($post_id, "_file", $uploaded_file['url']);
                        return $id;
                    } else {
                        $message = $uploaded_file['error'];
                    }
                }
            }

            if ($message) {
                set_transient(sprintf("_%s_file_upload_error", strtolower(self::PLUGIN_NAME)), $message, 60);
            }

            return false;
        }

        /**
         * get_post_errors
         *
         * checks for any transients stored on saving the post and displays them as admin error notices.
         *
         */
        public function get_post_errors() {
            global $post;
            if ($post && $post->post_type === self::POST_TYPE) {
                if($transient = get_transient(sprintf("_%s_file_upload_error", strtolower(self::PLUGIN_NAME)))) {
                    delete_transient(sprintf("_%s_file_upload_error", strtolower(self::PLUGIN_NAME))); ?>
                    <div class="error">
                        <p><?php echo esc_html($transient); ?></p>
                    </div>
                <?php
                }
            }
        }

        /**
         * get_custom_post_values
         *
         * Retrieve the custom field meta for the post
         *
         * @param $post
         * @return array
         */
        public static function get_custom_post_values($post) {

            $values = array(
                'fund_name' => get_post_meta($post->ID, '_fund_name', true ),
                'fund_value' => get_post_meta($post->ID, '_fund_value', true ),
                'investment_value' => get_post_meta($post->ID, '_investment_value', true),
                'direct_investment' => get_post_meta($post->ID, '_direct_investment', true),
                'projected_indirect_investment' => get_post_meta($post->ID, '_projected_indirect_investment', true),
                'currency' => get_post_meta($post->ID, '_currency', true),
                'companies' => get_post_meta($post->ID, '_companies', false),
                'file' => get_post_meta($post->ID, '_file', true),
                'google_doc_url' => get_post_meta($post->ID, '_google_doc_url', true),
                'geojson_geometry' => json_encode(get_post_meta($post->ID, '_geojson_geometry', true)),
            );

            $values['fund_value'] = $values['fund_value'] ? number_format((float)$values['fund_value'], 2) : '';
            $values['investment_value'] = $values['investment_value'] ? number_format((float)$values['investment_value'], 2) : '';
            $values['direct_investment'] = $values['direct_investment'] ? number_format((float)$values['direct_investment'], 2) : '';
            $values['projected_indirect_investment'] = $values['projected_indirect_investment'] ? number_format((float)$values['projected_indirect_investment'], 2) : '';

            $values['companies'] = $values['companies'] ? $values['companies'][0] : array();

            foreach($values['companies'] as &$company) {
                if(isset($company['value'])) {
                    $company['name'] = strip_tags($company['name']);
                    $company['value'] = number_format((float)$company['value'], 2);
                }
            }

            return $values;
        }

        /**
         * sanitize_custom_input
         *
         * @return array
         */
        private function sanitize_custom_input() {
            $values = array(
                'geojson_geometry' => json_decode(stripslashes($_POST['_geojson_geometry']), true),
                'fund_name' => filter_input(INPUT_POST, '_fund_name', FILTER_SANITIZE_STRING),
                'fund_value' => filter_input(INPUT_POST, '_fund_value', FILTER_SANITIZE_NUMBER_FLOAT, FILTER_FLAG_ALLOW_FRACTION),
                'investment_value' => filter_input(INPUT_POST, '_investment_value', FILTER_SANITIZE_NUMBER_FLOAT, FILTER_FLAG_ALLOW_FRACTION),
                'direct_investment' => filter_input(INPUT_POST, '_direct_investment', FILTER_SANITIZE_NUMBER_FLOAT, FILTER_FLAG_ALLOW_FRACTION),
                'projected_indirect_investment' => filter_input(INPUT_POST, '_projected_indirect_investment', FILTER_SANITIZE_NUMBER_FLOAT, FILTER_FLAG_ALLOW_FRACTION),
                'currency' => filter_input(INPUT_POST, '_currency', FILTER_SANITIZE_STRING),
                'google_doc_url' => filter_input(INPUT_POST, '_google_doc_url', FILTER_SANITIZE_URL),
                'companies' => array_fill(0, 5, array('name'=>'', 'value'=>0)),
            );

            if (isset($_POST['_companies'])) {
                foreach ($_POST['_companies'] as $key => $company) {
                    $values['companies'][$key]['name'] = filter_var($company['name'], FILTER_SANITIZE_STRING);
                    $values['companies'][$key]['value'] = filter_var($company['value'], FILTER_SANITIZE_NUMBER_FLOAT, FILTER_FLAG_ALLOW_FRACTION);
                }
            }

            return $values;
        }

        /**
         * activate
         *
         * On activation import geojson data from specified file if it exists.
         *
         * Imports posts only if no previously published posts exist
         *
         * @return bool
         */
        public function activate() {
            global $wpdb;
            if(self::IMPORT_GEOJSON && file_exists(self::getPluginPath() . self::IMPORT_GEOJSON)) {
                $count = (int)$wpdb->get_var("
                    SELECT COUNT(*)
                    FROM {$wpdb->prefix}postmeta AS m
                    INNER JOIN {$wpdb->prefix}posts AS p ON p.ID = m.post_id
                    WHERE p.post_type = '" . SELF::POST_TYPE ."';"
                );
                // import posts if no previous posts exist (i.e. first activation)
                if (!$count) {
                    $this->parse_json_file(self::getPluginPath() . self::IMPORT_GEOJSON);
                }
            }
        }

        /**
         * parse_json_file
         *
         * Need to sequentially parse large JSON files in case of memory limitations
         *
         * see - https://github.com/salsify/jsonstreamingparser
         *
         * @param $file
         * @return mixed
         * @throws Exception
         */
        public function parse_json_file($file) {
            require_once 'inc/geojson_parser.php';

            $listener = new \GeoJsonParser();
            $listener->callback = array($this, 'import_geojson_feature');
            $stream = fopen($file, 'r');
            try {
                $parser = new \JsonStreamingParser_Parser($stream, $listener);
                $parser->parse();
            } catch (\Exception $e) {
                fclose($stream);
                throw $e;
            }
        }

        /**
         * import_geojson_feature
         *
         * callback for GeoJsonParser listener
         *
         * @param $geojson - geo json fomratted string
         * @param $title_key - key in json to use for post_title
         * @param $delete_existing - remove existing posts
         * @return int - no. posts inserted
         */
        public static function import_geojson_feature($feature, $title_key = 'name') {
            if ($feature) {
                if (isset($feature['properties'][$title_key]) && $feature['geometry']) {
                    $post_id = wp_insert_post(array(
                        'post_title' => $feature['properties'][$title_key],
                        'post_name' => sanitize_title($feature['properties'][$title_key]),
                        'post_type' => self::POST_TYPE,
                    ));

                    if ($post_id) {
                        add_post_meta($post_id, '_geojson_geometry', $feature['geometry'], true);
                    }

                    return $post_id;
                }
            }
            return 0;
        }

        /**
         * delete_existing_posts
         *
         * Move posts to trash
         *
         */
        public function delete_existing_posts() {
            $posts = get_posts(array(
                'numberposts' => -1,
                'post_type' => self::POST_TYPE,
                'post_status' => 'any',
            ));
            foreach($posts as $post) {
                wp_delete_post($post->ID, false);
            }
        }

        /**
         * activation_error
         *
         * Log errors on activation
         */
        public function activation_error() {
            if ($ob = ob_get_contents()) {
                file_put_contents(dirname(__file__) . '/error_activation.txt', $ob);
            }
        }

        /**
         * Init the importer
         *
         */
        public function register_importer() {
            if(class_exists('FossilFuelDivestmentMap\Importer')) {
                // init the importer
                $custom_import = new Importer();
                register_importer('map_authority_importer', __("Map Authority Importer", self::PLUGIN_NAME), __("Import data for the Fossil Fuel Divestment Map.", self::PLUGIN_NAME), array($custom_import, 'dispatch'));
            }
        }

    }

endif;

new Plugin();
new MapShortcode();
new TableShortcode();