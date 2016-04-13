'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:ManageClasses
 * @description
 *
 * 
 * # ManageClasses
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('ManageClasses', ['$scope', '$translate', 'tableEntriesService', 'userAccessService', function($scope, $translate, tableEntriesService, userAccessService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.factSelection = null;
	$scope.manageStudents = null;

	function setupTableEntries() {
		$scope.factSelection = tableEntriesService.getTableSelections("student");
		$scope.factSelection = $scope.factSelection[0];
		tableEntriesService.updateTableConfig("fact", $scope.factSelection);
	}

	function getManagedStudents() {
		$scope.manageStudents = userAccessService.getUsersManagedStudents();
	}

	/**** initial setup ****/
	setupTableEntries();
	getManagedStudents();
}])
.directive('sbManageClasses', [function() {
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
		templateUrl: 'modules/scheduler/views/manage-classes.html',
		link: link
	};
}]);