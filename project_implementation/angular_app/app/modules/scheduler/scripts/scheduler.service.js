'use strict';

/**
 * Main service for back-end calls for the scheduler module
 */
angular.module('sbAngularApp').factory('schedulerService', ['$q', '$http', 'commonService', function($q, $http, commonService) {
	var GET_SCHEDULES = "api/schedules";

	return {
		
		/**
		 * Attemps to generate schedule based on facts and constraints.
		 * @return {array} returns an array representing a fulfilled schedule
		 */
		generateSchedule: function() {
			var deferred = $q.defer();
			var url = commonService.conformUrl(GET_SCHEDULES);

			$http.get(url).then(function(data) {
				deferred.resolve(data.data[0].scheduled_classes);
				// 	// TODO: for now, return the most recently generated schedule
				// if (data.data && data.data.length) {
				// 	deferred.resolve(data.data[data.data.length - 1]);
				// 	return;
				// }
				// deferred.reject("Incorrect format");
			}, function(data) {
				deferred.reject(data.data);
			});
			
			return deferred.promise;

			// NOTE test method:
			// var data = [ 
			// 	{ 
			// 		"teacher": {
			// 			"id": 1, 
			// 			"first_name": "Severus", 
			// 			"last_name": "Snape"
			// 		}, 
			// 		"classroom": {
			// 			"id": 1, 
			// 			"room_number": "101", 
			// 			"max_student_count": 15
			// 		}, 
			// 		"start_time": "0800", 
			// 		"end_time": "1000", 
			// 		"course": {
			// 			"id": 1, 
			// 			"name": "Remedial Potions", 
			// 			"duration": 120, 
			// 			"max_student_count": 30, 
			// 			"min_student_count": 10
			// 		},
			// 		"students": [ 
			// 			{
			// 				"id": 1, 
			// 				"first_name": "Harry", 
			// 				"last_name": "Potter"
			// 			}, 
			// 			{
			// 				"id": 2, 
			// 				"first_name": "Ron", 
			// 				"last_name": "Weasly"
			// 			}
			// 		] 
			// 	},
			// 	{ 
			// 		"teacher": {
			// 			"id": 1, 
			// 			"first_name": "Albus", 
			// 			"last_name": "Dumbledore"
			// 		}, 
			// 		"classroom": {
			// 			"id": 1, 
			// 			"room_number": "L103", 
			// 			"max_student_count": 50
			// 		}, 
			// 		"start_time": "1400", 
			// 		"end_time": "1600",
			// 		"course": {
			// 			"id": 1, 
			// 			"name": "Defense Against Dark Arts", 
			// 			"duration": 120, 
			// 			"max_student_count": 120, 
			// 			"min_student_count": 30
			// 		},
			// 		"students": [ 
			// 			{
			// 				"id": 1, 
			// 				"first_name": "Harry", 
			// 				"last_name": "Potter"
			// 			}, 
			// 			{
			// 				"id": 3, 
			// 				"first_name": "Amos", 
			// 				"last_name": "Diggory"
			// 			},
			// 			{
			// 				"id": 4, 
			// 				"first_name": "Fleur", 
			// 				"last_name": "Delacour"
			// 			}
			// 		]
			// 	}
			// ];
			
			// deferred.resolve(data);
			
			// return deferred.promise;
		},

		/**
		 * DEBUG METHOD
		 * flushes the DB for the next demo
		 */
		debugFlushDB: function() {
			var deferred = $q.defer();
			var data, url;

			deferred.resolve(data);

			url = commonService.conformUrl("test");
			
			return deferred.promise;
		}
	};
}]);