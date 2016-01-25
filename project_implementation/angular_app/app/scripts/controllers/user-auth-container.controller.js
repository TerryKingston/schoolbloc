'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:UserAuthContainer
 * @description
 *
 * Page container for login and registration page
 *
 * # UserAuthContainer
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('UserAuthContainer', ['$scope', '$translate', 'userAuthService', function($scope, $translate, userAuthService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];
	$scope.userAuthContainer = {
		form: {
			isLoginForm: true,
			username: null,
			fullName: null,
			password: null,
			passwordRe: null,
			errors: {
				usernameError: null,
				fullNameError: null,
				passwordError: null,
				passwordReError: null
			},
			text: {
				title: null,
				switchLink: null,
				submitButton: null
			}
		},
		authenticationError: null
	};


	/**
	 * Returns true if front-end validates username, false otherwise
	 */
	$scope.isValidUsername = function() {
		// @TODO: determine exact requirements for username
		if ($scope.userAuthContainer.form.username &&
				$scope.userAuthContainer.form.username.length >= 2) {
			$scope.userAuthContainer.form.errors.usernameError = null;
			return true;
		}
		$translate("userAuthContainer.INVALID_USERNAME").then(function (translation) {
			$scope.userAuthContainer.form.errors.usernameError = translation;
		});
		return false;
	};

	/**
	 * Returns true if front-end validates password, false otherwise
	 */
	$scope.isValidPassword = function() {
		// @TODO: determine exact requirements for password
		if ($scope.userAuthContainer.form.password &&
				$scope.userAuthContainer.form.password.length >= 5) {
			$scope.userAuthContainer.form.errors.passwordError = null;
			return true;
		}
		$translate("userAuthContainer.INVALID_PASSWORD").then(function (translation) {
			$scope.userAuthContainer.form.errors.passwordError = translation;
		});
		return false;
	};

	/**
	 * Returns true if front-end validates full name, false otherwise
	 */
	$scope.isValidFullName = function() {
		// @TODO: determine exact requirements for fullName
		if ($scope.userAuthContainer.form.fullName &&
				$scope.userAuthContainer.form.fullName.length >= 2) {
			$scope.userAuthContainer.form.errors.fullNameError = null;
			return true;
		}
		$translate("userAuthContainer.INVALID_FULLNAME").then(function (translation) {
			$scope.userAuthContainer.form.errors.fullNameError = translation;
		});
		return false;
	};

	/**
	 * Returns true if front-end validates retyping of password, false otherwise
	 */
	$scope.isValidPasswordRe = function() {
		if ($scope.userAuthContainer.form.password === $scope.userAuthContainer.form.passwordRe) {
			$scope.userAuthContainer.form.errors.passwordReError = null;
			return true;
		}
		$translate("userAuthContainer.INVALID_PASSWORD_RE").then(function (translation) {
			$scope.userAuthContainer.form.errors.passwordReError = translation;
		});
		return false;
	};

	/**
	 * Switches view between login and registration
	 */
	$scope.switchForm = function() {
		$scope.userAuthContainer.form.isLoginForm = !$scope.userAuthContainer.form.isLoginForm;
		$scope.getFormTypeText();
	};

	/** Get the translated text based on it being a login or register form */
	$scope.getFormTypeText = function() {
		if ($scope.userAuthContainer.form.isLoginForm) {
			$translate("userAuthContainer.LOGIN").then(function (translation) {
				$scope.userAuthContainer.form.text.title = translation;
				$scope.userAuthContainer.form.text.submitButton = translation;
			});

			$translate("userAuthContainer.REGISTER_LINK").then(function (translation) {
				$scope.userAuthContainer.form.text.switchLink = translation;
			});
		}
		else {
			$translate("userAuthContainer.REGISTER").then(function (translation) {
				$scope.userAuthContainer.form.text.title = translation;
				$scope.userAuthContainer.form.text.submitButton = translation;
			});

			$translate("userAuthContainer.LOGIN_LINK").then(function (translation) {
				$scope.userAuthContainer.form.text.switchLink = translation;
			});
		}
	};

	/**
	 * Show authentication error in view.
	 */
	$scope.getAuthenticationError = function() {
		if ($scope.userAuthContainer.errorCode === "FORBIDDEN") {
			$translate("userAuthContainer.FORBIDDEN").then(function (translation) {
				$scope.userAuthContainer.authenticationError = translation;
			});
		}
	}

	/**
	 * Checks why error was thrown from server.  If so, it gets translated text for error.
	 * @param  {string} data status string from server response
	 */
	$scope.checkForErrors = function(data) {
		// 401 : "Username already exists."
		if (data === "Username already exists." || data === "Failed to save submission: submission was a duplicate.") {
			$translate("userAuthContainer.DUPLICATE_USERNAME").then(function (translation) {
				$scope.userAuthContainer.form.errors.usernameError = translation;
			});
		}
		// 401 : "Username does not exist."
		else if (data === "Username does not exist.") {
			$translate("userAuthContainer.NO_USERNAME").then(function (translation) {
				$scope.userAuthContainer.form.errors.usernameError = translation;
			});
		}
		// 401 : "Username password combination was invalid."
		else if (data == "Username password combination was invalid.") {
			$translate("userAuthContainer.BAD_PASSWORD").then(function (translation) {
				$scope.userAuthContainer.form.errors.passwordError = translation;
			});
		}
		// probably a 500 error
		else {
			$translate("userAuthContainer.SERVER_ERROR").then(function (translation) {
				$scope.userAuthContainer.authenticationError = translation;
			});
		}
	};

	/**
	 * Checks the form one last time for validity, and submits the form data.
	 */
	$scope.submitForm = function() {
		var validForm = true,
			form = $scope.userAuthContainer.form; // shortcut


		// login
		if (form.isLoginForm) {
			// perform checks
			// since we want to check each field, we have a variable keep track of whether or not it was valid
			if (!$scope.isValidUsername()) {
				validForm = false;
			} 
			if (!$scope.isValidPassword()) {
				validForm = false;
			}
			if (validForm) {
				// reset any authentication error, so the notification area is ready for the response
				$scope.userAuthContainer.authenticationError = null;
				
				userAuthService.loginUser(form.username, form.password).then(function (data) {
					// at the end of a successful submit, we want to reset the form in case the user logs out
					$scope.resetForm();
					$scope.$emit("checkUserAuth");
				}, function(data) {
					// display errors
					$scope.checkForErrors(data);
				});
			}
		}
		// register
		else {
			// perform checks
			// since we want to check each field, we have a variable keep track of whether or not it was valid
			if (!$scope.isValidUsername()) {
				validForm = false;
			}
			if (!$scope.isValidFullName()) {
				validForm = false;
			}
			if (!$scope.isValidPassword()) {
				validForm = false;
			}
			if (!$scope.isValidPasswordRe()) {
				validForm = false;
			}
			if (validForm) {
				$scope.userAuthContainer.authenticationError = null;

				userAuthService.registerUser(form.username, form.password, form.fullName).then(function (data) {
					// at the end of a successful submit, we want to reset the form in case the user logs out
					$scope.resetForm();
					$scope.$emit("checkUserAuth");
				}, function(data) {
					// display errors
					$scope.checkForErrors(data);
				});
			}
		}
	};

	$scope.resetForm = function() {
		$scope.userAuthContainer.form = {
			isLoginForm: true,
			username: null,
			fullName: null,
			password: null,
			passwordRe: null,
			errors: {
				usernameError: null,
				fullNameError: null,
				passwordError: null,
				passwordReError: null
			},
			text: {
				title: null,
				switchLink: null,
				submitButton: null
			}
		};
		$scope.getFormTypeText();
		$scope.getAuthenticationError();
	};

	/**************
	 * Inital setup
	 *************/
	$scope.resetForm();

}])
.directive('sbUserAuthContainer', [ function() {
	
	/**
	 * For manipulating the DOM
	 * @param  scope   
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
		templateUrl: 'views/user-auth-container.html',
		link: link
	};
}]);