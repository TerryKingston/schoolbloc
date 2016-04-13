'use strict';

/**
 * Provides data objects for large tables
 */
angular.module('sbAngularApp').factory('userAccessService', ['$q', '$http', 'commonService', function($q, $http, commonService) {
	var SERVER_ROOT = "api/",
		ALL_TOKENS = "api/students?constraints=false",
		TOKENS = SERVER_ROOT + "tokens/",
		STUDENT_TOKENS = TOKENS + "student",
		TEACHER_TOKENS = TOKENS + "teacher",
		MY_STUDENTS = SERVER_ROOT + "my_students";

	var manageStudents = {
		students: null,
		selectedStudent: null
	};

	return {

		getUserTokens: function() {
			var url;
			var deferred = $q.defer();
			//deferred.resolve(userAccess.tokens);
			// conform the url to change the port
			url = commonService.conformUrl(ALL_TOKENS);

			$http.get(url).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				deferred.reject(data.data);
			});
			return deferred.promise;
		},

		getUsersManagedStudents: function() {
			return manageStudents;
		},

		resetManagedStudents: function() {
			manageStudents.students = null;
			manageStudents.selectedStudent = null;
		},

		getUsersStudents: function() {
			var url;
			var deferred = $q.defer();

			// conform the url to change the port
			url = commonService.conformUrl(MY_STUDENTS);

			$http.get(url).then(function(data) {
				manageStudents.students = data.data;
				// set one to be the default, so one is always selected
				if (!manageStudents.selectedStudent && manageStudents.students.length) {
					manageStudents.selectedStudent = manageStudents.students[0];
				}
				deferred.resolve("Students updated");
				//deferred.resolve(data.data);
			}, function(data) {
				manageStudents.students = null;
				deferred.reject(data.data);
			});
			return deferred.promise;
		},

		saveStudent: function(id, user_token) {
			var url, data;
			var deferred = $q.defer();

			// conform the url to change the port
			url = commonService.conformUrl(MY_STUDENTS);

			data = {
				// id: id, don't need
				user_token: user_token
			};

			$http.post(url, data).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				deferred.reject(data.data);
			});
			return deferred.promise;
		}
	};
}]);
