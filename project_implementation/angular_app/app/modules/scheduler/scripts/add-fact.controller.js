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

	$scope.translations = {};

	$scope.toggleAddFact = function (show) {
		$scope.addFactConfig.showAddFact = show;
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
			factInput.error = $scope.translations.ERROR_MUST_NUMBER;
			return;
		}
		if (number < 0) {
			factInput.error = $scope.translations.ERROR_POS_INT;
		}

		factInput.error = null;
	}

	function checkUniqueText(factInput) {
		if (checkRequired(factInput)) {
			return;
		}
		factInput.error = null;
		// @TODO: you've already received a list of all facts of this type 
		// (it's used in the dynamic table directive)
		// just check against that list
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
		if (!factInput.required && !factInput.value) {
			factInput.error = null;
			return true;
		}
		if (factInput.required && !factInput.value) {
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
		for (i = 0; i < factInput.facts.length; i++) {
			if (factInput.facts[i] === factInput.value) {
				factInput.error = null;
			}
		}
	}

	$scope.saveFact = function (addAnotherFact) {
		var i,
			duplicateMap,
			ftc = $scope.addFactConfig.factTypeConfig,
			fe;

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
			fe[ftc[i].key] = null;
		}

		// @TODO: reset the form
		$scope.resetForm();

		// if save instead of save & add another
		if (!addAnotherFact) {
			$scope.addFactConfig.showAddFact = false;
		}
	};

	$scope.resetForm = function (factInput, index) {
		var i,
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

		getTranslations();

		// get the config object
		$scope.addFactConfig.factTypeConfig = tableEntriesService.getFactTypeConfig($scope.tableConfig.tableSelection);

		// make sure to grab the array of constraints for this fact type
		tableEntriesService.updateFactTypeFacts($scope.tableConfig.tableSelection);
	}

	function getTranslations() {
		$translate("schedulerModule.ADD_FACT").then(function (translation) {
			$scope.addFactConfig.addFactText = commonService.format(translation, [$scope.tableConfig.tableSelection]);
		});

		$translate("schedulerModule.ADDING_FACT").then(function (translation) {
			$scope.addFactConfig.addingFactText = commonService.format(translation, [$scope.tableConfig.tableSelection]);
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
	};

	/**** initial setup ****/
	getTableConfig(); 
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