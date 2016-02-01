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
.controller('AddFact', ['$scope', 'tableEntriesService', function($scope, tableEntriesService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.addFactConfig = {
		showAddFact: false,
		addFactText: "!!Add Course",
		factTypeConfig: null,
		factEntry: null
	};

	$scope.tableConfig = {

	};

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
			else if (factInput.type === "dropdown") {
				checkDropdown(factInput);
			}
			else if (factInput.type === "constraint") {
				checkConstraint(factInput);
			}
			else {
				console.error("addFactController.checkInput: unexpected state - invalid factInput type");
			}
		}
	};

	function checkMin(factInput) {
		if (!factInput.value.min && !factInput.value.min !== 0 && factInput.required) {
			factInput.error = "!!Input is required.";
		}
		if (factInput.value.min < 0) {
			factInput.error = "!!Cannot have a negative value.";
		} 
		else if (factInput.value.min > factInput.value.max && factInput.value.max) {
			factInput.error = "!!Cannot have the min > max."
		}
		else {
			factInput.error = null;
		}
	}

	function checkMax(factInput) {
		if (!factInput.value.max && !factInput.value.max !== 0 && factInput.required) {
			factInput.error = "!!Input is required.";
		}
		if (factInput.value.max < 1) {
			factInput.error = "!!Must be a positive value.";
		} 
		else if (factInput.value.min > factInput.value.max && factInput.value.min) {
			factInput.error = "!!Cannot have the min > max."
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
			factInput.error = "!!Input is required.";
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

		factInput.error = "!!Must be item from list.";
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
		
		factInput.error = "!!Must be item from list.";
		for (i = 0; i < factInput.facts.length; i++) {
			if (factInput.facts[i] === factInput.value) {
				factInput.error = null;
			}
		}
	}

	$scope.saveFact = function (addAnotherFact) {
		// check all input fields for errors

		//// set the factEntry keys according to the config object
		// 
		// no config object given
		if (!$scope.addFactConfig.factTypeConfig || !$scope.addFactConfig.factTypeConfig.length) {
			$scope.addFactConfig.factEntry = null;
			return;
		}
		$scope.addFactConfig.factEntry = {};
		ftc = $scope.addFactConfig.factTypeConfig;
		fe = $scope.addFactConfig.factEntry;
		for (i = 0; i < ftc.length; i++) {
			fe[ftc[i].key] = null;
		}


		if (!addAnotherFact) {
			$scope.addFactConfig.showAddFact = false;
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

		// get the config object
		$scope.addFactConfig.factTypeConfig = tableEntriesService.getFactTypeConfig($scope.tableConfig.tableSelection);

		// make sure to grab the array of constraints for this fact type
		tableEntriesService.updateFactTypeFacts($scope.tableConfig.tableSelection);
	}

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