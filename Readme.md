# jsSeo

A way to render web pages that are generated on the client
side for web robots.

# How it Works

# Installation

## Configuration Options

These options can be changed in config.json. The database configuration
options are set during the installation process

browser: google-chrome or chromium
port:

certfile: path to the crt file for ssl
keyfile: path to the key file for ssl
ssl: set true to use ssl

database: name of the database
hostname: mysql hostname
username: mysql username
password: mysql password

headless: will run xvbf is set to true
installed: you can set this to true if you have manually set
    all configuration options for the database
logfile: path to the log file
remove_scripts: true by default. This will remove all <script> tags
    from html pages
