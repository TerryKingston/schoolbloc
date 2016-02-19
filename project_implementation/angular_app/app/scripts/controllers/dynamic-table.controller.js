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
.controller('DynamicTable', ['$scope', 'tableEntriesService', '$translate', '$location', '$anchorScroll', 'commonService', function($scope, tableEntriesService, $translate, $location, $anchorScroll, commonService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.tableConfig = null;
	$scope.tableView = null;
  $scope.tableText = {
    closedArrayEntry: null,
    openedArrayEntry: null
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
      if (obj === null || typeof obj !== 'object') {
        return obj;
      }
      if ('min' in obj && 'max' in obj ) {
        return obj.min + "-" + obj.max;
      }
      else if ('start' in obj  && 'end' in obj ) {
        return obj.start + "-" + obj.end;
      }
      // if we reach here, there is an object that we aren't accounting for
      console.error("dynamicTable.convertObjectToString: unexpected state");
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
        // convert arrays into property objects as needed
        entry = $scope.tableConfig.entries[i][$scope.tableView.headers[j]];
        if (Array.isArray(entry)) {
          // check if there is actually objects in the array
          if (!entry.length) {
            // specify that it is an array
            entry = {
              value: null,
              type: "array"
            };
          }
          else {
            for (k = 0; k < entry.length; k++) {
              entry[k] = convertObjectToString(entry[k]);
            }
            // specify that it is an array
            entry = {
              value: entry,
              type: "array",
              text: null,
              closedText: null,
              openedText: $scope.tableText.openedArrayEntry,
              show: false
            };
            // add the "View X entries" text
            entry.closedText = commonService.format($scope.tableText.closedArrayEntry, entry.value.length + '');
            entry.text = entry.closedText;
          }
        }
        else {
          entry = convertObjectToString(entry);
        }
				row.push(entry);
			}
      $scope.tableView.rows.push(row);

      // DEBUG: adding constraint view
      if (i === 0) {
        $scope.tableView.rows.push({
          "type": "editor",
          "rowId": row[0], // unique id
          "constraintType": "course",
          "value": null,
          "priority": "mandatory",
          "constraints": ["test1"],
          "showFilters": true,
          "showFiltersText": $scope.tableText.hideFiltersText,
          "filters": [
            {
              "text": "!!Hide rooms already marked as mandatory",
              "checked": false
            },
            {
              "text": "!!Hide rooms not constrained by English",
              "checked": false
            },
            {
              "text": "!!Hide rooms that do not fit the course max",
              "checked": false
            },
            {
              "text": "!!Hide rooms already constrained",
              "checked": false
            }
          ]
        });
      }
		}
	}

  function getTranslations() {
    $translate("dynamicTable.CLOSED_TEXT").then(function (translation) {
      $scope.tableText.closedArrayEntry = translation;
    });

    $translate("dynamicTable.OPENED_TEXT").then(function (translation) {
      $scope.tableText.openedArrayEntry = translation;
    });

    $translate("dynamicTable.FILTERS_SHOW").then(function (translation) {
      $scope.tableText.showFiltersText = translation;
    });

    $translate("dynamicTable.FILTERS_HIDE").then(function (translation) {
      $scope.tableText.hideFiltersText = translation;
    });
  }

  $scope.toggleFilters = function(editor) {
    editor.showFilters = !editor.showFilters;
    if (editor.showFilters) {
      editor.showFiltersText = $scope.tableText.hideFiltersText;
    }
    else {
      editor.showFiltersText = $scope.tableText.showFiltersText;
    }
  };

  $scope.changePriority = function(editor, priority) {
    editor.priority = priority;
  };

  $scope.addConstraint = function() {
    // scroll to the editor box
    $location.hash('constraintEditor');
    $anchorScroll();
  };

  $scope.toggleShow = function(rowEntry) {
    rowEntry.show = !rowEntry.show;
    if (rowEntry.show) {
      rowEntry.text = rowEntry.openedText;
    }
    else {
      rowEntry.text = rowEntry.closedText;
    }
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
