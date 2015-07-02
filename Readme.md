# jsseo

A way to render web pages that are generated on the client
side for web robots.

# How it Works

jsseo runs a headless browser like firefox or chrome using selenium  
jsseo crawls your site and stores a copy of every page in a mysql database  
jsseo then delivers pages to search engine crawlers on request  

# Features

Browser of your choice  
Runs headless  
Caches pages in mysql  
Automatically generates a sitemap  

# Installation

## Configuration Options

Configuration options are set in config.json  
Instructions in sample_config.json  

# Logs
# Note
I have only tested this with Firefox on Ubuntu Server  
It should work with other browsers as well  
