'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:FactsConstraints
 * @description
 *
 * 
 * # FactsConstraints
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('FactsConstraints', ['$scope', 'tableEntriesService', function($scope, tableEntriesService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.factSelections = null;
	$scope.factSelection = null;

	function setupTableEntries() {
		$scope.factSelections = tableEntriesService.getTableSelections("fact");
		if ($scope.factSelections && $scope.factSelections.length) {
			$scope.factSelection = $scope.factSelections[0];
			// setup fact view to be defined for a particular fact (in this case, 'classroom')
			tableEntriesService.updateTableConfig("fact", $scope.factSelection);
		}
	}

	$scope.updateSelection = function() {
		// factSelection is set by ng-model in view
		tableEntriesService.updateTableConfig("fact", $scope.factSelection);
	}

	/**** initial setup ****/
	setupTableEntries();
}])
.directive('sbFactsConstraints', [function() {
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
		templateUrl: 'modules/scheduler/views/facts-constraints.html',
		link: link
	};
}]);