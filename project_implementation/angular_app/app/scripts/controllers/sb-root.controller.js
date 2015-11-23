'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:SbRoot
 * @description
 *
 * User login page.
 * 
 * # SbRoot
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('SbRoot', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];
	$scope.sbRoot = {
		initialLoading: true,
		user: {
			authenticated: false,
			username: null,
			role: null
		},
		userAuthContainer: {
			errorCode: null
		}
	};

}])
.directive('sbSbRoot', ['userAuthService', 'globalService', function(userAuthService, globalService) {
	/**
	 * For manipulating the DOM
	 * @param  scope   as configured in the controller
	 * @param  element jqLite-wrapped element that matches this directive.
	 * @param  attrs   hash object with key-value pairs of normalized attribute names and their corresponding attribute values.
	 */
	function link(scope, element, attrs) {
		scope.sbRoot.stateUpdates = globalService.getStateUpdates();
		scope.$watch('sbRoot.stateUpdates.forbiddenState', setState);

		scope.$on("checkUserAuth", function (event, args) {
			determineJwtState();
		});

		/**
		 * If some trigger has asked for a state change, 
		 * determine which trigger and update the state accordingly.
		 * Resets the trigger once done.
		 */
		function setState() {
			if (scope.sbRoot.stateUpdates.forbiddenState) {
				scope.sbRoot.user.authenticated = false;
				// @TODO: update error message for child directive: user-auth-container
				scope.sbRoot.userAuthContainer.errorCode = "FORBIDDEN";
				// reset the trigger
				scope.sbRoot.stateUpdates.forbiddenState = false;
			}
		}

		/**
		 * Determines the state based on JWT.
		 * Sets necessary variables to accept the state.
		 */
		function determineJwtState() {
			// only returns username if JWT exists and hasn't expired
			scope.sbRoot.user.username = userAuthService.getUsername();
			// is the user already authenticated?
			if (scope.sbRoot.user.username) {
				scope.sbRoot.user.authenticated = true;
			}
			else {
				scope.sbRoot.user.authenticated = false;
			}

			scope.sbRoot.initialLoading = false;
		}

		/**********************
		 * Begin initial setup.
		 *********************/
		determineJwtState();
	}

	/**
	 * restrict: directive is triggered by element (E) name
	 * scope: isolated scope to $scope.sbRoot only
	 * templateUrl: where we find the template.html
	 * link: for manipulating the DOM
	 */
	return {
		restrict: 'E',
		scope: {
			sbRoot: '=info',
			sbView: '=view'
		},
		templateUrl: 'views/sb-root.html',
		link: link
	};
}]);