'use strict';

/**
 * Main service for back-end calls for the scheduler module
 */
angular.module('sbAngularApp').factory('schedulerService', ['$q', '$http', 'commonService', function($q, $http, commonService) {
	var GET_SCHEDULES = "api/schedules";
	var GET_SCHEDULE_UPDATES = "api/notifications/unread";
	var scheduleConfig = {
		scheduleList: null,
		selectedSchedule: null
	};

	return {
		
		getScheduleUpdate: function() {
			var deferred = $q.defer();
			var url = commonService.conformUrl(GET_SCHEDULE_UPDATES);

			$http.get(url).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				deferred.reject(data);
			});

			return deferred.promise;
		},

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

		getSchedule: function(id, viewType) {
			var deferred = $q.defer();
			var url;

			if (id === null) {
				deferred.reject("No id given.");
				return deferred.promise;
			}

			if (!viewType) {
				viewType = "";
			}
			else {
				viewType = "/" + viewType;
			}

			// some way to signify that the schedule is loading
			scheduleConfig.selectedSchedule = {id: null};

			url = commonService.conformUrl(GET_SCHEDULES + "/" + id + viewType);

			$http.get(url).then(function(data) {
				var i;
				var ss;
				scheduleConfig.selectedSchedule = data.data;
				ss = scheduleConfig.selectedSchedule;
				// update the schedule's time to match standard time
				for (i = 0; i < ss.classes.length; i++) {
					ss.classes[i].time = commonService.formatTimeM2S(ss.classes[i].start_time, ss.classes[i].end_time);
				}

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