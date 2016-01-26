'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:AdminHomeContainer
 * @description
 *
 * 
 * # AdminHomeContainer
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('AdminHomeContainer', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];
	$scope.adminHomeContainer = {
		viewHeaderConfig: {
			title: "!!TITLE!!!",
			subTitle: "!!TEST!!",
			link: {
				text: "!!TEST2!!",
				action: null
			}
		}
	};

}])
.directive('sbAdminHomeContainer', [function() {
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
		templateUrl: 'views/admin-home-container.html',
		link: link
	};
}]);