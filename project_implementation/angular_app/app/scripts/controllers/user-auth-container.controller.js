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
			firstName: null,
			lastName: null,
			password: null,
			passwordRe: null,
			person: null,
			token: null,
			email: null,
			errors: {
				usernameError: null,
				firstNameError: null,
				lastNameError: null,
				passwordError: null,
				passwordReError: null,
				personError: null,
				tokenError: null,
				emailError: null
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
	 * Returns true if front-end validates person type, false otherwise
	 */
	$scope.isValidPerson = function() {
		if ($scope.userAuthContainer.form.person && ($scope.userAuthContainer.form.person === 'parent' || $scope.userAuthContainer.form.person === 'teacher' || $scope.userAuthContainer.form.person === 'student')) {
			$scope.userAuthContainer.form.errors.personError = null;
			return true;
		}
		$translate("userAuthContainer.INVALID_PERSON").then(function (translation) {
			$scope.userAuthContainer.form.errors.personError = translation;
		});
		return false;
	};

	/**
	 * Returns true if front-end validates access taken, false otherwise
	 */
	$scope.isValidToken = function() {
		// @TODO: determine exact requirements for token
		if ($scope.userAuthContainer.form.token &&
				$scope.userAuthContainer.form.token.length >= 2) {
			$scope.userAuthContainer.form.errors.tokenError = null;
			return true;
		}
		$translate("userAuthContainer.INVALID_TOKEN").then(function (translation) {
			$scope.userAuthContainer.form.errors.tokenError = translation;
		});
		return false;
	};

	/**
	 * Returns true if front-end validates email, false otherwise
	 */
	$scope.isValidEmail = function() {
		var regex = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/;
    	if (regex.test($scope.userAuthContainer.form.email.toUpperCase())) {
			$scope.userAuthContainer.form.errors.emailError = null;
    		return true;
    	}
		$translate("userAuthContainer.INVALID_EMAIL").then(function (translation) {
			$scope.userAuthContainer.form.errors.emailError = translation;
		});
		return false;
	};

	/**
	 * Returns true if front-end validates school id, false otherwise
	 */
	$scope.isValidId = function() {
		// @TODO: determine exact requirements for id
		if ($scope.userAuthContainer.form.id &&
				$scope.userAuthContainer.form.id.length >= 2) {
			$scope.userAuthContainer.form.errors.idError = null;
			return true;
		}
		$translate("userAuthContainer.INVALID_ID").then(function (translation) {
			$scope.userAuthContainer.form.errors.idError = translation;
		});
		return false;
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
	 * Returns true if front-end validates full name, false otherwise
	 */
	$scope.isValidFirstName = function() {
		// @TODO: determine exact requirements for fullName
		if ($scope.userAuthContainer.form.firstName &&
				$scope.userAuthContainer.form.firstName.length >= 2) {
			$scope.userAuthContainer.form.errors.firstNameError = null;
			return true;
		}
		$translate("userAuthContainer.INVALID_FULLNAME").then(function (translation) {
			$scope.userAuthContainer.form.errors.firstNameError = translation;
		});
		return false;
	};

	/**
	 * Returns true if front-end validates full name, false otherwise
	 */
	$scope.isValidLastName = function() {
		// @TODO: determine exact requirements for fullName
		if ($scope.userAuthContainer.form.lastName &&
				$scope.userAuthContainer.form.lastName.length >= 2) {
			$scope.userAuthContainer.form.errors.lastNameError = null;
			return true;
		}
		$translate("userAuthContainer.INVALID_FULLNAME").then(function (translation) {
			$scope.userAuthContainer.form.errors.lastNameError = translation;
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
		$scope.resetForm();
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
		if (data.message === "Username already exists" || data.message === "Failed to save submission: submission was a duplicate.") {
			$translate("userAuthContainer.DUPLICATE_USERNAME").then(function (translation) {
				$scope.userAuthContainer.form.errors.usernameError = translation;
			});
		}
		// 401 : "Username does not exist."
		else if (data.description === "Invalid credentials") {
			// $translate("userAuthContainer.NO_USERNAME").then(function (translation) {
			// 	$scope.userAuthContainer.form.errors.usernameError = translation;
			// });
			$scope.userAuthContainer.form.errors.usernameError = "Invalid credentials";
			$scope.userAuthContainer.form.errors.passwordError = "Invalid credentials";
		}
		// 401 : "Username password combination was invalid."
		else if (data.message == "Username password combination was invalid.") {
			$translate("userAuthContainer.BAD_PASSWORD").then(function (translation) {
				$scope.userAuthContainer.form.errors.passwordError = translation;
			});
		}
		// 401 : "School id does not exist."
		else if (data.message == "student user token not found") {
			$scope.userAuthContainer.form.errors.tokenError = "Access token was invalid.";
		}
		// 401 : "School id does not exist."
		else if (data.message == "This student already belongs to a user") {
			$scope.userAuthContainer.form.errors.tokenError = "Token belongs to another user.";
		}
		// 401 : "Bad school id - token access pair."
		else if (data.message == "Bad school id - token access pair.") {
			$translate("userAuthContainer.BAD_TOKEN").then(function (translation) {
				$scope.userAuthContainer.form.errors.tokenError = translation;
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
			user,
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
			if (!$scope.isValidPerson()) {
				validForm = false;
			}
			if (!$scope.isValidUsername()) {
				validForm = false;
			}
			if (!$scope.isValidPassword()) {
				validForm = false;
			}
			if (!$scope.isValidPasswordRe()) {
				validForm = false;
			}
			if (form.person === 'student') {
				if (!$scope.isValidToken()) {
					validForm = false;
				}
			}
			else if (form.person === 'parent') {
				if (!$scope.isValidEmail()) {
					validForm = false;
				}
				if (!$scope.isValidFirstName()) {
					validForm = false;
				}
				if (!$scope.isValidLastName()) {
					validForm = false;
				}
			}			
			if (validForm) {
				$scope.userAuthContainer.authenticationError = null;
				user = {
					username: form.username,
					password: form.password,
					role_type: form.person,
					first_name: form.firstName,
					last_name: form.lastName,
					email: form.email,
					user_token: form.token
				}
				userAuthService.registerUser(user).then(function (data) {
					// NOTE: b.e. fixed this
					// // after a register, the b.e. has a hard time giving what we need to login, so just login
					// $scope.userAuthContainer.form.isLoginForm = true;
					// $scope.submitForm();
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
			isLoginForm: $scope.userAuthContainer.form.isLoginForm,
			username: null,
			firstName: null,
			lastName: null,
			password: null,
			passwordRe: null,
			person: null,
			token: null,
			email: null,
			errors: {
				usernameError: null,
				firstNameError: null,
				lastNameError: null,
				passwordError: null,
				passwordReError: null,
				personError: null,
				tokenError: null,
				emailError: null
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