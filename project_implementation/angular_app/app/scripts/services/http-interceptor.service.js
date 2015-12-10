'use strict';

/**
 * HTTP Interceptor
 * As explained by: https://docs.angularjs.org/api/ng/service/$http#interceptors
 *
 * This is a way to intercept the http request/response to attach/retrieve the JWT token for user authorization. 
 */
angular.module('sbAngularApp').factory('httpInterceptorService', ['$q', '$window', "$location", 'globalService', function($q, $window, $location, globalService) {
	/**
	 * Saves the JWT token to local storage.  
	 * Make sure to only call this function if the token is validated.
	 * @param  {string} token JWT token
	 */
	function saveJwtToken(token) {
		// CITE: https://thinkster.io/angularjs-jwt-auth
		$window.localStorage.jwtToken = token;
		// END CITE
	}

	/**
	 * Retreives the JWT token from local storage.
	 * @return {string} JWT token
	 */
	function getJwtToken() {
		// CITE: https://thinkster.io/angularjs-jwt-auth
		return $window.localStorage.jwtToken;
		// END CITE
	}

	/**
	 * Removes the JWT token from local storage.
	 */
	function removeJwtToken() {
		// delete the JWT token so that the user would need to reauthenticate
		$window.localStorage.removeItem('jwtToken');
	}


	return {

		/**
		 * Attaches the JWT authorization header to http requests
		 * @param  {object} config object that is about to be sent in request
		 */
		request: function(config) {
			var token = getJwtToken();

			/* NOTE: for now, we assume that ALL requests must be authenticated.
			*  This constraint may not be true later: if we don't have secured data to request,
			*  we should uncomment out the if statement and comment out the other statement
			*/
			// CITE: https://thinkster.io/angularjs-jwt-auth
			//if (token && (config.url.indexOf("/auth") !== -1 || config.url.indexOf("/app-data") !== -1)) {
			//	config.headers.Authorization = 'JWT ' + token;
			//}
			// END CITE
			
			if (token) {
				config.headers.Authorization = 'JWT ' + token;
			}
			
			return config;
		},

		// NOTE: can't determine a reason why we need this yet
		// requestError: function(rejection) {
		// 	if (canRecover(rejection)) {
		// 		// @TODO:
		// 		return responseOrNewPromise;
		// 	}
		// 	return $q.reject(rejection);
		// },

		/**
		 * Retreives the user JWT token, if it was sent
		 * @param  {object} response object that was sent from server
		 */
		response: function(response) {
			// NOTE: see request() for more information:
			//if (response.config.url.indexOf("/auth") !== -1 || response.config.url.indexOf("/app-data") !== -1)
			if (response.data.access_token) {
				saveJwtToken(response.data.access_token);
			}

			return response;
		},

		/**
		 * Response failed.  
		 * Checks failed request for forbidden code (403).
		 * If so, redirect to login page.
		 * @param  {object} rejection object that was sent from server
		 */
		responseError: function(rejection) {
			var stateUpdates;

			// forbidden: redirect to login page
			if (rejection.status === 403) {

				// @TODO: do we want to remove the token? Not really, what if they are accessing a part of the website that they are allowed to be at?
				// But what do we do when a token expires?
				stateUpdates = globalService.getStateUpdates();
				stateUpdates.forbiddenState = true;
				// removeJwtToken();
				
				//$window.location.href = $window.location.href + "login";
				// $location.path("/login");
				// $location.replace();
				return;
			}

			return $q.reject(rejection);
		}
	};
}]);


/**
 * "The interceptors are service factories that are registered 
 * with the $httpProvider by adding them to the $httpProvider.interceptors 
 * array. The factory is called and injected with dependencies (if specified) 
 * and returns the interceptor."
 * SOURCE: https://docs.angularjs.org/api/ng/service/$http#interceptors
 */
angular.module('sbAngularApp').config(function ($httpProvider) {
	$httpProvider.interceptors.push('httpInterceptorService');
});