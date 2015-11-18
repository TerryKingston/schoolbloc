'use strict';

/**
 * @ngdoc function
 * @name sbAngularApp.controller:ImportExportContainer
 * @description
 *
 * 
 * # ImportExportContainer
 * Controller of the sbAngularApp
 */
angular.module('sbAngularApp')
.controller('ImportExportContainer', ['$scope', function($scope) {
	this.components = [
		'HTML5 Boilerplate',
		'AngularJS',
		'Karma'
	];
	$scope.importExportContainer = {
		viewHeaderConfig: {
			title: "importExport.TITLE",
			subTitle: "importExport.SUBTITLE",
			link: null
		}
	};

}])
.directive('sbImportExportContainer', [function() {
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
	 * scope: isolated scope to $scope.importExportContainer only
	 * templateUrl: where we find the template.html
	 * link: for manipulating the DOM
	 */
	return {
		restrict: 'E',
		templateUrl: 'views/import-export-container.html',
		link: link
	};
}]);