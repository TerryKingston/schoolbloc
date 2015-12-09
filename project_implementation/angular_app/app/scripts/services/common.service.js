'use strict';

/**
 * Provides a lot of quick and basic functions that are useful and common among many areas of the app.
 */
angular.module('sbAngularApp').factory('commonService', ['$translate', '$window', '$location', function($translate, $window, $location) {
	
	/**
	 * Retreives the JWT token from local storage.
	 * @return {string} JWT token
	 */
	function getJwtToken() {
		// CITE: https://thinkster.io/angularjs-jwt-auth
		return $window.localStorage.jwtToken;
		// END CITE
	}

	return {

		/**
		 * Authenticates a URL with the JWT token.
		 * Append returned string to URL.
		 * This is only needed if a URL bypassing Angular (such as ng-src)
		 * @return {string}     token: add to URL
		 */
		authenticateUrl: function() {
			var token = userAuthService.getJwtToken();
			if (token) {
				return "?token=" + token;
			}
			return "";
		},

		/**
		 * Generates a valid portion of a URL based on the given value
		 * @param  value will be converted into URL
		 * @return       converted URL
		 */
		generateValidUrl: function(value) {
			if (!value) {
				return "";
			}
			return value.replace(/ /g,"-");
		},

		/**
		 * Renders the URL correctly with given port and absolute path if need be
		 */
		conformUrl: function(url) {
			// port of backend
			var port = "5000";
			return $location.protocol() + "://" + $location.host() + ":" + port + "/" + url;
		},

		/**
		 * Formats a given string value to replace all {x} with the given args[x].
		 * For example, "Hi {0}! This is {1}", where args[0] = "Bob" and args[1] = "Alice", then the return will be "Hi Bob! This is Alice"
		 * @param  {string} value The string value needed to be formatted.  Should contain "{x}", where x starts at 0 and incrementally goes up.
		 * @param  {array} args   Array of replacements for the {x} in the string value.
		 * @return {string}       Formatted string.
		 */
		format: function(value, args) {
			// @TODO: later, directly allow for: "This is a {0}".format("string")
			// CITE: https://gist.github.com/litera/9634958
			return value.replace(/\{(\d+)\}/g, function (match, capture) {
				// 1* so we can force capture to be a number
				return args[1*capture];
			});
			// END CITE
		}
	};
}]);