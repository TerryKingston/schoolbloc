'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:SchedulerContainer
 * @description
 *
 * 
 * # SchedulerContainer
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('SchedulerContainer', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];
}])
.directive('sbSchedulerContainer', ['schedulerService', function(schedulerService) {
	/**
	 * For manipulating the DOM
	 * @param  scope   as configured in the controller
	 * @param  element jqLite-wrapped element that matches this directive.
	 * @param  attrs   hash object with key-value pairs of normalized attribute names and their corresponding attribute values.
	 */
	function link(scope, element, attrs) {
		scope.config = {
			showSchedule: false
		}
		scope.schedule = [];

		scope.generateSchedule = function() {
			schedulerService.generateSchedule().then(function(data) {
				scope.schedule = data;
				// only show it if the schedule has entries
				scope.config.showSchedule = !!scope.schedule.length;
			}, function(error) {
				scope.config.showSchedule = false;
				scope.schedule = [];
			});
		};

		scope.deleteSchedule = function() {
			scope.config.showSchedule = false;
			scope.schedule = [];
		};

		scope.debugFlushDB = function() {
			scope.config.showSchedule = false;
			scope.schedule = [];
			schedulerService.debugFlushDB().then(function(data) {
				
			}, function(error) {
				
			});
		}
	}

	/**
	 * restrict: directive is triggered by element (E) name
	 * scope: isolated scope
	 * templateUrl: where we find the template.html
	 * link: for manipulating the DOM
	 */
	return {
		restrict: 'E',
		templateUrl: 'modules/scheduler/views/scheduler-container.html',
		link: link
	};
}]);