'use strict';

/**
 * Main service for back-end calls for the scheduler module
 */
angular.module('sbAngularApp').factory('schedulerService', ['$q', '$http', 'commonService', function($q, $http, commonService) {
	var GET_SCHEDULES = "api/schedules";
	var scheduleConfig = {
		scheduleList: null,
		selectedSchedule: null
	};

	return {
		
		getScheduleConfig: function() {
			return scheduleConfig;
		},

		updateScheduleList: function() {
			var url = commonService.conformUrl(GET_SCHEDULES);

			$http.get(url).then(function(data) {
				scheduleConfig.scheduleList = data.data;
			}, function(data) {
				// @TODO: how should we deal with this error?
				scheduleConfig.scheduleList = [];
			});
		},

		getSchedule: function(id) {
			var deferred = $q.defer();
			var url;

			if (id === null) {
				deferred.reject("No id given.");
				return deferred.promise;
			}

			url = commonService.conformUrl(GET_SCHEDULES + "/" + id);

			$http.get(url).then(function(data) {
				scheduleConfig.selectedSchedule = data.data;
				deferred.resolve(scheduleConfig.selectedSchedule);
			}, function(data) {
				// @TODO: how should we deal with this error?
				scheduleConfig.selectedSchedule = null;
				deferred.reject(data);
			});
			return deferred.promise;
		},

		deleteSchedule: function(id) {
			var deferred = $q.defer();
			var url;

			if (id === null) {
				deferred.reject("No id given.");
				return deferred.promise;
			}

			url = commonService.conformUrl(GET_SCHEDULES + "/" + id);

			$http.delete(url).then(function(data) {
				scheduleConfig.scheduleList = data.data;
				scheduleConfig.selectedSchedule = null;
				deferred.resolve(data.data);
			}, function(data) {
				// @TODO: how should we deal with this error?
				scheduleConfig.selectedSchedule = null;
				deferred.reject(data);
			});
			return deferred.promise;
		},

		/**
		 * Attemps to generate schedule based on facts and constraints.
		 * @return {array} returns an array representing a fulfilled schedule
		 */
		generateSchedule: function() {
			var deferred = $q.defer();
			var url = commonService.conformUrl(GET_SCHEDULES);

			$http.post(url).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				deferred.reject(data);
			});
			
			return deferred.promise;
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