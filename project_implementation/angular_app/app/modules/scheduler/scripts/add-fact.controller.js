'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:AddFact
 * @description
 *
 * 
 * # AddFact
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('AddFact', ['$scope', 'tableEntriesService', function($scope, tableEntriesService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.addFactConfig = {
		showAddFact: false,
		addFactText: "!!Add Course",
		factTypeConfig: null
	};

	$scope.tableConfig = {

	};

	$scope.toggleAddFact = function (show) {
		$scope.addFactConfig.showAddFact = show;
	};

	$scope.saveFact = function (addAnotherFact) {
		// @TODO:
		
		if (!addAnotherFact) {
			$scope.addFactConfig.showAddFact = false;
		}
	};

	$scope.addInput = function (factInput, index) {
		var newFactInput = {}, 
			keys, i;

		keys = Object.keys(factInput);
		for (i = 0; i < keys.length; i++) {
			newFactInput[keys[i]] = factInput[keys[i]];
		}
		// mark it as an added input 
		newFactInput.addedValue = true;

		$scope.addFactConfig.factTypeConfig.splice(index + 1, 0, newFactInput);
	};

	$scope.removeInput = function (factInput, index) {
		$scope.addFactConfig.factTypeConfig.splice(index, 1);
	}

	$scope.$watch('tableConfig.tableSelection', updateFactType);

	function getTableConfig() {
		$scope.tableConfig = tableEntriesService.getTableConfiguration();
		updateFactType();
	}

	function updateFactType() {
		if ($scope.tableConfig.tableType === "fact" && $scope.tableConfig.tableSelection) {
			$scope.addFactConfig.factTypeConfig = tableEntriesService.getFactTypeConfig($scope.tableConfig.tableSelection);

			// make sure to grab the array of constraints for this fact type
			tableEntriesService.updateFactTypeFacts($scope.tableConfig.tableSelection);
		}
	}

	/**** initial setup ****/
	getTableConfig(); 
}])
.directive('sbAddFact', [function() {
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
		templateUrl: 'modules/scheduler/views/add-fact.html',
		link: link
	};
}]);