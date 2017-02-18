<?php

namespace FossilFuelDivestmentMap;

if (!defined('ABSPATH')) {
    exit; // exit if accessed directly
}

/**
 * Code for displaying the Fossil Fuel Divestment Box shortcode
 *
 */
if(!class_exists('FossilFuelDivestmentMap\BoxShortcode')) :

    /**
     * FossilFuelDivestmentMap\BoxShortcode
     *
     * @class FossilFuelDivestmentMap\BoxShortcode
     *
     */
    class BoxShortcode {

        const BOX_ID = 'fossil-fuel-map-totals-box';

        /**
         * constructor
         *
         */
        public function __construct() {
            // register shortcode
            add_shortcode(Plugin::PLUGIN_NAME . '-box', array($this, 'shortcode'));

            // register css
            add_action('wp_enqueue_scripts', array($this, 'register_css'));
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
         * shortcode
         *
         * Add a shortcode [fossil_fuel_divestment_map] to display the map
         *
         * @atts - shortcode attributes array
         * @return void
         */
        public function shortcode ($atts) {

            // params
            $defaults = array(
                'fund_value' => 0,
                'investment_value' => 0,
            );

            $atts = shortcode_atts($defaults, $atts, Plugin::PLUGIN_NAME);

            // enque scripts / styles
            wp_enqueue_style(Plugin::PLUGIN_NAME);

            ?>
            <table id="<?php echo self::BOX_ID; ?>">
                <tbody>
                    <tr>
                        <td><strong><?php _e("Total Pension Fund Value:", Plugin::PLUGIN_NAME); ?></strong></td>
                        <td><?php echo esc_html($atts['fund_value']); ?></td>
                    </tr>
                    <tr>
                        <td><strong><?php _e("Total Fossil Fuel Investments", Plugin::PLUGIN_NAME); ?></strong></td>
                        <td><?php echo esc_html($atts['investment_value']); ?></td>
                    </tr>
                </tbody>
            </table>
        <?php
        }
    }

endif;