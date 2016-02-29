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
.controller('FactsConstraints', ['$scope', '$translate', 'tableEntriesService', function($scope, $translate, tableEntriesService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.factSelections = null;
	$scope.factSelection = null;
	$scope.factSelectionText = null;
	$scope.factSelectionsText = null;

	function updateFactSelectionText() {
		var i;

		$scope.factSelectionsText = [];

		if (!$scope.factSelections || !$scope.factSelections.length) {
			return;
		}
		for (i = 0; i < $scope.factSelections.length; i++) {
			$translate("schedulerModule." + $scope.factSelections[i].toUpperCase()).then(function (translation) {
				$scope.factSelectionsText.push(translation);

				// once the last one has been translated, update the factSelectionText
				if ($scope.factSelectionsText.length === $scope.factSelections.length) {
					$scope.factSelectionText = $scope.factSelectionsText[0];
				}
			});
		}
	}

	function setupTableEntries() {
		$scope.factSelections = tableEntriesService.getTableSelections("fact");
		updateFactSelectionText();
		if ($scope.factSelections && $scope.factSelections.length) {
			$scope.factSelection = $scope.factSelections[0];
			// setup fact view to be defined for a particular fact (in this case, 'classroom')
			tableEntriesService.updateTableConfig("fact", $scope.factSelection);
		}
	}

	$scope.updateSelection = function() {
		var i;
		// convert from text to obj key
		for (i = 0; i < $scope.factSelectionsText.length; i++) {
			if ($scope.factSelectionsText[i] === $scope.factSelectionText) {
				$scope.factSelection = $scope.factSelections[i];
			}
		}
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