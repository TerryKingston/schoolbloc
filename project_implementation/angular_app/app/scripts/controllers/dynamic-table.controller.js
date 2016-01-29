'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:DynamicTable
 * @description
 *
 * 
 * # DynamicTable
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('DynamicTable', ['$scope', 'tableEntriesService', function($scope, tableEntriesService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.tableConfig = null;
	$scope.tableView = null;

	function getTableEntries() {
		$scope.tableConfig = tableEntriesService.getTableConfiguration();

		setupTableView();
	}

	function setupTableView() {
		var i, rowEntry, j;

		$scope.tableView = {
			headers: [],
			rows: []
		};

		// no entries
		if (!$scope.tableConfig.entries.length) {
			return;
		}

		$scope.tableView.headers = Object.keys($scope.tableConfig.entries[0]);

		for (i = 0; i < $scope.tableConfig.entries.length; i++) {
			rowEntry = [];
			for (j = 0; j < $scope.tableView.headers.length; j++) {
				rowEntry.push($scope.tableConfig.entries[i][$scope.tableView.headers[j]]);
			}
			$scope.tableView.rows.push(rowEntry);
		}
	}

	/**** initial setup ****/
	getTableEntries();
}])
.directive('sbDynamicTable', [function() {
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
		templateUrl: 'views/dynamic-table.html',
		link: link
	};
}]);