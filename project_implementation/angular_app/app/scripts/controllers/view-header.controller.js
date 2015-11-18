'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:ViewHeader
 * @description
 *
 * USE:
 * <sb-view-header config="configObject"></sb-view-header>
 *
 * configObject = {
 *   title: <Locale CONSTANT>
 *   subTitle: <Locale CONSTANT>
 *   link: { // optional
 *     text: <Locale CONSTANT>
 *     action: <@TODO: need to determine how we want to do this...>
 *   }
 * }
 * 
 * # ViewHeader
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('ViewHeader', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];


}])
.directive('sbViewHeader', ['$translate', function($translate) {
	/**
	 * For manipulating the DOM
	 * @param  scope   as configured in the controller
	 * @param  element jqLite-wrapped element that matches this directive.
	 * @param  attrs   hash object with key-value pairs of normalized attribute names and their corresponding attribute values.
	 */
	function link(scope, element, attrs) {
		scope.viewHeader = {
			textValues: {
				title: "",
				subTitle: "",
				subTitleAction: ""
			}
		};
		
		function translateText() {
			if (!scope.config) {
				return;
			}
			if (scope.config.title) {
				$translate(scope.config.title).then(function (translation) {
					scope.viewHeader.textValues.title = translation;
				});
			}
			if (scope.config.subTitle) {
				$translate(scope.config.subTitle).then(function (translation) {
					scope.viewHeader.textValues.subTitle = translation;
				});
			}
			if (scope.config.link && scope.config.link.text) {
				$translate(scope.config.link.text).then(function (translation) {
					scope.viewHeader.textValues.subTitleAction = translation;
				});
			}
		}

		/**
		 * Perform the link action.
		 * @TODO: what is the link action?  
		 *   Probably a global variable that any actionable view is listening for.
		 *   You could have the main-container listen for view changes.
		 *   It then updates the innerview, and sends the actionable item to the new view.
		 *   So that the new view can peform the action.
		 */
		scope.linkToHeaderAction = function() {
			if (!scope.config || !scope.config.link || !scope.config.link.action) {
				return;
			}
			// @TODO:
		};

		/**** INITIAL SETUP ****/
		translateText();
	}

	/**
	 * restrict: directive is triggered by element (E) name
	 * scope: isolated scope to $scope.viewHeader only
	 * templateUrl: where we find the template.html
	 * link: for manipulating the DOM
	 */
	return {
		restrict: 'E',
		scope: {
			config: '=config'
		},
		templateUrl: 'views/view-header.html',
		link: link
	};
}]);