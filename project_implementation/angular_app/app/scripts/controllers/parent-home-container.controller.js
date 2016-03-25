'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:ParentHomeContainer
 * @description
 *
 * 
 * # ParentHomeContainer
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('ParentHomeContainer', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];
	$scope.parentHomeContainer = {
		viewHeaderConfig: {
			title: "mainDashboard.TITLE",
			subTitle: "mainDashboard.SUBTITLE",
			link: {
				text: "mainDashboard.SUBTITLE_ACTION",
				action: null
			}
		}
	};

}])
.directive('sbParentHomeContainer', [function() {
	/**
	 * For manipulating the DOM
	 * @param  scope   as configured in the controller
	 * @param  element jqLite-wrapped element that matches this directive.
	 * @param  attrs   hash object with key-value pairs of normalized attribute names and their corresponding attribute values.
	 */
	function link(scope, element, attrs) {
		
	}

	/**
	 * restrict: directive is triggered by element (E) name
	 * scope: isolated scope
	 * templateUrl: where we find the template.html
	 * link: for manipulating the DOM
	 */
	return {
		restrict: 'E',
		templateUrl: 'views/parent-home-container.html',
		link: link
	};
}]);