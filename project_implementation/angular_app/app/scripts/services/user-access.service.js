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
					"uid": "0123643",
					"token": "vjkalh382ho"
				},
				{
					"name": "Barbs Bucket",
					"uid": "2565434",
					"token": "fsbjrpsob3"
				},
				{
					"name": "Callen Coy",
					"uid": "2345675",
					"token": "352pogj0bj"
				},
				{
					"name": "Dartanian Decker",
					"uid": "2554466",
					"token": "3pt8gjwjj09"
				},
				{
					"name": "Eli Ellen",
					"uid": "5787653",
					"token": "dvbe324556"
				}
			],
			teacher: [
				{
					"name": "Mrs. Buttersworth",
					"uid": "97654355",
					"token": "gsnserbdrn"
				},
				{
					"name": "Mr. America",
					"uid": "97654775",
					"token": "35btgrd"
				},
				{
					"name": "Dr. Who",
					"uid": "980876578",
					"token": "3htyjt5etf"
				},
				{
					"name": "Dr. Mario",
					"uid": "96543455",
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
		}
	};
}]);
