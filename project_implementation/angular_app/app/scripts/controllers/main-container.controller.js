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
	$scope.mainContainer = {
		
	};

}])
.directive('sbMainContainer', [function() {
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
	 * scope: isolated scope to $scope.mainContainer only
	 * templateUrl: where we find the template.html
	 * link: for manipulating the DOM
	 */
	return {
		restrict: 'E',
		scope: {
			mainView: '=view'
		},
		templateUrl: 'views/main-container.html',
		link: link
	};
}]);