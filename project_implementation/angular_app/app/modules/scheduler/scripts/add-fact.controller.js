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
.controller('AddFact', ['$scope', '$translate', 'tableEntriesService', 'commonService', function($scope, $translate, tableEntriesService, commonService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.addFactConfig = {
		showAddFact: false,
		addFactText: null,
		addingFactText: null,
		factTypeConfig: null,
		factEntry: null
	};

	$scope.tableConfig = {

	};

	$scope.previousTableSelection = null;

	$scope.translations = {};

	$scope.toggleAddFact = function (show) {
		$scope.addFactConfig.showAddFact = show;
		// remove error if cancel
		if (!show) {
			$scope.addFactConfig.addFactErrorText = null;
		}
	};

	$scope.checkInput = function (factInput, specifyType) {
		if (specifyType && specifyType === 'min') {
			checkMin(factInput);
		}
		else if (specifyType && specifyType == 'max') {
			checkMax(factInput);
		}
		else {
			if (factInput.type === "text") {
				checkText(factInput);
			}
			else if (factInput.type === "number") {
				checkNumber(factInput);
			}
			else if (factInput.type === "uniqueText") {
				checkUniqueText(factInput);
			}
			else if (factInput.type === "dropdown") {
				checkDropdown(factInput);
			}
			else if (factInput.type === "constraint") {
				checkConstraint(factInput);
			}
			else if (factInput.type === "startEnd") {
				checkStartEnd(factInput);
			}
			else if (factInput.type === "date") {
				checkDate(factInput);
			}
			else {
				console.error("addFactController.checkInput: unexpected state - invalid factInput type: " + factInput.type);
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

	$scope.saveFact = function (addAnotherFact) {
		var i,
			duplicateMap,
			ftc = $scope.addFactConfig.factTypeConfig,
			fe, priority;

		// no config object given
		if (!$scope.addFactConfig.factTypeConfig || !$scope.addFactConfig.factTypeConfig.length) {
			$scope.addFactConfig.factEntry = null;
			return;
		}
		// remove any empty added input fields
		for (i = 0; i < ftc.length; i++) {
			if (ftc[i].addedValue && (ftc[i].value === null || ftc[i].value === "")) {
				$scope.removeInput(ftc[i], i);
				// reduce i becaues we've reduced the array
				i--;
			}
		}

		// remove duplicate added input fields
		duplicateMap = {};
		for (i = 0; i < ftc.length; i++) {
			if (ftc[i].addedValue) {
				// if we already have that value for this input set, remove this one
				if (duplicateMap[ftc[i].value]) {
					$scope.removeInput(ftc[i], i);
					// reduce i becaues we've reduced the array
					i--;
				}
				else {
					duplicateMap[ftc[i].value] = true;
				}
			}
			// reset the duplicate checker for the next not-added input field
			else {
				duplicateMap = {};
				duplicateMap[ftc[i].value] = true;
			}
		}

		// check all input fields for errors
		for (i = 0; i < ftc.length; i++) {
			// special case since .value is an object
			if (ftc[i].type === "minMax") {
				$scope.checkInput(ftc[i], "min");
				$scope.checkInput(ftc[i], "min");
			}
			else {
				$scope.checkInput(ftc[i]);
			}
		}
		// if errors, don't continue
		for (i = 0; i < ftc.length; i++) {
			if (ftc[i].error) {
				return;
			}
		}

		//// @TODO: set the factEntry keys according to the config object
		// 
		$scope.addFactConfig.factEntry = {};
		fe = $scope.addFactConfig.factEntry;
		for (i = 0; i < ftc.length; i++) {
			if (ftc[i].type === 'constraint') {
				if (!fe[ftc[i].key] && (ftc[i].value !== null && ftc[i].value !== "")) {
					fe[ftc[i].key] = [];
				}
				if (fe[ftc[i].key] && (ftc[i].value !== null && ftc[i].value !== "")) {
					if (ftc[i].elective) {
						priority = "low";
					}
					else {
						priority = "mandatory";
					}
					fe[ftc[i].key].push({
						"id": ftc[i].facts.map[ftc[i].value],
						"priority": priority, // for now, it's always mandatory when we add
						"active": true // for now, it's always true when we add
					});
				}
			}
			else if (ftc[i].type === 'minMax') {
				fe['min_' + ftc[i].key] = ftc[i].value.min;
				fe['max_' + ftc[i].key] = ftc[i].value.max;
			}
			else if (ftc[i].type === 'startEnd' && (ftc[i].value !== null && ftc[i].value !== "")) {
				fe[ftc[i].key] = commonService.formatSingleTimeS2M(ftc[i].value);
			}
			else {
				fe[ftc[i].key] = ftc[i].value;
			}
		}
		tableEntriesService.addFact(fe, $scope.tableConfig.tableSelection).then(function (data) {
			// reset the form
			$scope.resetForm();

			$scope.addFactConfig.addFactErrorText = null;
			// if save instead of save & add another
			if (!addAnotherFact) {
				$scope.addFactConfig.showAddFact = false;
			}
			// update the table to contain the new information
			tableEntriesService.updateTableConfig("fact", $scope.tableConfig.tableSelection);
		}, function(error) {
			$translate("schedulerModule.ADD_FACT_ERROR").then(function (translation) {
				$scope.addFactConfig.addFactErrorText = translation;
			});
		});
	};

	$scope.resetForm = function (factInput, index) {
		var i,
			weekDayFacts,
			ftc = $scope.addFactConfig.factTypeConfig;

		// remove all added input fields
		for (i = 0; i < ftc.length; i++) {
			if (ftc[i].addedValue) {
				$scope.removeInput(ftc[i], i);
				// reduce i becaues we've reduced the array
				i--;
			}
		}

		// set all values to null
		for (i = 0; i < ftc.length; i++) {
			// special case for object value types
			if (ftc[i].type === "minMax") {
				ftc[i].value = {
					min: null,
					max: null
				}
			}
			else {
				ftc[i].value = null;
			}
			ftc[i].error = null;
		}

		// special case for teacher day values
		if ($scope.factSelection === 'teacher') {
			weekDayFacts = ftc[5].facts;
			// remove the day that is set to null, and add the all weekdays as checked
			ftc.splice(5, 1, {
				key: "day",
				value: "Monday",
				error: null,
				required: true,
				type: "constraint",
				multipleValues: true,
				facts: weekDayFacts
			},
			{
				addedValue: true,
				key: "day",
				value: "Tuesday",
				error: null,
				required: true,
				type: "constraint",
				multipleValues: true,
				facts: weekDayFacts
			},
			{
				addedValue: true,
				key: "day",
				value: "Wednesday",
				error: null,
				required: true,
				type: "constraint",
				multipleValues: true,
				facts: weekDayFacts
			},
			{
				addedValue: true,
				key: "day",
				value: "Thursday",
				error: null,
				required: true,
				type: "constraint",
				multipleValues: true,
				facts: weekDayFacts
			},
			{
				addedValue: true,
				key: "day",
				value: "Friday",
				error: null,
				required: true,
				type: "constraint",
				multipleValues: true,
				facts: weekDayFacts
			});
		}
	};

	$scope.addInput = function (factInput, index) {
		var newFactInput = {}, 
			keys, i;

		keys = Object.keys(factInput);
		for (i = 0; i < keys.length; i++) {
			// if value is an object, we don't want to copy over by reference
			if (keys[i] === "value" && factInput.type === "minMax") {
				newFactInput.value = {
					min: null,
					max: null
				}
			}
			// otherwise, we want value to be empty
			else if (keys[i] === "value") {
				newFactInput.value = null;
			}
			else {
				newFactInput[keys[i]] = factInput[keys[i]];
			}
		}

		// mark it as an added input 
		newFactInput.addedValue = true;

		if (newFactInput.canBeElective) {
			newFactInput.elective = false;
		}

		$scope.addFactConfig.factTypeConfig.splice(index + 1, 0, newFactInput);
	};

	$scope.removeInput = function (factInput, index) {
		$scope.addFactConfig.factTypeConfig.splice(index, 1);
	};

	$scope.$watch('tableConfig.tableSelection', updateFactType);

	function getTableConfig() {
		$scope.tableConfig = tableEntriesService.getTableConfiguration();
		updateFactType();
	}

	function updateFactType() {
		var i, ftc, fe;

		if ($scope.tableConfig.tableType !== "fact" || !$scope.tableConfig.tableSelection) {
			$scope.addFactConfig.factTypeConfig = null;
			$scope.addFactConfig.factEntry = null;
			return;
		}

		getDynamicTranslations();

		// make sure we don't call the BE more than we need to
		if ($scope.tableConfig.tableSelection === $scope.previousTableSelection) {
			return;
		}
		$scope.previousTableSelection = $scope.tableConfig.tableSelection;
		
		// get the config object
		$scope.addFactConfig.factTypeConfig = tableEntriesService.getFactTypeConfig($scope.tableConfig.tableSelection);
		// make sure to grab the array of constraints for this fact type
		tableEntriesService.updateFactTypeFacts($scope.tableConfig.tableSelection);

		$scope.resetForm();
	}

	function getDynamicTranslations() {
		$translate("schedulerModule.ADD_FACT").then(function (translation) {
			$scope.addFactConfig.addFactText = commonService.format(translation, [$scope.translations[$scope.tableConfig.tableSelection]]);
		});

		$translate("schedulerModule.ADDING_FACT").then(function (translation) {
			$scope.addFactConfig.addingFactText = commonService.format(translation, [$scope.translations[$scope.tableConfig.tableSelection]]);
		});
	}

	function getTranslations() {
		$translate("schedulerModule.ELECTIVE_COURSE").then(function (translation) {
			$scope.translations.student_course = translation;
		});

		$translate("schedulerModule.DAY").then(function (translation) {
			$scope.translations.day = translation;
		});

		$translate("schedulerModule.DAYS").then(function (translation) {
			$scope.translations.days = translation;
		});

		$translate("schedulerModule.SUBJECT").then(function (translation) {
			$scope.translations.subject = translation;
		});

		$translate("schedulerModule.TEACHER").then(function (translation) {
			$scope.translations.teacher = translation;
		});

		$translate("schedulerModule.COURSE").then(function (translation) {
			$scope.translations.course = translation;
		});

		$translate("schedulerModule.STUDENT").then(function (translation) {
			$scope.translations.student = translation;
		});

		$translate("schedulerModule.CLASSROOM").then(function (translation) {
			$scope.translations.classroom = translation;
		});

		$translate("schedulerModule.STUDENT_GROUP").then(function (translation) {
			$scope.translations.student_group = translation;
		});

		$translate("schedulerModule.NAME").then(function (translation) {
			$scope.translations.name = translation;
		});

		$translate("schedulerModule.FIRST_NAME").then(function (translation) {
			$scope.translations.first_name = translation;
		});

		$translate("schedulerModule.LAST_NAME").then(function (translation) {
			$scope.translations.last_name = translation;
		});

		$translate("schedulerModule.ROOM_NUMBER").then(function (translation) {
			$scope.translations.room_number = translation;
		});

		$translate("schedulerModule.STUDENT_COUNT").then(function (translation) {
			$scope.translations.student_count = translation;
		});

		$translate("schedulerModule.MAX_STUDENT_COUNT").then(function (translation) {
			$scope.translations.max_student_count = translation;
		});

		$translate("schedulerModule.MIN_STUDENT_COUNT").then(function (translation) {
			$scope.translations.min_student_count = translation;
		});

		$translate("schedulerModule.AVAIL_START_TIME").then(function (translation) {
			$scope.translations.avail_start_time = translation;
		});

		$translate("schedulerModule.AVAIL_END_TIME").then(function (translation) {
			$scope.translations.avail_end_time = translation;
		});

		$translate("schedulerModule.START_TIME").then(function (translation) {
			$scope.translations.start_time = translation;
		});

		$translate("schedulerModule.END_TIME").then(function (translation) {
			$scope.translations.end_time = translation;
		});

		$translate("schedulerModule.TIMEBLOCK").then(function (translation) {
			$scope.translations.timeblock = translation;
		});

		$translate("schedulerModule.DURATION").then(function (translation) {
			$scope.translations.duration = translation;
		});

		$translate("schedulerModule.USER_ID").then(function (translation) {
			$scope.translations.uid = translation;
		});

		$translate("schedulerModule.ERROR_LIST_ITEM").then(function (translation) {
			$scope.translations.ERROR_LIST_ITEM = translation;
		});

		$translate("schedulerModule.ERROR_MUST_NUMBER").then(function (translation) {
			$scope.translations.ERROR_MUST_NUMBER = translation;
		});

		$translate("schedulerModule.ERROR_POS_INT").then(function (translation) {
			$scope.translations.ERROR_POS_INT = translation;
		});

		$translate("schedulerModule.ERROR_DATE").then(function (translation) {
			$scope.translations.ERROR_DATE = translation;
		});

		$translate("schedulerModule.ERROR_TIME").then(function (translation) {
			$scope.translations.ERROR_TIME = translation;
		});

		$translate("schedulerModule.ERROR_NEG_VALUE").then(function (translation) {
			$scope.translations.ERROR_NEG_VALUE = translation;
		});

		$translate("schedulerModule.ERROR_MIN_MAX").then(function (translation) {
			$scope.translations.ERROR_MIN_MAX = translation;
		});

		$translate("schedulerModule.ERROR_REQUIRED").then(function (translation) {
			$scope.translations.ERROR_REQUIRED = translation;
		});

		$translate("schedulerModule.ERROR_UNIQUE").then(function (translation) {
			$scope.translations.ERROR_UNIQUE = translation;
		});
	};

	/**** initial setup ****/
	getTableConfig(); 
	getTranslations();
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