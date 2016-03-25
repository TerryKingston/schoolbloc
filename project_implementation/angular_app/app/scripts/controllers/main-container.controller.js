'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:MainContainer
 * @description
 *
 * 
 * # MainContainer
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('MainContainer', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.mainNavBar = null;
	// $scope.userAccess = null;
}])
.directive('sbMainContainer', ['$translate', 'globalService', function($translate, globalService) {
	/**
	 * For manipulating the DOM
	 * @param  scope   as configured in the controller
	 * @param  element jqLite-wrapped element that matches this directive.
	 * @param  attrs   hash object with key-value pairs of normalized attribute names and their corresponding attribute values.
	 */
	function link(scope, element, attrs) {
		scope.userAccess = {
			role: null
		};

		function getModuleTranslations() {
			if (scope.userAccess && scope.userAccess.role === 'admin') {
				$translate("schedulerModule.SCHEDULER").then(function (translation) {
					scope.mainContainer.navBarConfig.modules[0].name = translation;
				});

				$translate("schedulerModule.FACTS_CONSTRAINTS").then(function (translation) {
					scope.mainContainer.navBarConfig.modules[0].submodules[0].name = translation;
				});
			}
			else if (scope.userAccess && scope.userAccess.role === 'parent' || scope.userAccess.role === 'student') {
				$translate("schedulerModule.SCHEDULE").then(function (translation) {
					scope.mainContainer.navBarConfig.modules[0].name = translation;
				});

				$translate("schedulerModule.MANAGE_CLASSES").then(function (translation) {
					scope.mainContainer.navBarConfig.modules[0].submodules[0].name = translation;
				});
			}
		};

		function getUserAccess() {
			scope.userAccess = globalService.getUserAccess();
			getModuleTranslations();
		}

		function roleChange() {
			getModuleTranslations();
		}

		scope.$watch('userAccess.role', roleChange);

		/**** initial setup ****/
		getUserAccess();
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
			mainView: '=view',
			mainContainer: '=info'
		},
		templateUrl: 'views/main-container.html',
		link: link
	};
}]);