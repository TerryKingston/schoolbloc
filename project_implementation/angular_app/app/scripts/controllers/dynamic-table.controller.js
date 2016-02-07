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
		var i, rowEntry, j, k, z;
    var srowItem = "",tmpRowItem = "";
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

      // Converts each object or array to a string
      for (k = 0; k < Object.keys(rowEntry).length; k++) {

        // If array
        if(Array.isArray(rowEntry[k])) {

          // If the array contains objects
          if (!Array.isArray(rowEntry[k][0]) && typeof(rowEntry[k][0]) == 'object') {
            if(typeof rowEntry[k][0].min !== "undefined")
            {
              srowItem = rowEntry[k][0].min + "-" + rowEntry[k][0].max;
            }
            else if(typeof rowEntry[k][0].start !== "undefined")
            {
              srowItem = rowEntry[k][0].start + "-" + rowEntry[k][0].end;
            }
            for (z = 1; z < Object.keys(rowEntry[k]).length; z++) {
              tmpRowItem = rowEntry[k][z];
              if(typeof tmpRowItem.min !== "undefined")
              {
                srowItem = srowItem + ", " + tmpRowItem + "-" + rowEntry[k].max;
              }
              else if(typeof tmpRowItem.start !== "undefined")
              {
                srowItem = srowItem + ", " + rowEntry[k][z].start + "-" + rowEntry[k][z].end;
              }
            }
            rowEntry[k] = srowItem;
          }
          // If the array does not contain objects
          else
          {
            srowItem = rowEntry[k][0]
            for(z = 1; z < Object.keys(rowEntry[k]).length; z++)
            {
              srowItem = srowItem + ", " +  rowEntry[k][z];
            }
            rowEntry[k] = srowItem;
          }
        }
          // If object
          else if(rowEntry[k] !== null && typeof(rowEntry[k]) == 'object')
          {
            if(typeof rowEntry[k].min !== "undefined")
            {
              tmpRowItem = rowEntry[k].min;
              rowEntry[k] = tmpRowItem + "-" + rowEntry[k].max;
            }
            else {
              tmpRowItem = rowEntry[k].start;
              rowEntry[k] = tmpRowItem + "-" + rowEntry[k].end;
            }
          }


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
