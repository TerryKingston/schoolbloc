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
.controller('ImportExportContainer', ['$scope', 'FileUploader', function($scope, FileUploader) {
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

	$scope.fileUploader = new FileUploader({
		queueLimit: 1
	});

	

	// the upload URL depends on the selected table, so we'll set that 
	// when a selection is made. The url also gets added to the 'File' object
	// when one is selected, so we have to change it also if we want the 
	// change to reflect in a previously selected file
	$scope.setUploadUrl = function(){
		var url = '';
		switch($scope.uploadTableName){
			case 'teachers':
				url = '.../teachers/...';
				break;
			case 'students':
				url = '.../students/...';
				break;
			case 'courses':
				url = '.../courses/...';
				break;
			case 'classrooms':
				url = '.../classrooms/...';
				break;
			default:
				
		}
		$scope.fileUploader.url = url;
		if ($scope.fileUploader.queue.length > 0){
			$scope.fileUploader.queue[0].url = url			
		}
	}
	$scope.uploadTableName = 'students'
	$scope.setUploadUrl()

	$scope.uploadSelectedFile = function(){
		if ($scope.fileUploader.queue.length < 1){
			return
		}
		$scope.fileUploader.uploadItem(0)
	}

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