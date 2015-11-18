'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:SuggestionList
 * @description
 *
 * USE:
 * <sb-suggestion-list config="configObject"></sb-suggestion-list>
 *
 * configObject = {
 *   
 * }
 * 
 * # SuggestionList
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('SuggestionList', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];


}])
.directive('sbSuggestionList', ['$translate', function($translate) {
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
	 * scope: isolated scope to $scope.suggestionList only
	 * templateUrl: where we find the template.html
	 * link: for manipulating the DOM
	 */
	return {
		restrict: 'E',
		scope: {
			config: '=config'
		},
		templateUrl: 'views/suggestion-list.html',
		link: link
	};
}]);