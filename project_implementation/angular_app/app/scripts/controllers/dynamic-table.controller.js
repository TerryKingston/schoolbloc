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
.controller('DynamicTable', ['$scope', '$timeout', 'tableEntriesService', '$translate', '$location', '$anchorScroll', 'commonService', function($scope, $timeout, tableEntriesService, $translate, $location, $anchorScroll, commonService) {
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

  $scope.tableOptions = {
    show: false,
    floatTableHeader: false
  };

  $scope.headerObj = {
    type: "header"
  };

  $scope.translations = {
    subject: null,
    teacher: null,
    course: null,
    student: null,
    classroom: null,
    student_group: null,
    name: null,
    first_name: null,
    last_name: null,
    room_number: null,
    student_count: null,
    max_student_count: null,
    min_student_count: null,
    avail_start_time: null,
    avail_end_time: null,
    start_time: null,
    end_time: null,
    timeblock: null,
    duration: null,
    user_id: null
  };

  $scope.editor = {
    "type": "editor",
    "rowId": null, // unique id
    "rowIndex": null, // where it sits in row
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
  };

	function getTableEntries() {
		$scope.tableConfig = tableEntriesService.getTableConfiguration();

		setupTableView();
	}

	function setupTableView() {
		var i, row, j, k, entry, keys, headerObj;

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
      headersIndex: 0,
      rows: []
    };

    // no entries
    if (!$scope.tableConfig.entries || !$scope.tableConfig.entries.length) {
      return;
    }

    // prepare headers
    $scope.tableView.headers = [];
    keys = Object.keys($scope.tableConfig.entries[0])
    for (i = 0; i < keys.length; i++) {
      // ignore ids
      if (keys[i] === "id") {
        continue;
      }
      $scope.tableView.headers.push({
        value: keys[i],
        text: $scope.translations[keys[i]],
        show: true
      });
    }

    for (i = 0; i < $scope.tableConfig.entries.length; i++) {
      row = [];
      for (j = 0; j < $scope.tableView.headers.length; j++) {
        // convert arrays into property objects as needed
        entry = $scope.tableConfig.entries[i][$scope.tableView.headers[j].value];
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
              entry[k].value = convertObjectToString(entry[k].value);
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
        else if ($scope.tableView.headers[j].value === 'disabled') {
          entry = {
            value: entry,
            type: "disabled"
          }
        }
        // ignore ids
        else if ($scope.tableView.headers[j].value === 'id') {
          continue;
        }
        else {
          entry = convertObjectToString(entry);
        }
        row.push(entry);
      }
      $scope.tableView.rows.push(row);
    }

    // add header to rows before first row
    headerObj = {
      type: "header"
    };
    $scope.tableView.rows.splice($scope.tableView.headerIndex, 0, headerObj);
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

  $scope.toggleTableOptions = function(show) {
    if (typeof show === 'undefined') {
      $scope.tableOptions.show = !$scope.tableOptions.show;
    }
    else {
      $scope.tableOptions.show = show;
    }
  }

  $scope.moveHeader = function(rowIndex, forceMove) {

    // if floating table header is turned off, do not float it
    if (!$scope.tableOptions.floatTableHeader && !forceMove) {
      return;
    }

    if (rowIndex === 0) {
      rowIndex ++;
    }
    // remove old header row
    $scope.tableView.rows.splice($scope.tableView.headerIndex, 1);
    // update header row to rowIndex
    $scope.tableView.headerIndex = rowIndex - 1;
    $scope.tableView.rows.splice($scope.tableView.headerIndex, 0, $scope.headerObj);
  }

  $scope.resetHeader = function(rowIndex) {
    $timeout(function() {
        $scope.moveHeader(0, true);
    }, 100);
  }

  $scope.changePriority = function(editor, priority) {
    editor.priority = priority;
  };

  $scope.editConstraint = function(rowIndex) {
    placeEditor(rowIndex);
  };

  $scope.addConstraint = function(rowIndex) {
    placeEditor(rowIndex);
  };

  $scope.cancelEditor = function() {
    resetEditor();
  };

  function placeEditor(rowIndex) {
    // determine if row index is affected by an already in place editor, and reconfigure if needed
    if ($scope.editor.rowIndex !== null && rowIndex > $scope.editor.rowIndex) {
      rowIndex--;
    }

    // remove any previous editor
    resetEditor();

    // add editor into rows
    $scope.editor.rowIndex = rowIndex;
    $scope.tableView.rows.splice(rowIndex, 0, $scope.editor);
    
    // need timeout for it to be placed in html template
    // scroll to the editor box
    $timeout(function() {
        $location.hash('constraintEditor');
        $anchorScroll();
    }, 100);
  }

  function resetEditor() {
    if ($scope.editor.rowIndex !== null) {
      $scope.tableView.rows.splice($scope.editor.rowIndex, 1);
    }

    $scope.editor.rowIndex = null;
    $scope.editor.rowId = null;
    $scope.editor.constraintType = null;
    $scope.editor.value = null;
    $scope.editor.priority = "mandatory";
    $scope.editor.constraints = [];
    $scope.editor.showFilters = true;
    $scope.editor.filters = [];
  }

  $scope.toggleAllEntries = function(index, show) {
    var i;
    debugger;
    for (i = 0; i < $scope.tableView.rows.length; i++) {
      // skip the header
      if ($scope.tableView.rows[i].type === "header") {
        continue;
      }
      $scope.toggleShow($scope.tableView.rows[i][index], show);
    }
  }

  $scope.toggleShow = function(rowEntry, forceShow) {
    if (typeof forceShow === 'undefined') {
      rowEntry.show = !rowEntry.show;
    }
    else {
      rowEntry.show = forceShow;
    }
    if (rowEntry.show) {
      rowEntry.text = rowEntry.openedText;
    }
    else {
      rowEntry.text = rowEntry.closedText;
    }
  };


  function getTranslations() {
    $translate("dynamicTable.SUBJECT").then(function (translation) {
      $scope.translations.subject = translation;
    });

    $translate("dynamicTable.TEACHER").then(function (translation) {
      $scope.translations.teacher = translation;
    });

    $translate("dynamicTable.COURSE").then(function (translation) {
      $scope.translations.course = translation;
    });

    $translate("dynamicTable.STUDENT").then(function (translation) {
      $scope.translations.student = translation;
    });

    $translate("dynamicTable.CLASSROOM").then(function (translation) {
      $scope.translations.classroom = translation;
    });

    $translate("dynamicTable.STUDENT_GROUP").then(function (translation) {
      $scope.translations.student_group = translation;
    });

    $translate("dynamicTable.NAME").then(function (translation) {
      $scope.translations.name = translation;
    });

    $translate("dynamicTable.FIRST_NAME").then(function (translation) {
      $scope.translations.first_name = translation;
    });

    $translate("dynamicTable.LAST_NAME").then(function (translation) {
      $scope.translations.last_name = translation;
    });

    $translate("dynamicTable.ROOM_NUMBER").then(function (translation) {
      $scope.translations.room_number = translation;
    });

    $translate("dynamicTable.STUDENT_COUNT").then(function (translation) {
      $scope.translations.student_count = translation;
    });

    $translate("dynamicTable.MAX_STUDENT_COUNT").then(function (translation) {
      $scope.translations.max_student_count = translation;
    });

    $translate("dynamicTable.MIN_STUDENT_COUNT").then(function (translation) {
      $scope.translations.min_student_count = translation;
    });

    $translate("dynamicTable.AVAIL_START_TIME").then(function (translation) {
      $scope.translations.avail_start_time = translation;
    });

    $translate("dynamicTable.AVAIL_END_TIME").then(function (translation) {
      $scope.translations.avail_end_time = translation;
    });

    $translate("dynamicTable.START_TIME").then(function (translation) {
      $scope.translations.start_time = translation;
    });

    $translate("dynamicTable.END_TIME").then(function (translation) {
      $scope.translations.end_time = translation;
    });

    $translate("dynamicTable.TIMEBLOCK").then(function (translation) {
      $scope.translations.timeblock = translation;
    });

    $translate("dynamicTable.DURATION").then(function (translation) {
      $scope.translations.duration = translation;
    });

    $translate("dynamicTable.USER_ID").then(function (translation) {
      $scope.translations.user_id = translation;
    });




    $translate("dynamicTable.SHOW_NUMBER").then(function (translation) {
      $scope.tableText.closedArrayEntry = translation;
    });

    $translate("dynamicTable.HIDE_ALL").then(function (translation) {
      $scope.tableText.openedArrayEntry = translation;
    });

    $translate("dynamicTable.FILTERS_SHOW").then(function (translation) {
      $scope.tableText.showFiltersText = translation;
    });

    $translate("dynamicTable.FILTERS_HIDE").then(function (translation) {
      $scope.tableText.hideFiltersText = translation;
    });
  }

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
