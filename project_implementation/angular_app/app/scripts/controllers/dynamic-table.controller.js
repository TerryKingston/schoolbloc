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
.controller('DynamicTable', ['$scope', 'tableEntriesService', '$translate', 'commonService', function($scope, tableEntriesService, $translate, commonService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.tableConfig = null;
	$scope.tableView = null;
  $scope.tableText = {
    closedArrayEntry: null
  };

	function getTableEntries() {
		$scope.tableConfig = tableEntriesService.getTableConfiguration();

		setupTableView();
	}

	function setupTableView() {
		var i, row, j, k, entry;

    /**
     * Converts an object into a string,
     * specifically {min: x, max: y} --> "x-y"
     * and {start: x, end: y} --> "x-y"
     * Returns string if obj is object, otherwise returns obj
     */
    var convertObjectToString = function(obj) {
      if (!obj) {
        return null;
      }
      if (obj.min && obj.max) {
        return obj.min + "-" + obj.max;
      }
      else if (obj.start && obj.end) {
        return obj.start + "-" + obj.end;
      }
      return obj;
    };

		$scope.tableView = {
			headers: [],
			rows: []
		};

		// no entries
		if (!$scope.tableConfig.entries || !$scope.tableConfig.entries.length) {
			return;
		}

		$scope.tableView.headers = Object.keys($scope.tableConfig.entries[0]);

		for (i = 0; i < $scope.tableConfig.entries.length; i++) {
			row = [];
			for (j = 0; j < $scope.tableView.headers.length; j++) {
        entry = $scope.tableConfig.entries[i][$scope.tableView.headers[j]];
        if (Array.isArray(entry)) {
          // make sure there is actually objects in the array
          if (!entry.length) {
            entry = null;
          }
          else {
            for (k = 0; k < entry.length; k++) {
              entry[k] = convertObjectToString(entry[k]);
            }
            // specify that it is an array
            entry = {
              value: entry,
              type: "array",
              closedText: null,
              show: false
            };
            // add the "View X entries" text
            entry.closedText = commonService.format($scope.tableText.closedArrayEntry, entry.value.length + '');
          }
        }
        else {
          entry = convertObjectToString(entry);
        }
				row.push(entry);
			}
      $scope.tableView.rows.push(row);
		}
	}

  function getTranslations() {
    $translate("dynamicTable.CLOSED_TEXT").then(function (translation) {
      $scope.tableText.closedArrayEntry = translation;
    });
  }

  $scope.toggleShow = function(rowEntry, show) {
    rowEntry.show = show;
  };

  $scope.$watch('tableConfig.entries', setupTableView);

	/**** initial setup ****/
	getTableEntries();

  getTranslations();
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
