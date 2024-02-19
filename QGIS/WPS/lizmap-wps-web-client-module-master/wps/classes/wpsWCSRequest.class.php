<?php
/**
 * Manage WCS request.
 *
 * @author    3liz
 * @copyright 2015 3liz
 *
 * @see      http://3liz.com
 *
 * @license Mozilla Public License : http://www.mozilla.org/MPL/
 */
class wpsWCSRequest extends wpsOGCRequest
{
    protected $tplExceptions = 'wps~wcs_exception';

    protected function constructUrl()
    {
        if (!array_key_exists('service', $this->params)) {
            $this->params['service'] = 'WCS';
        }

        return parent::constructUrl();
    }

    protected function process_getcapabilities()
    {
        $result = parent::process_getcapabilities();

        $data = $result->data;
        if (empty($data) or floor($result->code / 100) >= 4) {
            jMessage::add('Server Error !', 'Error');

            return $this->serviceException();
        }

        if (preg_match('#ServiceExceptionReport#i', $data)) {
            return $result;
        }

        // Replace qgis server url in the XML (hide real location)
        $sUrl = jUrl::getFull(
            'wps~ows:index'
        );
        $sUrl = str_replace('&', '&amp;', $sUrl);
        preg_match('/<get>.*\n*.+xlink\:href="([^"]+)"/i', $data, $matches);
        if (count($matches) < 2) {
            preg_match('/get onlineresource="([^"]+)"/i', $data, $matches);
        }
        if (count($matches) < 2) {
            preg_match('/ows:get.+xlink\:href="([^"]+)"/i', $data, $matches);
        }
        if (count($matches) > 1) {
            $data = str_replace($matches[1], $sUrl, $data);
        }
        $data = str_replace('&amp;&amp;', '&amp;', $data);

        return (object) array(
            'code' => 200,
            'mime' => $result->mime,
            'data' => $data,
            'cached' => false,
        );
    }

    protected function process_describecoverage()
    {
        $result = $this->doRequest();

        if (!$result) {
            jMessage::add('Server Error !', 'Error');

            return $this->serviceException();
        }

        $data = $result->data;
        if (empty($data) or floor($result->code / 100) >= 4) {
            jMessage::add('Server Error !', 'Error');

            return $this->serviceException();
        }

        return $result;
    }

    protected function process_getcoverage()
    {
        $result = $this->doRequest();

        if (!$result) {
            jMessage::add('Server Error !', 'Error');

            return $this->serviceException();
        }

        $data = $result->data;
        if (empty($data) or floor($result->code / 100) >= 4) {
            jMessage::add('Server Error !', 'Error');

            return $this->serviceException();
        }

        return $result;
    }
}