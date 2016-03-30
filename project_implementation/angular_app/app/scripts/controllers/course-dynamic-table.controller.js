'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:CourseDynamicTable
 * @description
 *
 *
 * # CourseDynamicTable
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('CourseDynamicTable', ['$scope', '$timeout', 'tableEntriesService', '$translate', '$location', '$anchorScroll', 'commonService', function($scope, $timeout, tableEntriesService, $translate, $location, $anchorScroll, commonService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.tableConfig = null;
	$scope.tableView = null;


  $scope.deleteRow = function(index) {
    debugger;
    console.error("TODO");
  }


	function getTableEntries() {
		$scope.tableConfig = tableEntriesService.getTableConfiguration();
		setupTableView();
	}

	function setupTableView() {
		var i, row, j, k, entry, keys, headerObj;

    $scope.tableView = {
      requiredCourses: [],
      electiveCourses: []
    };

    // no entries
    if (!$scope.tableConfig.entries || !$scope.tableConfig.entries.length) {
      return;
    }

    keys = Object.keys($scope.tableConfig.entries[0]);
    for (i = 0; i < $scope.tableConfig.entries.length; i++) {
      row = [];
      row.push($scope.tableConfig.entries[i].course);
      if ($scope.tableConfig.entries[i].required) {
        $scope.tableView.requiredCourses.push(row);
      }
      else {
        // rank is @ index 1
        row.push($scope.tableConfig.entries[i].rank);
        row.push($scope.tableConfig.entries[i].id);
        $scope.tableView.electiveCourses.push(row);
      }
    }

    // sort elective based on rank
    sortElectivesArrayByRank();
  }

  function sortElectivesArrayByRank() {
    var i, j, newRankArr = [], ec;

    ec = $scope.tableView.electiveCourses;

    if (!ec.length) {
      return;
    }

    for (i = 0; i < ec.length; i++) {
      for (j = 0; j < ec.length; j++) {
        // rank is @ index 1
        if (ec[j][1] - 1 === i) {
          newRankArr.push(ec[j]);
        }
      }
    }

    $scope.tableView.electiveCourses = newRankArr;
  }

  $scope.$watch('tableConfig.entries', setupTableView);

	/**** initial setup ****/
	getTableEntries();
}])
.directive('sbCourseDynamicTable', [function() {
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
		templateUrl: 'views/course-dynamic-table.html',
		link: link
	};
}]);
