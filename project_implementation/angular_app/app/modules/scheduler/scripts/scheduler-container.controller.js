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
.controller('SchedulerContainer', ['$scope', 'schedulerService', '$timeout', function($scope, schedulerService, $timeout) {
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
	$scope.showExportOptions = false;
	$scope.scheduleConfig = {};
	$scope.scheduleOptions = {
		values: [{value: "class", "text": "Class"}, {value: "student", "text": "Student"}],
		selectedValue: 'class'
	};


	$scope.selectSchedule = function(id) {
		schedulerService.getSchedule(id);
	};

	$scope.updateScheduleView = function() {
		console.log($scope.scheduleOptions.selectedValue)
		schedulerService.getSchedule($scope.scheduleConfig.selectedSchedule.id, $scope.scheduleOptions.selectedValue);
	}

	/**
	 * Request the generated schedule from the back-end
	 */
	$scope.generateSchedule = function() {
		$scope.config.loadingGenerate = true;

		getGenerationUpdates();

		schedulerService.generateSchedule().then(function(data) {
			$scope.config.loadingGenerate = false;
			$scope.config.error = null;
		}, function(error) {
			$scope.config.loadingGenerate = false;
			$scope.config.error = "Error: could not generate a schedule."
		});
	};


	function getGenerationUpdates() {
		// stop requesting updates once the new schedule is generated
		if (!$scope.config.loadingGenerate) {
			return;
		}

		// every 5 seconds get new updates
		$timeout(function() {
			schedulerService.getScheduleUpdate().then(function(data) {
				debugger;
				getGenerationUpdates();
			}, function(error) {
				debugger;
				//$scope.config.loadingGenerate = false;
				$scope.config.error = "Error: could not get updates."
			});
		}, 5000);
	}

	/**
	 * Remove the schedule from the front-end view
	 */
	$scope.deleteSchedule = function() {
		schedulerService.deleteSchedule().then(function(data) {
			$scope.config.error = null;
		}, function(error) {
			$scope.config.error = "Error: could not generate a schedule.";
		});		
	};

	$scope.showExportScheduleOptions = function() {
		$scope.showExportOptions = !$scope.showExportOptions;
	}

	/**
	 * Export the schedule to a .json file
	 * @todo : allow for other file types in export
	 */
	$scope.exportAsJSON = function() {	
		var filename, scheduleId = "", data, blob,
			e, a;

		// generate file name
		if ($scope.scheduleConfig.selectedSchedule.id) {
			scheduleId = $scope.scheduleConfig.selectedSchedule.id;
		}
		filename = "schedule_" + scheduleId + ".json";

		data = JSON.stringify($scope.scheduleConfig.selectedSchedule, null, '\t');

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

	/**
	 * Export the schedule to a .json file
	 * @todo : allow for other file types in export
	 */
	$scope.exportAsCSV = function() {	
		var filename, scheduleId = "", data, blob,
			e, a, i, j, s;

		// generate file name
		if ($scope.scheduleConfig.selectedSchedule.id) {
			scheduleId = $scope.scheduleConfig.selectedSchedule.id;
		}
		filename = "schedule_" + scheduleId + ".csv";

		// convert to csv file format
		data = "\"classroom\",\"course\",\"time\",\"teacher\",\"student\"\n";
		s = $scope.scheduleConfig.selectedSchedule.classes;
		for (i = 0; i < s.length; i++) {
			for (j = 0; j < s[i].students.length; j++) {
				data = data + "\"" + s[i].classroom.value + "\",";
				data = data + "\"" + s[i].course.value + "\",";
				data = data + "\"" + s[i].time + "\",";
				data = data + "\"" + s[i].teacher.value + "\",";
				data = data + "\"" + s[i].students[j].value + "\"\n";
			}
		}

		// create a fake a tag that has a url to the json file, then fake click it
		// CITE: http://bgrins.github.io/devtools-snippets/#console-save
		blob = new Blob([data], {type: 'text/json'});
		e = document.createEvent('MouseEvents');
		a = document.createElement('a');

		a.download = filename;
		a.href = window.URL.createObjectURL(blob);
		a.dataset.downloadurl = ['text/csv', a.download, a.href].join(':');
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
	 * @param  {number} row        with rowAttribute
	 * @param  {string} rowAttribute name of attribute that is clustered
	 */
	$scope.toggleCluster = function(row, rowAttribute) {
		if (!row["show_" + rowAttribute]) {
			row["show_" + rowAttribute] = true;
		}
		else {
			row["show_" + rowAttribute] = !row["show_" + rowAttribute];
		}
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