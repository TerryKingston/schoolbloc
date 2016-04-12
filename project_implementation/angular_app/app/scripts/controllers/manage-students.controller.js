'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:ManageStudents
 * @description
 *
 * 
 * # ManageStudents
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('ManageStudents', ['$scope', 'userAccessService', function($scope, userAccessService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];
	
	$scope.addStudent = {
		showAddStudent: false,
		form: {
			id: null,
			access_token: null,
			id_error: null,
			access_token_error: null,
			error: null
		},
		addAnother: false
	};

	$scope.manageStudents = {
		students: null,
		selectedStudent: null
	}

	function getUsersStudents() {
		userAccessService.getUsersStudents().then(function(data) {
			$scope.manageStudents.students = data;
		}, function(error) {
			$scope.manageStudents.students = null;
		});
	}

	$scope.selectStudent = function(student) {
		$scope.manageStudents.selectedStudent = student;
	}


	$scope.addStudentToggle = function(show) {
		$scope.addStudent.showAddStudent = show;
	}

	$scope.checkInput = function(inputType) {
		if (inputType === 'id') {
			return checkId();
		}
		if (inputType === 'access_token') {
			return checkAccessToken();
		}
	}

	function checkId() {
		if (!$scope.addStudent.form.id) {
			$scope.addStudent.form.id_error = "Input is required.";
			return false;
		}
		$scope.addStudent.form.id_error = null;
		return true;
	}

	function checkAccessToken() {
		if (!$scope.addStudent.form.access_token) {
			$scope.addStudent.form.access_token_error = "Input is required.";
			return false;
		}
		$scope.addStudent.form.access_token_error = null;
		return true;
	}

	$scope.saveStudent = function(addAnother) {
		if (!checkInput('id') || !checkInput('access_token')) {
			return;
		}

		$scope.addStudent.addAnother = addAnother;

		userAccessService.saveStudent($scope.addStudent.form.id, $scope.addStudent.form.access_token).then(function(data) {
			if ($scope.addStudent.addAnother) {
				$scope.addStudent.addAnother = false;
			}
			else {
				$scope.addStudent.showAddStudent = false;
			}
			$scope.addStudent.form.error = null;

			// update the student's table with the newly added student
			getUsersStudents();

		}, function(error) {
			$scope.addStudent.form.error = error;
		});
	}

	/**** initial setup ****/
	getUsersStudents();
}])
.directive('sbManageStudents', [function() {
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
		templateUrl: 'views/manage-students.html',
		link: link
	};
}]);