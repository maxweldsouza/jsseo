var jsSeo;
(function () {
    'use strict';

    jsSeo = function(action) {
        var links = [];
        var hostname = window.location.origin;
        var options = {
            jsSeoUrl: 'http://localhost:4000/'
        }

        function sendCurrentPage(callback) {
            var path = window.location.href;
            var doctype = document.docType;
            var domcontent = document.documentElement.outerHTML;

            console.log('sending: ' + path);
            var postcontent = {
                content: domcontent,
            }
            $.ajax({
                url: options.jsSeoUrl + path,
                type: 'POST',
                data: postcontent,
                success: function (data, textStatus, jqXHR) {
                    callback();
                },
                error: function (jqXHR, textStatus, errorThrown)
                {
                }
            });
        }

        function getLinksFromPage() {
            /* extract all links from current page */
            var links = [];
            $('a').each(function () {
                links.push($(this).attr('href'));
            });
            return links;
        }

        function isInternal(a) {
            /* check whether a given url is internal */
            return a.indexOf('http') !== 0;
        }

        function internalAbsToRelative (a) {
            /* Converts absolute internal links to relative links */
            var origin = window.location.origin;
            if (a.indexOf(origin) === 0) {
                return a.substr(origin.length);
            }
            return a;
        }

        function getInternalLinks() {
            var links = getLinksFromPage();
            links = links.filter(isInternal);
            return links;
        }

        function nextPage () {
            var postcontent = {
                action: 'next-page',
                hostname: hostname
            }
            $.ajax({
                url: options.jsSeoUrl + 'api/v1',
                type: 'GET',
                data: postcontent,
                datatype: 'json',
                success: function (data, textStatus, jqXHR) {
                    if (typeof data['next-page'] !== 'undefined') {
                        window.location = data['next-page'];
                    } else {
                        console.log(data.message);
                    }
                },
                error: function (jqXHR, textStatus, errorThrown)
                {
                }
            });
        }

        function submitPaths (callback) {
            var postcontent = {
                action: 'submit-paths',
                paths: getInternalLinks()
            }
            if (links.length > 0) {
                $.ajax({
                    url: options.jsSeoUrl + 'api/v1',
                    type: 'GET',
                    data: postcontent,
                    datatype: 'json',
                    success: function (data, textStatus, jqXHR) {
                        console.log(data.message);
                        callback();
                    },
                    error: function (jqXHR, textStatus, errorThrown)
                    {
                    }
                });
            }
        }

        if (action === 'send') {
            /* start crawl */
            submitPaths();
            sendCurrentPage(function () {
                nextPage();
            });
        }
    }
}())
