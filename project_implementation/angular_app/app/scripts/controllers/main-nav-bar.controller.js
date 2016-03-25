'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:MainNavBar
 * @description
 *
 *  * USE:
 * <sb-main-nav-bar config="configObject"></sb-main-nav-bar>
 *
 * configObject = {
 *   view: <the current view string identifier>,
 *   profile: {
		username: <string username>,
		role: <string user role>
	}
 * }
 *
 * view can be: 'main dashboard' | 'import export' | identifier for a module
 * 
 * # MainNavBar
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('MainNavBar', ['$scope', 'userAuthService', function($scope, userAuthService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.mainNavBar = {
		isOpen: true,
		navBarStyle: {
			// since browsers don't determine height in css form, we need to manually determine it here
			'height': '0px'
		},
		profileIsOpen: false,
	};

	// $scope.userAccess = null;

	$scope.mainNavBar.changeView = function(view) {
		$scope.mainNavBar.config.view = view;
		$scope.mainNavBar.config.subView = null
	};

	$scope.mainNavBar.changeSubView = function(subView, view) {
		// show active for parent module
		$scope.mainNavBar.config.view = view;
		$scope.mainNavBar.config.subView = subView;
	};

	$scope.mainNavBar.logout = function() {
		userAuthService.logoutUser();
		$scope.$emit("checkUserAuth");
	};


}])
.directive('sbMainNavBar', ['$window', '$translate', 'commonService', 'globalService', '$document', function($window, $translate, commonService, globalService, $document) {
	/**
	 * For manipulating the DOM
	 * @param  scope   as configured in the controller
	 * @param  element jqLite-wrapped element that matches this directive.
	 * @param  attrs   hash object with key-value pairs of normalized attribute names and their corresponding attribute values.
	 */
	function link(scope, element, attrs) {
		scope.translations = {
			signed_in: null
		};
		/**
		 * Provide config params to the controller
		 */
		function linkConfig () {
			scope.mainNavBar.config = scope.config;
		}

		/**
		 * Updates the height of the window as it is resized.
		 */
		function updateWindowSize () {
			// NOTE: later, if I don't want to make the nav bar fixed, we need to know what is larger: the browser window size or the body size and make the nav bar that size.
			// Make sure to update this anytime the body height changes and not just on browser window resizes (as it currently is)
			// // find the height of the body element and browser window and pick the larger of the two
			//var bodyHeight = $document[0].body.scrollHeight;
			var browserHeight = $window.innerHeight;
			// if (bodyHeight > browserHeight) {
			// 	browserHeight = bodyHeight;
			// }
			scope.mainNavBar.navBarStyle.height = browserHeight - 10 + "px"; // -10 for top-padding
		}

		/**
		 * Needed since window resize is handled outside of Angular's digest cycle.
		 */
		function applyAndCheckWindowSize () {
			scope.$apply(function(){
	        	updateWindowSize();
	        });
		}

		scope.toggleNavBar = function(isOpen) {
			scope.mainNavBar.isOpen = isOpen;
		};

		scope.toggleProfileSettings = function() {
			scope.profileIsOpen = !scope.profileIsOpen;
		};

		function getTranslations() {
			$translate("mainNavBar.SIGNED_IN").then(function (translation) {
				scope.translations.signed_in = commonService.format(translation, [scope.config.profile.username]);
			});
		};

		function getUserAccess() {
			scope.userAccess = globalService.getUserAccess();
		}

		/**** initial setup ****/
		linkConfig();
		getTranslations();
		getUserAccess();

		// check against the current window size when the browser loads.
		updateWindowSize();

		// anytime the window resizes, we need to know the new height.
		angular.element(window).on('resize', applyAndCheckWindowSize);

		// remove resources when no longer needed.
		scope.$on('$destroy', function () {
  			angular.element(window).off('resize', applyAndCheckWindowSize);
		});
	}

	/**
	 * restrict: directive is triggered by element (E) name
	 * scope: isolated scope
	 * templateUrl: where we find the template.html
	 * link: for manipulating the DOM
	 */
	return {
		restrict: 'E',
		scope: {
			config: '=config',
			mainNavBar: '=info'
		},
		templateUrl: 'views/main-nav-bar.html',
		link: link
	};
}]);