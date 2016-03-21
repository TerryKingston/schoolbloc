'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:UserAccess
 * @description
 *
 * 
 * # UserAccess
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('UserAccess', ['$scope', 'userAccessService', function($scope, userAccessService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];
	
	$scope.userAccess = {
		tokens: {}
	};

	function getAccessTokens() {
		userAccessService.getUserTokens().then(function(data) {
			$scope.userAccess.tokens = data;
		});
	}

	/**** initial setup ****/
	getAccessTokens();
}])
.directive('sbUserAccess', [function() {
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
		templateUrl: 'views/user-access.html',
		link: link
	};
}]);