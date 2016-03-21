'use strict';

/**
 * Provides data objects for large tables
 */
angular.module('sbAngularApp').factory('userAccessService', ['$q', '$http', 'commonService', function($q, $http, commonService) {
	var SERVER_ROOT = "api/",
		TOKENS = SERVER_ROOT + "tokens/",
		STUDENT_TOKENS = TOKENS + "student",
		TEACHER_TOKENS = TOKENS + "teacher";

	var userAccess = {
		tokens: {
			student: [
				{
					"name": "Alfred Alloy",
					"user_id": "0123643",
					"token": "vjkalh382ho"
				},
				{
					"name": "Barbs Bucket",
					"user_id": "2565434",
					"token": "fsbjrpsob3"
				},
				{
					"name": "Callen Coy",
					"user_id": "2345675",
					"token": "352pogj0bj"
				},
				{
					"name": "Dartanian Decker",
					"user_id": "2554466",
					"token": "3pt8gjwjj09"
				},
				{
					"name": "Eli Ellen",
					"user_id": "5787653",
					"token": "dvbe324556"
				}
			],
			teacher: [
				{
					"name": "Mrs. Buttersworth",
					"user_id": "97654355",
					"token": "gsnserbdrn"
				},
				{
					"name": "Mr. America",
					"user_id": "97654775",
					"token": "35btgrd"
				},
				{
					"name": "Dr. Who",
					"user_id": "980876578",
					"token": "3htyjt5etf"
				},
				{
					"name": "Dr. Mario",
					"user_id": "96543455",
					"token": "2365ygfhf"
				}
			]
		}
	}

	return {

		getUserTokens: function() {
			var deferred = $q.defer();
			deferred.resolve(userAccess.tokens);
			return deferred.promise;
		},

		getStudentTokens: function() {
			var deferred = $q.defer();
			deferred.resolve(userAccess.tokens.student);
			return deferred.promise;
		},

		getTeacherTokens: function() {
			var deferred = $q.defer();
			deferred.resolve(userAccess.tokens.teacher);
			return deferred.promise;
		}
	};
}]);
