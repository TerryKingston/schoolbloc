'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:SchedulerModule
 * @description
 *
 * 
 * # SchedulerModule
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('SchedulerModule', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];

	$scope.schedulerModule = {
		viewHeaderConfig: {
			title: "schedulerModule.TITLE",
			subTitle: "schedulerModule.SUBTITLE",
			link: {
				text: "schedulerModule.SUBTITLE_ACTION",
				action: null
			}
		}
	};
}])
.directive('sbSchedulerModule', ['schedulerService', 'globalService', function(schedulerService, globalService) {
	/**
	 * For manipulating the DOM
	 * @param  scope   as configured in the controller
	 * @param  element jqLite-wrapped element that matches this directive.
	 * @param  attrs   hash object with key-value pairs of normalized attribute names and their corresponding attribute values.
	 */
	function link(scope, element, attrs) {
		scope.userAccess = {
			role: null
		};

		scope.$watch('config.subView', viewChange);

		function viewChange() {
			if (scope.config.subView === null && scope.config.view === 'scheduler') {
				schedulerService.updateScheduleList();
			}
		}

		function getUserAccess() {
			scope.userAccess = globalService.getUserAccess();
		}

		// function roleChange() {
		// 	getModuleTranslations();
		// }

		// scope.$watch('userAccess.role', roleChange);

		/**** initial setup ****/
		getUserAccess();
	}

	/**
	 * restrict: directive is triggered by element (E) name
	 * scope: isolated scope
	 * templateUrl: where we find the template.html
	 * link: for manipulating the DOM
	 */
	return {
		restrict: 'E',
		scope: {
			config: "=config",
			schedulerModule: "=info"
		},
		templateUrl: 'modules/scheduler/views/scheduler-module.html',
		link: link
	};
}]);