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
.controller('ImportExportContainer', ['$scope', 'FileUploader', 'commonService', function($scope, FileUploader, commonService) {
	var IMPORT_ROOT = "api/import/",
		IMPORT_TEACHER_URL = IMPORT_ROOT + 'teacher',
		IMPORT_STUDENT_URL = IMPORT_ROOT + 'student',
		IMPORT_COURSE_URL = IMPORT_ROOT + 'course',
		IMPORT_CLASSROOM_URL = IMPORT_ROOT + 'classroom';

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
		queueLimit: 10,
		formData: {
			table_name: 'students' // default to students. can be changed in form
		}	
	});

	// the upload URL depends on the selected table, so we'll set that 
	// when a selection is made. 
	$scope.setUploadUrl = function(){
		var url = '';
		switch ($scope.fileUploader.formData.table_name) {
			case 'teachers':
				url = commonService.conformUrl(IMPORT_TEACHER_URL);
				break;
			case 'students':
				url = commonService.conformUrl(IMPORT_STUDENT_URL);
				break;
			case 'courses':
				url = commonService.conformUrl(IMPORT_COURSE_URL);
				break;
			case 'classrooms':
				url = commonService.conformUrl(IMPORT_CLASSROOM_URL);
				break;
			default:
				break;
		}
		$scope.fileUploader.url = url;
	}
	$scope.setUploadUrl();

	$scope.uploadSelectedFile = function() {
		if ($scope.fileUploader.queue.length < 1) {
			return;
		}
		$scope.fileUploader.uploadItem(0);
	}

	$scope.deleteTableEntry = function(index, ignore) {
		if (ignore) {
			return;
		}
		$scope.fileUploader.queue.splice(index, 1);
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