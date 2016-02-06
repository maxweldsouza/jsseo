# jsseo

A way to render web pages that are generated on the client
side for web robots.

This was initially used at [Comparnion.com](https://comparnion.com).
It was called scantuary.com at that time. We used this to prerender pages
for googlebot. Although this worked fine, we have now moved to react.
Our site is isomorphic now so this repository is no longer used.

## How it Works

* jsseo runs a headless browser like firefox or chrome using selenium
* jsseo crawls your site and stores a copy of every page in a mysql database
* jsseo then delivers pages to search engine crawlers on request

## Features

* Supports _escaped_fragment_
* Browser of your choice
* Runs headless
* Caches pages in mysql
* Automatically generates a sitemap

## Installation

### Dependencies
* pyvirtualdisplay
* selenium
* mysql
* beautifulsoup
* tornado
* mysqldbhelper
* browsers: chromium/firefox/phantomjs

### Configuration Options

Configuration options are set in config.json.
Instructions in sample_config.json.

## Logs

## Note
Tested with Firefox on Ubuntu Server.
