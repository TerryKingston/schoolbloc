'use strict';

/**
 * Main service for back-end calls for the scheduler module
 */
angular.module('sbAngularApp').factory('schedulerService', ['$q', '$http', 'commonService', function($q, $http, commonService) {
	var GET_SCHEDULES = "api/schedules";
	var GET_SCHEDULE_UPDATES = "api/notifications/unread";
	var scheduleConfig = {
		scheduleList: null,
		selectedSchedule: null,
		checkIfRunningSchedule: 0,
		loadingGenerate: false,
		previousScheduleAmount: 0,
		currentScheduleAmount: 0
	};

	var convertDays = function(container) {
		var daysAbbr = "", j;
		if (!container.days || !container.days.length) {
			return daysAbbr;
		}
		for (j = 0; j < container.days.length; j++) {
			if (container.days[j] === "Monday") {
				daysAbbr = daysAbbr + "M";
			}
			else if (container.days[j] === "Tuesday") {
				daysAbbr = daysAbbr + "T";
			}
			else if (container.days[j] === "Wednesday") {
				daysAbbr = daysAbbr + "W";
			}
			else if (container.days[j] === "Thursday") {
				daysAbbr = daysAbbr + "H";
			}
			else if (container.days[j] === "Friday") {
				daysAbbr = daysAbbr + "F";
			}
			else if (container.days[j] === "Saturday") {
				daysAbbr = daysAbbr + "Sa";
			}
			else if (container.days[j] === "Sunday") {
				daysAbbr = daysAbbr + "Su";
			}
		}
		return daysAbbr;
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

				// update the historical amount of schedule list length
				scheduleConfig.previousScheduleAmount = scheduleConfig.currentScheduleAmount;
				scheduleConfig.currentScheduleAmount = data.data.length;
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
				viewType = "/class";
			}
			else {
				viewType = "/" + viewType;
			}

			// some way to signify that the schedule is loading
			scheduleConfig.selectedSchedule = {id: null};

			url = commonService.conformUrl(GET_SCHEDULES + "/" + id + viewType);

			$http.get(url).then(function(data) {
				var i, j;
				var ss;
				scheduleConfig.selectedSchedule = data.data;
				ss = scheduleConfig.selectedSchedule;
				// update the schedule's time to match standard time
				if (ss.classes) {
					for (i = 0; i < ss.classes.length; i++) {
						ss.classes[i].time = commonService.formatTimeM2S(ss.classes[i].start_time, ss.classes[i].end_time);
						ss.classes[i].time = convertDays(ss.classes[i]) + " " + ss.classes[i].time;
					}
				}
				if (ss.students) {
					for (i = 0; i < ss.students.length; i++) {
						for (j = 0; j < ss.students[i].classes.length; j++) {
							ss.students[i].classes[j].time = commonService.formatTimeM2S(ss.students[i].classes[j].start_time, ss.students[i].classes[j].end_time);
							ss.students[i].classes[j].time = convertDays(ss.students[i].classes[j]) + " " + ss.students[i].classes[j].time;
						}
					}
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
			var url, self = this;

			if (id === null) {
				deferred.reject("No id given.");
				return deferred.promise;
			}

			url = commonService.conformUrl(GET_SCHEDULES + "/" + id + "/class");

			$http.delete(url).then(function(data) {
				//scheduleConfig.scheduleList = data.data;
				self.updateScheduleList();
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