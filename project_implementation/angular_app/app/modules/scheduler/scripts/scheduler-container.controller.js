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
.controller('SchedulerContainer', ['$scope', 'schedulerService', function($scope, schedulerService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.config = {
		showSchedule: false,
		loadingGenerate: false,
		error: null
	};
	$scope.schedule = [];
	$scope.clusterList = [];

	$scope.scheduleConfig = {};

	$scope.selectSchedule = function(schedule) {
		schedulerService.getSchedule(schedule.id);
	};

	/**
	 * Refreshes the clusterList based on 
	 * @param  {array} schedule schedule to replace.  If none, schedule is removed
	 */
	function refreshSchedule(schedule) {
		var i;

		if (!schedule) {
			$scope.schedule = [];
			$scope.config.showSchedule = false;
			$scope.clusterList = [];
			return;
		}
		$scope.schedule = schedule;
		// only show it if the schedule has entries
		$scope.config.showSchedule = !!$scope.schedule.length;

		// match clusterList size to size of schedule rows
		$scope.clusterList = [];
		if ($scope.schedule.length) {
			for (i = 0; i < $scope.schedule.length; i++) {
				$scope.clusterList.push({});
			}
		}
	}

	/**
	 * Request the generated schedule from the back-end
	 */
	$scope.generateSchedule = function() {
		$scope.config.loadingGenerate = true;
		schedulerService.generateSchedule().then(function(data) {
			$scope.config.loadingGenerate = false;
			$scope.config.error = null;
			refreshSchedule(data);
		}, function(error) {
			$scope.config.loadingGenerate = false;
			$scope.config.error = "Error: could not generate a schedule."
			refreshSchedule();
		});
	};

	/**
	 * Remove the schedule from the front-end view
	 */
	$scope.deleteSchedule = function() {
		// @TODO: actually remove the schedule
		refreshSchedule();
	};

	/**
	 * Export the schedule to a .json file
	 * @todo : allow for other file types in export
	 */
	$scope.exportSchedule = function() {	
		var scheduleId = "", filename, data, blob,
			e, a;	

		if (!$scope.schedule || !$scope.schedule.length) {
			console.log("scheduler-container.exportSchedule: reached an unexpected state");
			refreshSchedule();
			return;
		}

		// generate file name
		if ($scope.schedule.id) {
			scheduleId = $scope.schedule.id;
		}
		filename = "schedule_" + scheduleId + ".json";

		data = JSON.stringify($scope.schedule, null, '\t');

		// create a fake a tag that has a url to the json file, then fake click it
		// CITE: http://bgrins.github.io/devtools-snippets/#console-save
		blob = new Blob([data], {type: 'text/json'});
		e = document.createEvent('MouseEvents');
		a = document.createElement('a');

		a.download = filename;
		a.href = window.URL.createObjectURL(blob);
		a.dataset.downloadurl = ['text/json', a.download, a.href].join(':');
		e.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
		a.dispatchEvent(e);
		// END CITE
	};

	// $scope.debugFlushDB = function() {
	// 	$scope.config.showSchedule = false;
	// 	$scope.schedule = [];
	// 	schedulerService.debugFlushDB().then(function(data) {
			
	// 	}, function(error) {
			
	// 	});
	// };

	/**
	 * Toggles whether or not to show a row cluster (like 21 students)
	 * @param  {number} index        of row
	 * @param  {string} rowAttribute name of attribute that is clustered
	 * @return {[type]}              [description]
	 */
	$scope.toggleCluster = function(index, rowAttribute) {
		if (!$scope.clusterList[index][rowAttribute]) {
			$scope.clusterList[index][rowAttribute] = {
				show: false
			}; 
		}
		$scope.clusterList[index][rowAttribute].show = !$scope.clusterList[index][rowAttribute].show;
	};

	function getScheduleConfig() {
		$scope.scheduleConfig = schedulerService.getScheduleConfig();
	}

	/**** initial setup ****/
	getScheduleConfig();
}])
.directive('sbSchedulerContainer', [ function() {
	/**
	 * For manipulating the DOM
	 * @param  scope   as configured in the controller
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
		templateUrl: 'modules/scheduler/views/scheduler-container.html',
		link: link
	};
}]);