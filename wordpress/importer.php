<?php
/**
 * Map Authority Importer
 *
 * @package WordPress
 * @subpackage Importer
 */

namespace FossilFuelDivestmentMap;

if ( !defined('WP_LOAD_IMPORTERS') ) {
    return;
}

/** Display verbose errors */
define( 'IMPORT_DEBUG', true );

// Load Importer API
require_once ABSPATH . 'wp-admin/includes/import.php';

if (!class_exists('WP_Importer')) {
    $class_wp_importer = ABSPATH . 'wp-admin/includes/class-wp-importer.php';
    if ( file_exists( $class_wp_importer ) ) {
        require $class_wp_importer;
    }
}

if ( class_exists( 'WP_Importer' ) ) {

    /**
     * Class MapAuthorityImporter
     */
    class Importer extends \WP_Importer {

        private $id;
        private $file;

        const DELIMITER = ',';

        /**
         * MapAuthorityImporter_Import
         */
        public function MapAuthorityImporter_Import() { }

        /**
         * header
         *
         */
        function header() { ?>
            <div class="wrap">
                <h2><?php _e("Import CSV", Plugin::PLUGIN_NAME); ?></h2>
        <?php
        }

        /**
         * footer
         */
        function footer() { ?>
            </div>
        <?php
        }

        /**
         * greet
         *
         */
        function greet() { ?>
            <p><?php _e("Choose a CSV (.csv) file to upload, then click Upload file and import.", Plugin::PLUGIN_NAME); ?></p>
            <strong><?php _e("Requirements:", Plugin::PLUGIN_NAME); ?></strong>
            <ol>
                <li><?php _e("The `post_title` column must match exactly the existing Map Authority post titles to import data for, otherwise a new post will be created.", Plugin::PLUGIN_NAME); ?></li>
                <li><?php _e("Use UTF-8 as charset.", Plugin::PLUGIN_NAME); ?></li>
                <li><?php echo sprintf(__("Use field delimiter: '%s'", Plugin::PLUGIN_NAME), self::DELIMITER ); ?></li>
                <li><?php _e("Quote all text cells.", Plugin::PLUGIN_NAME); ?></li>
                <li><?php _e("Accepted columns headers are:", Plugin::PLUGIN_NAME); ?>
                    <ul>
                        <li>post_title</li>
                        <li>post_content</li>
                        <li>fund_name</li>
                        <li>fund_value</li>
                        <li>investment_value</li>
                        <li>direct_investment</li>
                        <li>projected_indirect_investment</li>
                        <li>google_doc_url</li>
                        <li>companies[0-4]['name']</li>
                        <li>companies[0-4]['value']</li>
                    </ul>
                </li>
            </ol>
            <p><?php _e("From Open Office please export as csv before import", Plugin::PLUGIN_NAME); ?></p>
            <?php wp_import_upload_form(add_query_arg('step', 1));
        }

        /**
         * dispatch
         *
         * Registered callback function for the Custom Importer
         *
         * Manages the separate stages of the import process
         *
         */
        function dispatch() {
            $this->header();

            if (empty ($_GET['step'])) {
                $step = 0;
            }
            else {
                $step = (int)$_GET['step'];
            }

            switch ($step) {
                case 0 :
                    $this->greet();
                    break;
                case 1 :
                    check_admin_referer('import-upload');
                    set_time_limit(0);
                    $result = $this->import();
                    if ( is_wp_error( $result ) ) {
                        echo $result->get_error_message();
                    }
                    break;
            }

            $this->footer();
        }

        /**
         * import
         *
         * The main controller for the actual import stage. Contains all the import steps.
         *
         * @param none
         * @return none
         */
        function import() {
            $file = wp_import_handle_upload();

            if ( isset( $file['error'] ) ) { ?>
                <p>
                    <strong><?php __("Sorry, there was an error with the import.", Plugin::PLUGIN_NAME); ?></strong><br>
                    <?php echo esc_html($file['error']); ?>
                </p><?php
                return false;
            } else if (!file_exists($file['file'])) { ?>
                <p>
                    <strong><?php _e("Sorry, there was an error with the import.",  Plugin::PLUGIN_NAME); ?></strong><br>
                    <?php echo sprintf(__("The export file could not be found at <code>%s</code>. It is likely that this was caused by a permissions problem.", Plugin::PLUGIN_NAME), esc_html($file['file'])); ?>
                </p>
                <?php
                return false;
            }

            $this->id = (int)$file['id'];
            $this->file = get_attached_file($this->id);
            $result = $this->process_posts();
            if (is_wp_error($result)) {
                return $result;
            }
        }

        /**
         * process_posts
         *
         * Imports posts and loads $this->posts
         *
         * @uses $wpdb
         *
         * @param none
         * @return none
         */
        function process_posts() {

            $headers = array();
            $content = array();

            // read file contents first
            if (($handle = fopen($this->file, 'r')) !== false) {
                $row = 0;
                while (($data = fgetcsv($handle, 1000, self::DELIMITER)) !== false) {
                    // read headers
                    if ($row === 0) {
                        $headers = $data;
                    } else {
                        $content[] = $data;
                    }
                    $row++;
                }
            }

            fclose($handle);

            $results = array('errors' => 0, 'updated' => 0);

            // Check for invalid headers
            $matches = preg_grep('/^(post_title|post_content|fund_name|fund_value|investment_value|direct_investment|projected_indirect_investment|google_doc_url|companies\[[0-4]\]\[\'name\'\]|companies\[[0-4]\]\[\'value\'\])$/', $headers, PREG_GREP_INVERT);

            if ($matches) { ?>
                <div class="error">
                    <strong><?php _e("Invalid headers found:", Plugin::PLUGIN_NAME) ?></strong>
                    <ul>
                    <?php foreach($matches as &$match) : ?>
                        <li><?php echo esc_html($match); ?></li>
                    <?php endforeach?>
                    </ul>
                </div>
                <?php
            }

            // store the post data
            if ($headers && $content) {
                // read cols
                foreach ($content as $row => &$cols) {

                    $companies = array();

                    $post_title = $content[$row][array_search('post_title', $headers)];

                    $post = get_page_by_title($post_title, OBJECT, Plugin::POST_TYPE);

                    if (!$post) { ?>
                        <div class="error">
                            <p><?php echo sprintf(__("post_title `%s` does not match any existing post titles.", Plugin::PLUGIN_NAME), esc_html($post_title)); ?></p>
                        </div>
                        <?php
                        $results['errors']++;
                        continue;
                    } else {
                        $results['updated']++;
                    }

                    $post->post_status = 'publish';

                    foreach ($cols as $col => $val) {

                        $key = $headers[$col];

                        switch ($key) {
                            case 'post_title' :
                                continue 2; // skip to next col
                            case 'post_content' :
                                $post->post_content = sanitize_post_field('post_content', $val, $post->ID, 'display');
                            case 'fund_name' :
                                $val = trim(filter_var($val, FILTER_SANITIZE_STRING));
                                update_post_meta($post->ID, "_{$key}", $val);
                                continue 2;
                            case 'google_doc_url' :
                                $val = trim(filter_var($val, FILTER_SANITIZE_URL));
                                update_post_meta($post->ID, "_{$key}", $val);
                                continue 2;
                            case 'fund_value' :
                            case 'investment_value' :
                            case 'direct_investment' :
                            case 'projected_indirect_investment' :
                                $val = trim(filter_var($val, FILTER_SANITIZE_NUMBER_FLOAT, FILTER_FLAG_ALLOW_FRACTION));
                                update_post_meta($post->ID, "_{$key}", $val);
                                continue 2;
                        }

                        // build arrays for complex meta
                        $matches = array();

                        if (preg_match('/companies\[(\d+)\]\[\'name\'\]/', $key, $matches)) {
                            $companies[$matches[1]]['name'] = filter_var($val, FILTER_SANITIZE_STRING);
                        }

                        if (preg_match('/companies\[(\d+)\]\[\'value\'\]/', $key, $matches)) {
                            $companies[$matches[1]]['value'] = filter_var($val, FILTER_SANITIZE_STRING);
                        }
                    }

                    update_post_meta($post->ID, "_companies", $companies);

                    // publish the post so that it is displayed on the map
                    $post->post_status = 'publish';

                    wp_update_post($post);
                }

                ?>
                <p><?php _e("Import Complete!", Plugin::PLUGIN_NAME) ?></p>
                <ul>
                    <li><?php _e("Errors:", Plugin::PLUGIN_NAME) ?> <?php echo $results['errors']; ?></li>
                    <li><?php _e("Updated Posts:", Plugin::PLUGIN_NAME) ?> <?php echo $results['updated']; ?></li>
                </ul>
            <?php
            } else { ?>
                <p class="error"><?php _e("File had no recognized content!", Plugin::PLUGIN_NAME) ?></p>
            <?php
            }
        }
    }
}
