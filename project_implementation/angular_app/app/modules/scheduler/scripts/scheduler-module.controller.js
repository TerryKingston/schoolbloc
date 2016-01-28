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
.directive('sbSchedulerModule', [ function() {
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
		scope: {
			config: "=config",
			schedulerModule: "=info"
		},
		templateUrl: 'modules/scheduler/views/scheduler-module.html',
		link: link
	};
}]);