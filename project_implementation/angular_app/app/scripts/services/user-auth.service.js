'use strict';

/**
 * Helps with basic user authentication and registration.
 */
angular.module('sbAngularApp').factory('userAuthService', ['$q', '$http', '$window', 'commonService', function($q, $http, $window, commonService) {
	var SERVER_ROOT = "",
		REGISTER_URL = SERVER_ROOT + "/register",
		LOGIN_URL = SERVER_ROOT + "auth";

	/**
	 * Parses a given JWT token so that its claim is in a JSON readable format.
	 * @param  {string} token JWT token; as sent from server
	 * @return {object}       JSON object that represents the JWT token.
	 */
	function parseJwtTokenClaim(token) {
		// token = "<base64-encoded header>.<base64-encoded claims>.<base64-encoded signature>"
		
		// CITE: https://thinkster.io/angularjs-jwt-auth
		// we are only interested in the <base64-encoded claims> as the other components are only necessary for the server
		// NOTE: this may not be true as we may need to verify the token is correct.  See https://developer.atlassian.com/static/connect/docs/latest/concepts/understanding-jwt.html
		var base64Url = token.split('.')[1];
		var base64 = base64Url.replace('-', '+').replace('_', '/');
		// atob = a to b: decodes string using base64 encoding
		return JSON.parse($window.atob(base64));
		// END CITE
	}

	return {
		
		/**
		 * Attempts to register the user with the given credentials
		 */
		registerUser: function(username, password, fullname) {
			var data;
			var url = commonService.conformUrl(REGISTER_URL);
			var deferred = $q.defer();

			data = {
				username: username,
				password: password,
				fullName: fullname
			};

			$http.post(url, data).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				deferred.reject(data.data);
			});
			return deferred.promise;
		},

		/**
		 * Attempts to log in the user with the given credentials
		 */
		loginUser: function(username, password) {
			var data;
			var url =  commonService.conformUrl(LOGIN_URL);
			var deferred = $q.defer();

			data = {
				username: username,
				password: password
			};

			$http.post(url, data).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				deferred.reject(data.data);
			});
			return deferred.promise;
		},

		/**
		 * Log a user out of the app.  A user must log in afterwards for authentication.
		 */
		logoutUser: function() {
			// delete the JWT token so that the user would need to reauthenticate
			$window.localStorage.removeItem('jwtToken');
		},

		/**
		 * Returns whether or not the user is authenticated against the server
		 * @return {Boolean} true if user is authenticated, false otherwise
		 */
		isUserAuthenticated: function() {
			var self = this,
				token = self.getJwtToken();
			// is there a stored token and is the exp (expiration) property of the JSON parsed token expired?
			// CITE: https://thinkster.io/angularjs-jwt-auth
			return token && (Math.round(new Date().getTime() / 1000) <= parseJwtTokenClaim(token).exp);
			// END CITE
		},

		/**
		 * Returns the current user's username if the JWT token is valid.
		 * @return {string} username associate with current JWT token
		 */
		getUsername: function() {
			var self = this;
			if (self.isUserAuthenticated()) {
				// flask-JWT is only returning the identity
				return parseJwtTokenClaim(self.getJwtToken()).identity;
			}
			// @TODO: what do we do if the token has expired or there is no token?
		},

		/**
		 * Saves the JWT token to local storage.  
		 * Make sure to only call this function if the token is validated.
		 * @param  {string} token JWT token
		 */
		saveJwtToken: function(token) {
			// CITE: https://thinkster.io/angularjs-jwt-auth
			$window.localStorage.jwtToken = token;
			// END CITE
		},

		/**
		 * Retreives the JWT token from local storage.
		 * @return {string} JWT token
		 */
		getJwtToken: function() {
			// CITE: https://thinkster.io/angularjs-jwt-auth
			return $window.localStorage.jwtToken;
			// END CITE
		}
	};
}]);