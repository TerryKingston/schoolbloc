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
.controller('SchedulerContainer', ['$scope', 'schedulerService', '$timeout', 'userAuthService', function($scope, schedulerService, $timeout, userAuthService) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.config = {
		showSchedule: false,
		error: null
	};
	$scope.schedule = [];
	$scope.requestScheduleList = false;
	$scope.clusterList = [];
	$scope.showExportOptions = false;
	$scope.scheduleConfig = {};
	$scope.scheduleOptions = {
		values: [{value: "class", "text": "Class"}, {value: "student", "text": "Student"}],
		selectedValue: 'class'
	};

	$scope.scheduleLog = {
		data: [
			// {
			// 	"created_at": "2015-16-14 13:45.34567",
			// 	"description": "Schedule has started, but a bunny jumped into the main system and is crashing all the servers.  Oh no! He just ate the internet!"
			// },
			// {
			// 	"created_at": "2015-16-14 13:45.34567",
			// 	"description": "Schedule has started, but a bunny jumped into the main system and is crashing all the servers.  Oh no! He just ate the internet!"
			// },
			// {
			// 	"created_at": "2015-16-14 13:45.34567",
			// 	"description": "Schedule has started, but a bunny jumped into the main system and is crashing all the servers.  Oh no! He just ate the internet!"
			// },
			// {
			// 	"created_at": "2015-16-14 13:45.34567",
			// 	"description": "Schedule has started, but a bunny jumped into the main system and is crashing all the servers.  Oh no! He just ate the internet!"
			// }
		]
	};

	$scope.selectSchedule = function(id) {
		schedulerService.getSchedule(id, $scope.scheduleOptions.selectedValue);
	};

	$scope.updateScheduleView = function() {
		schedulerService.getSchedule($scope.scheduleConfig.selectedSchedule.id, $scope.scheduleOptions.selectedValue);
	}

	/**
	 * Request the generated schedule from the back-end
	 */
	$scope.generateSchedule = function() {
		$scope.scheduleConfig.loadingGenerate = true;

		getGenerationUpdates();

		schedulerService.generateSchedule().then(function(data) {
			//$scope.scheduleConfig.loadingGenerate = false;
			$scope.config.error = null;
		}, function(error) {
			$scope.scheduleConfig.loadingGenerate = false;
			$scope.config.error = "Error: could not generate a schedule."
		});
	};

	function startGenerationUpdates() {
		// only set if we've never been to this page before
		if ($scope.scheduleConfig.checkIfRunningSchedule === 0) {
			$scope.scheduleConfig.checkIfRunningSchedule = 1;
		}
		if ($scope.scheduleConfig.checkIfRunningSchedule !== 2) {
			$scope.scheduleConfig.loadingGenerate = true;
		}
		getGenerationUpdates();
	}


	function getGenerationUpdates() {
		var time = 5000;
		if ($scope.scheduleConfig.checkIfRunningSchedule !== 2) {
			time = 100;
		}

		// stop requesting updates once the new schedule is generated
		if (!$scope.scheduleConfig.loadingGenerate) {
			return;
		}

		// every 5 seconds get new updates
		$timeout(function() {
			schedulerService.getScheduleUpdate().then(function(data) {
				var i;
				if (data) {
					for (i = 0; i < data.length; i++) {
						$scope.scheduleLog.data.push(data[i]);
						// schedule done, allow for another to be generated
						if (data[i].description === "Solution found, saving schedule now") {
							$scope.scheduleConfig.loadingGenerate = false;
							// schedule may be finished, check for new schedule
							$scope.requestScheduleList = true;
							updateScheduleList();
						}
					}
				}
				// if we return back with no data, and this is the first time visiting this page,
				// the odds of a schedule running is low so we can allow for generating of a schedule
				if (data && !data.length && $scope.scheduleConfig.checkIfRunningSchedule !== 2) {
					$scope.scheduleConfig.checkIfRunningSchedule = 2;
					$scope.scheduleConfig.loadingGenerate = false;
					return;
				}
				else if (data && data.length && $scope.scheduleConfig.checkIfRunningSchedule !== 2) {
					$scope.scheduleConfig.checkIfRunningSchedule = 2;
				}

				// check if role is still valid (i.e. did admin sign out and log in as a student?)
				if (userAuthService.getUserRole() === 'admin') {
					getGenerationUpdates();
				}
			}, function(error) {
				//$scope.scheduleConfig.loadingGenerate = false;
				$scope.config.error = "Error: could not get updates."
			});
		}, time);
	}

	function updateScheduleList() {

		schedulerService.updateScheduleList();

		$timeout(function() {
			if ($scope.scheduleConfig.previousScheduleAmount !== $scope.scheduleConfig.currentScheduleAmount) {
				$scope.requestScheduleList = false;
			}

			if ($scope.requestScheduleList) {
				// check if role is still valid (i.e. did admin sign out and log in as a student?)
				if (userAuthService.getUserRole() === 'admin') {
					updateScheduleList();
				}
			}
		}, 5000);
	}

	/**
	 * Remove the schedule from the front-end view
	 */
	$scope.deleteSchedule = function() {
		schedulerService.deleteSchedule($scope.scheduleConfig.selectedSchedule.id).then(function(data) {
			$scope.config.error = null;
		}, function(error) {
			$scope.config.error = "Error: could not delete the schedule.";
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

		if ($scope.scheduleOptions.selectedValue === 'class') {
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
		}
		else if ($scope.scheduleOptions.selectedValue === 'student') {
			
			s = $scope.scheduleConfig.selectedSchedule.students;
			for (i = 0; i < s.length; i++) {
				for (j = 0; j < s[i].classes.length; j++) {
					data = data + "\"" + s[i].classes[j].classroom + "\",";
					data = data + "\"" + s[i].classes[j].course + "\",";
					data = data + "\"" + s[i].classes[j].time + "\",";
					data = data + "\"" + s[i].classes[j].teacher + "\",";
					data = data + "\"" + s[i].first_name + " " + s[i].last_name + "\"\n";
				}
			}
		}
		else {
			console.error("Incorrect table type: cannot export.");
			return;
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
	startGenerationUpdates();

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