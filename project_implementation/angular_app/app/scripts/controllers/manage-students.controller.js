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
			user_token: null,
			id_error: null,
			user_token_error: null,
			error: null
		},
		addAnother: false
	};

	$scope.manageStudents = {
		students: null,
		selectedStudent: null
	}

	function getUsersStudents() {
		$scope.manageStudents = userAccessService.getUsersManagedStudents();
		userAccessService.getUsersStudents().then(function(data) {
			//$scope.manageStudents.students = data;
		}, function(error) {
			//$scope.manageStudents.students = null;
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
		if (inputType === 'user_token') {
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
		if (!$scope.addStudent.form.user_token) {
			$scope.addStudent.form.user_token_error = "Input is required.";
			return false;
		}
		$scope.addStudent.form.user_token_error = null;
		return true;
	}

	$scope.saveStudent = function(addAnother) {
		// if (!$scope.checkInput('id')) {
		// 	return;
		// }

		if (!$scope.checkInput('user_token')) {
			return;
		}

		$scope.addStudent.addAnother = addAnother;

		userAccessService.saveStudent($scope.addStudent.form.id, $scope.addStudent.form.user_token).then(function(data) {
			if ($scope.addStudent.addAnother) {
				$scope.addStudent.addAnother = false;
			}
			else {
				$scope.addStudent.showAddStudent = false;
			}
			$scope.addStudent.form.error = null;
			resetForm();
			// update the student's table with the newly added student
			getUsersStudents();

		}, function(error) {
			if (error.message === 'Student with requested access token not found') {
				$scope.addStudent.form.error = "Invalid access token.";
			}
			else {
				$scope.addStudent.form.error = error.message;
			}
		});
	}

	function resetForm() {
		$scope.addStudent.form = {
			id: null,
			user_token: null,
			id_error: null,
			user_token_error: null,
			error: null
		};
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