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
  $scope.factTypeConfig = null;
	$scope.tableView = null;
  $scope.tableText = {
    closedArrayEntry: null,
    openedArrayEntry: null
  };

  $scope.selectedRow = {
    index: null,
    delete: false
  };

  $scope.tableOptions = {
    show: false,
    floatTableHeader: false
  };

  $scope.headerObj = {
    type: "header"
  };

  $scope.translations = {};

  $scope.editor = {
    "type": "editor",
    "subType": null,
    "rowIndex": null, // where it sits in row
    "key": null, // course, classroom, student_group
    "factType": null, // uniqueText, number, constraint, etc
    "selectedEntry": null, // reference to selected entry to keep track of edit
    "value": null,
    "originalValue": null,
    "constraintId": null, // constraints are saved as ids in the back-end, we need to keep track of them
    "priority": "mandatory",
    "error": null,
    "facts": {
      "values": []
    },
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
      rows: [],
      rowIds: []
    };

    resetEditor();

    // no entries
    if (!$scope.tableConfig.entries || !$scope.tableConfig.entries.length) {
      return;
    }

    // get the newest factTypeConfig object
    $scope.factTypeConfig = tableEntriesService.getFactTypeConfig($scope.tableConfig.tableSelection);

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
        else {
          entry = convertObjectToString(entry);
        }
        row.push(entry);
      }
      $scope.tableView.rows.push(row);
    }

    // deal with storing ids
    for (i = 0; i < $scope.tableConfig.entries.length; i++) {
      $scope.tableView.rowIds.push($scope.tableConfig.entries[i].id);
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

  $scope.editConstraint = function(rowIndex, entryIndex, entry) {    
    placeEditor('edit-constraint', rowIndex, entryIndex, entry);
  };

  $scope.addConstraint = function(rowIndex, entryIndex) {
    placeEditor('add-constraint', rowIndex, entryIndex, null);
  };

  $scope.addProperty = function(rowIndex, entryIndex) {
    placeEditor('add-property', rowIndex, entryIndex, null);
  };

  $scope.editProperty = function(rowIndex, entryIndex, entry) {
    placeEditor('edit-property', rowIndex, entryIndex, entry);
  };

  $scope.disableConstraint = function(rowIndex, entryIndex, entry) {
    var i, apiCompliant, factId, method, key;

    // determine if row index is affected by an already in place editor, and reconfigure if needed
    if ($scope.editor.rowIndex !== null && rowIndex > $scope.editor.rowIndex) {
      rowIndex--;
    }

    // convert to the API compliant version for sending to b.e.
    apiCompliant = {};

    method = "edit";
    key = $scope.tableView.headers[entryIndex].value;

    apiCompliant[key] = [
      {
        "method": method,
        "id": entry.id,
        "active": !entry.active
      }
    ];
    
    // rowIndex is one off because of header being in the row
    factId = $scope.tableView.rowIds[rowIndex - 1];

    tableEntriesService.editFact(apiCompliant, factId, $scope.tableConfig.tableSelection).then(function (data) {
      // switch the disable btn
      entry.active = !entry.active;
    }, function(error) {
      // do not switch the disable btn
    });
  };

  $scope.deleteConstraint = function(rowIndex, entryIndex, entry) {
    placeEditor('delete-constraint', rowIndex, entryIndex, entry);
  };

  $scope.deleteProperty = function(rowIndex, entryIndex, entry) {
    placeEditor('delete-property', rowIndex, entryIndex, entry);
  };

  $scope.disableRow = function(rowIndex) {
    // @TODO: there is no API to do this
  };

  $scope.deleteRow = function(rowIndex) {
    // determine if row index is affected by an already in place editor, and reconfigure if needed
    if ($scope.editor.rowIndex !== null && rowIndex > $scope.editor.rowIndex) {
      rowIndex--;
    }

    resetEditor();

    // because now the rowIndex is the editor
    $scope.selectedRow.index = rowIndex + 1;
    $scope.selectedRow.delete = true;

    $scope.editor.subType = 'delete-row';

    // add editor into rows
    $scope.editor.rowIndex = rowIndex;
    $scope.tableView.rows.splice(rowIndex, 0, $scope.editor);
    
    // need timeout for it to be placed in html template
    // scroll to the editor box
    $timeout(function() {
        $location.hash('constraintEditor');
        $anchorScroll();
    }, 100);
  };

  /**
   * Delete a single constraint binding
   */
  $scope.confirmDeleteEntry = function() {
    // $scope.editor ...
    var i, apiCompliant, factId, method;

    // convert to the API compliant version for sending to b.e.
    apiCompliant = {};
    if ($scope.editor.factType === 'constraint') {
      method = "delete";

      apiCompliant[$scope.editor.key] = [
        {
          "method": method,
          "id": $scope.editor.facts.map[$scope.editor.value]
        }
      ];
    }
    else if ($scope.editor.factType === 'minMax') {
      // only delete one or the other
      if ($scope.editor.value.selectedMin) {
        apiCompliant['min_' + $scope.editor.key] = null;
      }
      else {
        apiCompliant['max_' + $scope.editor.key] = null;
      }
    }
    else {
      apiCompliant[$scope.editor.key] = null;
    }

    // rowIndex is one off because of header being in the row
    factId = $scope.tableView.rowIds[$scope.editor.rowIndex - 1];

    tableEntriesService.editFact(apiCompliant, factId, $scope.tableConfig.tableSelection).then(function (data) {
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

  $scope.confirmDeleteRow = function() {
    var i, factId, method;


    // rowIndex is one off because of header being in the row
    factId = $scope.tableView.rowIds[$scope.editor.rowIndex - 1];

    tableEntriesService.deleteFact(factId, $scope.tableConfig.tableSelection).then(function (data) {
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

  $scope.confirmEditEntry = function() {
    var i, apiCompliant, factId, method;

    // check input field for errors
    // special case since .value is an object
    if ($scope.editor.factType === "minMax") {
      $scope.checkInput($scope.editor, "min");
      $scope.checkInput($scope.editor, "min");
    }
    else {
      $scope.checkInput($scope.editor);
    }
    // if error, don't continue
    if ($scope.editor.error) {
      return;
    }

    // convert to the API compliant version for sending to b.e.
    apiCompliant = {};
    if ($scope.editor.factType === 'constraint') {
      $scope.editor.subType === 'edit-constraint' ? method = "edit" : method = "add";

      // we need to replace the old constraint with a new one
      if (method === 'edit' && $scope.editor.value !== $scope.editor.originalValue) {
        apiCompliant[$scope.editor.key] = [
          {
            "method": "add",
            "id": $scope.editor.facts.map[$scope.editor.value],
            "active": true,
            "priority": $scope.editor.priority
          },
          {
            "method": "delete",
            "id": $scope.editor.facts.map[$scope.editor.originalValue]
          } 
        ];
      }
      else {
        apiCompliant[$scope.editor.key] = [
          {
            "method": method,
            "id": $scope.editor.facts.map[$scope.editor.value],
            "priority": $scope.editor.priority
          }
        ];

        // default disabled to be false for added, for edited, we ignore it to preserve the old state
        if (method === 'add') {
          apiCompliant[$scope.editor.key][0].active = true;
        }
      }
    }
    else if ($scope.editor.factType === 'minMax') {
      apiCompliant['min_' + $scope.editor.key] = $scope.editor.value.min;
      apiCompliant['max_' + $scope.editor.key] = $scope.editor.value.max;
    }
    else if ($scope.editor.factType === 'startEnd') {
      apiCompliant[$scope.editor.key] = commonService.formatSingleTimeS2M($scope.editor.value);
    }
    else {
      apiCompliant[$scope.editor.key] = $scope.editor.value;
    }

    // rowIndex is one off because of header being in the row
    factId = $scope.tableView.rowIds[$scope.editor.rowIndex - 1];

    tableEntriesService.editFact(apiCompliant, factId, $scope.tableConfig.tableSelection).then(function (data) {
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

  $scope.cancelEditor = function() {
    resetEditor();
  };

  $scope.checkInput = function (factInput, specifyType) {
    if (specifyType && specifyType === 'min') {
      checkMin(factInput);
    }
    else if (specifyType && specifyType == 'max') {
      checkMax(factInput);
    }
    else {
      if (factInput.factType === "text") {
        checkText(factInput);
      }
      else if (factInput.factType === "number") {
        checkNumber(factInput);
      }
      else if (factInput.factType === "uniqueText") {
        checkUniqueText(factInput);
      }
      else if (factInput.factType === "dropdown") {
        checkDropdown(factInput);
      }
      else if (factInput.factType === "constraint") {
        checkConstraint(factInput);
      }
      else if (factInput.factType === "startEnd") {
        checkStartEnd(factInput);
      }
      else if (factInput.factType === "date") {
        checkDate(factInput);
      }
      else {
        console.error("dynamicTable.checkInput: unexpected state - invalid factInput type: " + factInput.factType);
      }
    }
  };

  function checkNumber(factInput) {
    if (checkRequired(factInput)) {
      return;
    }
    var number = factInput.value;
    number = parseInt(number);
    if (isNaN(number)) {
      factInput.error = $scope.translations.ERROR_POS_INT;
      return;
    }
    if (number <= 0) {
      factInput.error = $scope.translations.ERROR_POS_INT;
      return;
    }

    factInput.error = null;
  }

  function checkUniqueText(factInput) {
    var i;
    if (checkRequired(factInput)) {
      return;
    }
    factInput.error = null;
    // @TODO: you've already received a list of all facts of this type 
    // (it's used in the dynamic table directive)
    // just check against that list
    for (i = 0; i < $scope.tableConfig.entries.length; i++) {
      // "" + becuase it could be an int
      if (factInput.value === ("" + $scope.tableConfig.entries[i][factInput.key])) {
        factInput.error = $scope.translations.ERROR_UNIQUE;
        break;
      }
    }
  }

  function checkDate(factInput) {
    var convertedInput = factInput.value;
    if (checkRequired(factInput)) {
      return;
    }
    convertedInput = commonService.formatDateInput(convertedInput);
    if (convertedInput === "ERROR") {
      factInput.error = $scope.translations.ERROR_DATE;
      return;
    }
    factInput.error = null;
    factInput.value = convertedInput;
  }

  function checkStartEnd(factInput) {
    var convertedInput = factInput.value;
    if (checkRequired(factInput)) {
      return;
    }
    convertedInput = commonService.formatTimeInput2S(convertedInput);
    if (convertedInput === "ERROR") {
      factInput.error = $scope.translations.ERROR_TIME;
      return;
    }
    factInput.error = null;
    factInput.value = convertedInput;
  }

  function checkMin(factInput) {
    if (!factInput.value.min && !factInput.value.min !== 0 && factInput.required) {
      factInput.error = $scope.translations.ERROR_REQUIRED;
      return;
    }
    if (factInput.value.min < 0) {
      factInput.error = $scope.translations.ERROR_NEG_VALUE;
    } 
    else if (factInput.value.min > factInput.value.max && factInput.value.max) {
      factInput.error = $scope.translations.ERROR_MIN_MAX;
    }
    else {
      factInput.error = null;
    }
  }

  function checkMax(factInput) {
    if (!factInput.value.max && !factInput.value.max !== 0 && factInput.required) {
      factInput.error = $scope.translations.ERROR_REQUIRED;
      return;
    }
    if (factInput.value.max < 1) {
      factInput.error = $scope.translations.ERROR_POS_INT;
    } 
    else if (factInput.value.min > factInput.value.max && factInput.value.min) {
      factInput.error = $scope.translations.ERROR_MIN_MAX;
    }
    else {
      factInput.error = null;
    }
  }

  function checkRequired(factInput) {
    // if it's empty but not required, we don't want to do further checks
    if (!factInput.required && (factInput.value === null || factInput.value === "")) {
      factInput.error = null;
      return true;
    }
    if (factInput.required && (factInput.value === null || factInput.value === "")) {
      factInput.error = $scope.translations.ERROR_REQUIRED;
      return true;
    }
    return false;
  }

  function checkText(factInput) {
    if (checkRequired(factInput)) {
      return;
    }
    factInput.error = null;
  }

  function checkDropdown(factInput) {
    var i;

    if (checkRequired(factInput)) {
      return;
    }

    factInput.error = $scope.translations.ERROR_LIST_ITEM;
    for (i = 0; i < factInput.possibleAnswers.length; i++) {
      if (factInput.possibleAnswers[i] === factInput.value) {
        factInput.error = null;
      }
    }
  }

  function checkConstraint(factInput) {
    var i;

    if (checkRequired(factInput)) {
      return;
    }
    
    factInput.error = $scope.translations.ERROR_LIST_ITEM;
    for (i = 0; i < factInput.facts.values.length; i++) {
      if (factInput.facts.values[i] === factInput.value) {
        factInput.error = null;
        return;
      }
    }
  }

  function placeEditor(rowSubType, rowIndex, entryIndex, entry, preventReposition) {
    var i, valueIdString;
    // NOTE: do not modify editor here, resetEditor() happens below

    // determine if row index is affected by an already in place editor, and reconfigure if needed
    if ($scope.editor.rowIndex !== null && rowIndex > $scope.editor.rowIndex) {
      rowIndex--;
    }

    // remove any previous editor
    resetEditor();

    // because now the rowIndex is the editor
    $scope.selectedRow.index = rowIndex + 1;
    $scope.selectedRow.delete = false;

    //// edit editor object to have needed properties
    $scope.editor.subType = rowSubType;
    $scope.editor.key = $scope.tableView.headers[entryIndex].value;
    if ($scope.editor.key === 'min_student_count') {
      $scope.editor.value = {
        min: null,
        max: null,
        selectedMin: true
      };
      $scope.editor.key = 'student_count';
    }
    else if ($scope.editor.key === 'max_student_count') {
      $scope.editor.value = {
        min: null,
        max: null,
        selectedMin: false
      };
      $scope.editor.key = 'student_count';
    }

    // get factTypes based on config file
    for (i = 0; i < $scope.factTypeConfig.length; i++) {
      if ($scope.factTypeConfig[i].key === $scope.editor.key) {
        $scope.editor.factType = $scope.factTypeConfig[i].type;
        
        // get constraint lists
        if ($scope.editor.factType === 'constraint') {
          $scope.editor.facts = $scope.factTypeConfig[i].facts;
        }
        break;
      }
    }

    // set value/id as needed
    // @TODO: for the special case of min-max, we have to go get the other property (either min or max),
    // so that we can ensure that min <= max
    if ($scope.editor.key === 'student_count') {
      // would be null at this point since the factTypeConfig would be student_count instead of max/min_student_count
      $scope.editor.value.min = $scope.tableConfig.entries[rowIndex - 1]['min_student_count'];
      $scope.editor.value.max = $scope.tableConfig.entries[rowIndex - 1]['max_student_count'];
    }
    else if ($scope.editor.factType === 'constraint' && entry) {
      if (entry.id) {
        $scope.editor.constraintId = entry.id; 
      }
      if (entry.priority) {
        $scope.editor.priority = entry.priority;
      }
      if (entry.value) {
        $scope.editor.value = entry.value;
      }
    }
    else {
      $scope.editor.value = entry;
    }

    // alter value to match an id to value pairing, if need be
    if ($scope.editor.factType === 'constraint' && $scope.editor.value) {
      valueIdString = tableEntriesService.getValueWithIdString($scope.editor.value, $scope.editor.constraintId);
      // check if value has been altered
      if ($scope.editor.facts.map[valueIdString]) {
        $scope.editor.value = valueIdString;
      }
    }

    // preserve originalValue if replacing it (i.e. editing a constraint's name)
    $scope.editor.originalValue = $scope.editor.value;

    // deal with showing the selected entry
    if ($scope.editor.factType === 'constraint') {
      if (entry) {
        entry.isSelected = true;
      }
      $scope.editor.selectedEntry = entry;
    }

    // add editor into rows
    $scope.editor.rowIndex = rowIndex;
    $scope.tableView.rows.splice(rowIndex, 0, $scope.editor);
    
    // scroll to the editor box
    // need digest for the constraintEditor id to be placed in html template at the right place
    if (!preventReposition) {
      $timeout(function() {
        $location.hash('constraintEditor');
        $anchorScroll();
      }, 100);
    }
  }

  function resetEditor() {
    // deal with removing the selected entry
    if ($scope.editor.selectedEntry) {
      $scope.editor.selectedEntry.isSelected = false;
    }

    if ($scope.editor.rowIndex !== null) {
      $scope.tableView.rows.splice($scope.editor.rowIndex, 1);
    }

    $scope.selectedRow.index = null;
    $scope.selectedRow.delete = false;

    $scope.editor.error = null;
    $scope.editor.selectedEntry = null;
    $scope.editor.rowIndex = null;
    $scope.editor.subType = null;
    $scope.editor.key = null;
    $scope.editor.factType = null;
    $scope.editor.value = null;
    $scope.editor.originalValue = null;
    $scope.editor.constraintId = null;
    $scope.editor.priority = "mandatory";
    $scope.editor.facts = {
      values: []
    };
    $scope.editor.showFilters = true;
    $scope.editor.filters = [];
  }

  $scope.toggleAllEntries = function(index, show) {
    var i;
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

    $translate("dynamicTable.ERROR_LIST_ITEM").then(function (translation) {
      $scope.translations.ERROR_LIST_ITEM = translation;
    });

    $translate("dynamicTable.ERROR_MUST_NUMBER").then(function (translation) {
      $scope.translations.ERROR_MUST_NUMBER = translation;
    });

    $translate("dynamicTable.ERROR_POS_INT").then(function (translation) {
      $scope.translations.ERROR_POS_INT = translation;
    });

    $translate("dynamicTable.ERROR_DATE").then(function (translation) {
      $scope.translations.ERROR_DATE = translation;
    });

    $translate("dynamicTable.ERROR_TIME").then(function (translation) {
      $scope.translations.ERROR_TIME = translation;
    });

    $translate("dynamicTable.ERROR_NEG_VALUE").then(function (translation) {
      $scope.translations.ERROR_NEG_VALUE = translation;
    });

    $translate("dynamicTable.ERROR_MIN_MAX").then(function (translation) {
      $scope.translations.ERROR_MIN_MAX = translation;
    });

    $translate("dynamicTable.ERROR_REQUIRED").then(function (translation) {
      $scope.translations.ERROR_REQUIRED = translation;
    });

    $translate("schedulerModule.ERROR_UNIQUE").then(function (translation) {
      $scope.translations.ERROR_UNIQUE = translation;
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
