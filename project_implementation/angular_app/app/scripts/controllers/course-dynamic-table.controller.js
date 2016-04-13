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
  $scope.readyForSortable = false;
  $scope.selectedRow = {
    index: null,
    delete: false
  };

  $scope.editor = {
    "type": "editor",
    "subType": null,
    "rowIndex": null, // where it sits in row
    "key": null, // course, classroom, student_group
    "selectedEntry": null, // reference to selected entry to keep track of edit
    "error": null
  };

  // $scope.deleteRow = function(rowIndex) {
  //   // determine if row index is affected by an already in place editor, and reconfigure if needed
  //   if ($scope.editor.rowIndex !== null && rowIndex > $scope.editor.rowIndex) {
  //     rowIndex--;
  //   }

  //   resetEditor();

  //   // because now the rowIndex is the editor
  //   $scope.selectedRow.index = rowIndex + 1;
  //   $scope.selectedRow.delete = true;

  //   $scope.editor.subType = 'delete-row';

  //   // add editor into rows
  //   $scope.editor.rowIndex = rowIndex;
  //   $scope.tableView.electiveCourses.splice(rowIndex, 0, $scope.editor);
  // };

  $scope.cancelEditor = function() {
    resetEditor();
  };

  function resetEditor() {
    // deal with removing the selected entry
    if ($scope.editor.selectedEntry) {
      $scope.editor.selectedEntry.isSelected = false;
    }

    if ($scope.editor.rowIndex !== null) {
      $scope.tableView.electiveCourses.splice($scope.editor.rowIndex, 1);
    }

    $scope.selectedRow.index = null;
    $scope.selectedRow.delete = false;

    $scope.editor.error = null;
    $scope.editor.selectedEntry = null;
    $scope.editor.rowIndex = null;
    $scope.editor.subType = null;
    $scope.editor.key = null;
    $scope.skipCourseOfId = null;
  }

  /**
   * We use this instead of the constraint editor $scope.deleteRow --> $scope.confirmDeleteRow typical method
   * because the constraint editor is part of the rows 
   * and is therefore ui:sortable (moveable), which causes all sorts of headaches
   */
  $scope.forceDeleteRow = function(rowIndex) {
    var i, courseId, method;

    // rowIndex is one off because of header being in the row
    courseId = $scope.tableView.electiveCourses[rowIndex][2];

    tableEntriesService.deleteFact(courseId, 'student_course').then(function (data) {
      // reset the form
      $scope.cancelEditor();

      // update the table to contain the new information
      tableEntriesService.updateTableConfig("fact", $scope.tableConfig.tableSelection);
    }, function(error) {
      $translate("dynamicTable.EDITOR_ERROR").then(function (translation) {
        $scope.editor.error = translation;
      });
    });
  };

  // $scope.confirmDeleteRow = function() {
  //   var i, courseId, method;

  //   // rowIndex is one off because of header being in the row
  //   courseId = $scope.tableView.electiveCourses[$scope.editor.rowIndex + 1][2];

  //   tableEntriesService.deleteFact(courseId, 'student_course').then(function (data) {
  //     // reset the form
  //     $scope.cancelEditor();

  //     // update the table to contain the new information
  //     tableEntriesService.updateTableConfig("fact", $scope.tableConfig.tableSelection);
  //   }, function(error) {
  //     $translate("dynamicTable.EDITOR_ERROR").then(function (translation) {
  //       $scope.editor.error = translation;
  //     });
  //   });
  // };


	function getTableEntries() {
		$scope.tableConfig = tableEntriesService.getTableConfiguration();
		setupTableView();
	}

  function updateElectiveCourses() {
    var i, ec, newRankArr = [];

    if (!$scope.tableView.electiveCourses || !$scope.tableView.electiveCourses.length) {
      return;
    }
    if (!$scope.readyForSortable) {
      $scope.readyForSortable = true;
      return;
    }

    // send rank changes to back-end
    //console.log("First elective: " + $scope.tableView.electiveCourses[0][0]);
    ec = $scope.tableView.electiveCourses;
    for (i = 0; i < ec.length; i++) {
      newRankArr.push({
        id: ec[i][2],
        rank: i + 1
      });
    }

    tableEntriesService.editStudentCourse(newRankArr).then(function(data) {
      // don't think I have to do anything
    }, function(error) {
      // @TODO: not sure what to do on a failure
    });
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

    $scope.readyForSortable = false;

    keys = Object.keys($scope.tableConfig.entries[0]);
    for (i = 0; i < $scope.tableConfig.entries.length; i++) {
      // ignore disabled entries
      if ($scope.tableConfig.entries[i].disabled) {
        continue;
      }
      row = [];
      row.push($scope.tableConfig.entries[i].course);
      if ($scope.tableConfig.entries[i].priority === "mandatory") {
        $scope.tableView.requiredCourses.push(row);
      }
      else {
        // rank is @ index 1
        row.push($scope.tableConfig.entries[i].rank);
        // id is @ index 2
        row.push($scope.tableConfig.entries[i].id);
        $scope.tableView.electiveCourses.push(row);
      }
    }

    // sort elective based on rank
    sortElectivesArrayByRank();
  }

  function sortElectivesArrayByRank() {
    var i, j, newRankArr = [], ec, foundRank, lowestRank, curRank;
    ec = $scope.tableView.electiveCourses;
    if (!ec.length) {
      return;
    }

    for (i = 0; i < ec.length; i++) {
      foundRank = false;
      for (j = 0; j < ec.length; j++) {
        // rank is @ index 1
        if (ec[j][1] - 1 === i) {
          newRankArr.push(ec[j]);
          foundRank = true;
        }
      }
      // rank is out of sync, instead sort by lowest to highest rank, then update rank with proper numbers, then send that to the b.e.
      if (!foundRank) {
        curRank = 0;
        newRankArr = [];
        //                                        some extreme limit, and extreme problem in ranking sync has occured
        while (newRankArr.length !== ec.length || curRank > ec.length * 10) {
          for (i = 0; i < ec.length; i++) {
            // rank is @ index 1
            if (ec[i][1] === curRank) {
              newRankArr.push(ec[i]);
            }
          }
          curRank++;
        }

        // update the b.e. with this sync'd rank
        $scope.tableView.electiveCourses = newRankArr;
        // make it ready for sortable, even if it thinks it isn't
        $scope.readyForSortable = true;
        updateElectiveCourses();

        // don't continue with the out-of-sync ranked arr
        return;
      }
    }

    $scope.tableView.electiveCourses = newRankArr;
  }

  $scope.$watch('tableConfig.entries', setupTableView);
  $scope.$watchCollection('tableView.electiveCourses', updateElectiveCourses);

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
