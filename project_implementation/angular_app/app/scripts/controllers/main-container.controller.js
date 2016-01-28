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

}])
.directive('sbMainContainer', ['$translate', function($translate) {
	/**
	 * For manipulating the DOM
	 * @param  scope   as configured in the controller
	 * @param  element jqLite-wrapped element that matches this directive.
	 * @param  attrs   hash object with key-value pairs of normalized attribute names and their corresponding attribute values.
	 */
	function link(scope, element, attrs) {
		function getModuleTranslations() {
			$translate("schedulerModule.SCHEDULER").then(function (translation) {
				scope.mainContainer.navBarConfig.modules[0].name = translation;
			});

			$translate("schedulerModule.FACTS_CONSTRAINTS").then(function (translation) {
				scope.mainContainer.navBarConfig.modules[0].submodules[0].name = translation;
			});

		};

		/**** initial setup ****/
		getModuleTranslations();
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