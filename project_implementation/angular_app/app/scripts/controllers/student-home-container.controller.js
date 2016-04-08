'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:StudentHomeContainer
 * @description
 *
 * 
 * # StudentHomeContainer
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('StudentHomeContainer', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];
	$scope.studentHomeContainer = {
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
.directive('sbStudentHomeContainer', [function() {
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
		templateUrl: 'views/student-home-container.html',
		link: link
	};
}]);