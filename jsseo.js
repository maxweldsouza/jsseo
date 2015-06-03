var jsseo;
(function () {
    'use strict';

    jsseo = function() {
        var links = [];
        var hostname = window.location.origin;
        var options = {
            serviceurl: 'http://localhost:4000/'
        }


        function sendRequest(domcontent, path) {
            var postcontent = {
                content: domcontent,
            }
            $.ajax({
                url: options.serviceurl + path,
                type: 'POST',
                data: postcontent,
                success: function (data, textStatus, jqXHR) {
                },
                error: function (jqXHR, textStatus, errorThrown)
                {
                }
            });
        }

        function sendCurrentPage() {
            var url = window.location.href;
            var doctype = document.docType;
            var dom = document.documentElement.outerHTML;
            console.log('sending: ' + url);
            sendRequest(dom, url);
        }

        function getLinksFromPage() {
            /* extract all links from current page */
            var links = [];
            $('a').each(function () {
                links.push($(this).attr('href'));
            });
            return links;
        }

        function nextPage () {
            var postcontent = {
                action: 'next-page',
                hostname: hostname
            }
            $.ajax({
                url: options.serviceurl + 'api/v1',
                type: 'GET',
                data: postcontent,
                datatype: 'json',
                success: function (data, textStatus, jqXHR) {
                    if (typeof data['next-page'] !== 'undefined') {
                        window.location = data['next-page'];
                    }
                },
                error: function (jqXHR, textStatus, errorThrown)
                {
                }
            });
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

        /*
        if (action === 'test') {
            getLinksFromService();
        } else if (action === 'nextPage') {
            nextPage();
        } else if (action === 'start') {
        } else if (action == 'build-sitemap') {
        } else if (action === 'send') {
            var links = getLinks();
            links = links.map(internalAbsToRelative);
            links = links.filter(isInternal);
        }
        */

        /* start crawl */
        sendCurrentPage();
        nextPage();
    }
}())
