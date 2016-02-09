'use strict';

/**
 * Provides data objects for large tables
 */
angular.module('sbAngularApp').factory('tableEntriesService', ['$q', '$http', 'commonService', function($q, $http, commonService) {
	var SERVER_ROOT = "api/",
		CLASSROOM_URL = SERVER_ROOT + "classrooms",
		COURSE_URL = SERVER_ROOT + "courses",
		STUDENT_URL = SERVER_ROOT + "students",
		STUDENT_GROUP_URL = SERVER_ROOT + "student_groups",
		SUBJECT_URL = SERVER_ROOT + "subjects",
		TEACHER_URL = SERVER_ROOT + "teachers",
		TIME_URL = SERVER_ROOT + "times";
		

	// never reinstantiate: reference will be lost with bound controllers
	var tableConfig = {
		tableType: null,
		tableSelection: null,
	};

	var tableTypes = {
		"fact": ["classroom", "course", "student", "student group", "subject", "teacher", "time"]
	};

	var factTypeConfig = {
		"classroom": [
			{
				key: "room number",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			{
				key: "size",
				value: null,
				required: true,
				type: "number",
				multipleValues: false
			},
			{
				key: "time",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "subject",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "teacher",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "course",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		],
		"course": [
			{
				key: "course name",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			{
				key: "term",
				value: null,
				error: null,
				required: true,
				type: "dropdown",
				multipleValues: false,
				possibleAnswers: ["year", "quarter"]
			},
			{
				key: "size",
				value: {
					min: null,
					max: null
				},
				required: false,
				type: "minMax",
				multipleValues: false
			},
			{
				key: "time",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "subject",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "teacher",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "classroom",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		],
		"student": [
			{
				key: "id",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			{
				key: "gender",
				value: null,
				error: null,
				required: true,
				type: "dropdown",
				multipleValues: false,
				possibleAnswers: ["female", "male", "other"]
			},
			{
				key: "name",
				value: null,
				error: null,
				required: true,
				type: "text",
				multipleValues: false
			},
			{
				key: "date of birth",
				value: null,
				error: null,
				required: true,
				type: "date",
				multipleValues: false
			},
			{
				key: "time",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "student group",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "required course",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		],
		"student group": [
			{
				key: "group name",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			{
				key: "time",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "student",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "required course",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		],
		"subject": [
			{
				key: "subject name",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			{
				key: "time",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "course",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "teacher",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "classroom",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		],
		"teacher": [
			{
				key: "id",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			{
				key: "name",
				value: null,
				error: null,
				required: true,
				type: "text",
				multipleValues: false
			},
			{
				key: "time",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "subject",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "course",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "classroom",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		],
		"time": [
			{
				key: "start time",
				value: null,
				required: true,
				type: "startEnd",
				multipleValues: false
			},
			{
				key: "end time",
				value: null,
				required: true,
				type: "startEnd",
				multipleValues: false
			},
			{
				key: "days",
				value: null,
				error: null,
				required: true,
				type: "dropdown",
				multipleValues: true,
				possibleAnswers: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "weekdays"]
			},
			{
				key: "subject",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "course",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "classroom",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		],
	};


	return {

		
		getTableConfiguration: function() {
			var self = this;

			self.updateTableConfig();

			return tableConfig;
		},

		getTableSelections: function(tableType) {
			return tableTypes[tableType];
		},

		getTableFacts: function(factName) {
			var url;
			var deferred = $q.defer();

			if (!factName) {
				return null;
			}

			// @TODO: change to get from back-end instead
			if (factName === "time") {
				deferred.resolve([
					{
						"time": "12:15PM-01:00PM",
						"days": ["monday", "wednesday", "friday"],
						"subjects": null,
						"courses": null,
						"teachers": null,
						"classrooms": null
					},
					{
						"time": "12:20PM-14:20PM",
						"days": ["tuesday", "thursday", "friday"],
						"subjects": null,
						"courses": null,
						"teachers": null,
						"classrooms": null
					},
					{
						"time": "2:00PM-2:45PM",
						"days": ["monday", "wednesday", "friday"],
						"subjects": null,
						"courses": null,
						"teachers": null,
						"classrooms": null
					}
				]);
				return deferred.promise;
			}
			else if (factName === "subject") {
				url = SUBJECT_URL;
			}
			else if (factName === "teacher") {
				url = TEACHER_URL;
			}
			else if (factName === "student") {
				url = STUDENT_URL;
			}
			else if (factName === "classroom") {
				url = CLASSROOM_URL;
			}
			else if (factName === "course" || factName === "required course" ) {
				url = COURSE_URL;
			}
			else if (factName === "student group") {
				url = STUDENT_GROUP_URL;
			}
			else {
				console.error("tableEntriesService.getTableFacts: unexpected state: invalid factName: " + constraintName);
				deferred.reject("ERROR: Unexpected front-end input.");
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url);

			$http.get(url).then(function(data) {
				// @TODO: this should automatically be conformed later
				var conformedData = [], i;
				// conform based on url, since we have no other way of knowing what type it is
				if (data.config.url.indexOf("student_groups") > 0) {
					// blank
					conformedData.push({
						"name": "4th grade",
						"students": null,
						"attributes": null,
						"transition to": "5th grade",
						"times": null,
						disabled: false
					});

					conformedData.push({
						"name": "5th grade",
						"students": null,
						"attributes": null,
						"transition to": "6th grade",
						"times": null,
						disabled: false
					});

					conformedData.push({
						"name": "6th grade",
						"students": null,
						"attributes": null,
						"transition to": null,
						"times": null,
						disabled: false
					});

					conformedData.push({
						"name": "student body",
						"students": null,
						"attributes": "Student - male",
						"transition to": null,
						"times": null,
						disabled: false
					});
				}
				else if (data.config.url.indexOf("students") > 0) {
					for (i = 0; i < data.data.length; i++) {
						conformedData.push({
							"id": data.data[i].id,
							"first name": data.data[i].first_name,
							"last name": data.data[i].last_name,
							"gender": null,
							"date of birth": null,
							"student groups": data.data[i].students_student_groups,
							"courses": data.data[i].courses_students,
							"times": null,
							disabled: false
						});
					}
				}
				else if (data.config.url.indexOf("teachers") > 0) {
					for (i = 0; i < data.data.length; i++) {
						conformedData.push({
							"id": data.data[i].id,
							"first name": data.data[i].first_name,
							"last name": data.data[i].last_name,
							"courses": data.data[i].courses_teachers,
							"subjects": data.data[i].subjects_teachers,
							"classrooms": data.data[i].classrooms_teachers,
							"times": null,
							disabled: false
						});
					}
				}
				else if (data.config.url.indexOf("classrooms") > 0) {
					for (i = 0; i < data.data.length; i++) {
						conformedData.push({
							"room": data.data[i].room_number,
							"seats": data.data[i].max_student_count,
							"subjects": data.data[i].classrooms_subjects,
							"teachers": data.data[i].classrooms_teachers,
							"courses": data.data[i].classrooms_courses,
							"times": null,
							disabled: false
						});
					}
				}
				else if (data.config.url.indexOf("courses") > 0) {
					for (i = 0; i < data.data.length; i++) {
						conformedData.push({
							"course": data.data[i].name,
							"term": data.data[i].term,
							"size": {
								min: data.data[i].min_student_count,
								max: data.data[i].max_student_count
							},
							"subjects": data.data[i].courses_subjects,
							"teachers": data.data[i].courses_teachers,
							"students": data.data[i].courses_students,
							"student groups": data.data[i].courses_student_groups,
							"rooms": data.data[i].classrooms_courses,
							"times": null,
							disabled: false
						});
					}
				}
				else if (data.config.url.indexOf("subjects") > 0) {
					// blank
					conformedData.push({
						"name": "Math",
						"courses": null,
						"teachers": null,
						"times": null,
						disabled: false
					});

					conformedData.push({
						"name": "English",
						"courses": null,
						"teachers": null,
						"times": null,
						disabled: false
					});

					conformedData.push({
						"name": "Programming",
						"courses": null,
						"teachers": null,
						"times": null,
						disabled: false
					});

					conformedData.push({
						"name": "Science",
						"courses": null,
						"teachers": null,
						"times": null,
						disabled: false
					});

					conformedData.push({
						"name": "History",
						"courses": null,
						"teachers": null,
						"times": null,
						disabled: false
					});
				}
				else {
					console.error("tableEntriesService.getTableFacts: unexpected url reuturn: " + data.config.url);
				}
				deferred.resolve(conformedData);
			}, function(data) {
				deferred.reject(data.data);
			});
			return deferred.promise;
		},

		updateTableConfig: function(tableType, tableSelection) {
			var self = this;
			// we're simply requesting an update, but cannot update if there is no given config
			if (!tableType && !tableSelection && !tableConfig.tableType) {
				return;
			}
			else if (tableType) {
				tableConfig.tableType = tableType;
				tableConfig.tableSelection = tableSelection;
			}

			// retrieve the table entries depending on type and selection
			if (tableType === "fact" && tableSelection) {
				// reset entries
				tableConfig.entries = null;
				self.getTableFacts(tableSelection).then(function (data) {
					tableConfig.entries = data;
				}, function (data) {
					// @TODO: display error message
				});
			}
			// if (tableType === "fact", tableSelection === "course") {
			// 	tableConfig.entries = [
			// 		{
			// 			course: "English III",
			// 			subject: "English",
			// 			teacher: "Karyl Heider",
			// 			classroom: null,
			// 			term: "Year",
			// 			size: {
			// 				min: 15,
			// 				max: 30
			// 			},
			// 			time: {
			// 				start: '1420',
			// 				end: '1520'
			// 			},
			// 			disabled: true
			// 		},
			// 		{
			// 			course: "Programming I",
			// 			subject: null,
			// 			teacher: null,
			// 			classroom: [
			// 				"1001", "1002"
			// 			],
			// 			term: "Quarter",
			// 			size: {
			// 				min: 8,
			// 				max: 22
			// 			},
			// 			time: [
			// 				{
			// 					start: '1215',
			// 					end: '1300'
			// 				},
			// 				{
			// 					start: '1420',
			// 					end: '1520'
			// 				}
			// 			],
			// 			disabled: false
			// 		}
			// 	];
			// }
		},

		getFactTypeConfig: function(factType) {
			return factTypeConfig[factType];
		},

		/**
		 * Updates factTypeConfig[factType][x].facts with an array of facts if x is a constraint
		 */
		updateFactTypeFacts: function(factType) {
			var self = this;
			var i, ftc;

			if (!factTypeConfig[factType] ||
				!factTypeConfig[factType].length) {
				return;
			}

			// for ease of coding
			ftc = factTypeConfig[factType];

			for (i = 0; i < ftc.length; i++) {
				if (ftc[i].type === "constraint") {
					self.getConstraintFacts(ftc[i].key, i).then(function (data) {
						ftc[data.index].facts = data.data;
					}, function (data) {
						// @TODO: display error message
						// where data.data === message
					});
				}
			}
		},

		/**
		 * Retrieves the array of facts for a given constraint.
		 * index is simply based back through return deferrment as a way to keep track of an index in a for loop
		 */
		getConstraintFacts: function(constraintName, index) {
			var url;
			var deferred = $q.defer();

			if (!constraintName) {
				return null;
			}

			// @TODO: change to get from back-end instead
			if (constraintName === "time") {
				deferred.resolve({
					index: index,
					data: [
						"12:15PM-01:00PM",
						"12:20PM-14:20PM",
						"2:00PM-2:45PM"
					]
				});
				return deferred.promise;
			}
			else if (constraintName === "subject") {
				url = SUBJECT_URL;
				//return ["Math", "English", "Programming", "Science", "History"]
			}
			else if (constraintName === "teacher") {
				url = TEACHER_URL;
				//return ["Karyl Heider", "Ralph Winterspoon", "Leeroy Jenkins", "Mrs. Buttersworth"]
			}
			else if (constraintName === "student") {
				url = STUDENT_URL;
				//return ["Harry Potter", "Frodo Baggins", "Luke Skywalker", "Tron"]
			}
			else if (constraintName === "classroom") {
				url = CLASSROOM_URL;
				//return ["1001", "1002", "203L", "West 123"]
			}
			else if (constraintName === "course" || constraintName === "required course" ) {
				url = COURSE_URL;
				//return ["English III"]
			}
			else if (constraintName === "student group") {
				url = STUDENT_GROUP_URL;
				//return ["4th grade", "5th grade", "6th grade", "student body"]
			}
			else {
				console.error("tableEntriesService.getConstraintFacts: unexpected state: invalid constraintName: " + constraintName);
				deferred.reject({data: "ERROR: Unexpected front-end input.", index: index});
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url);

			$http.get(url).then(function(data) {
				// @TODO: this should automatically be conformed later
				
				var conformedData = [], i;
				// conform based on url, since we have no other way of knowing what type it is
				if (data.config.url.indexOf("student_groups") > 0) {
					conformedData = ["4th grade", "5th grade", "6th grade", "student body"];
				}
				else if (data.config.url.indexOf("students") > 0) {
					for (i = 0; i < data.data.length; i++) {
						conformedData.push(data.data[i].first_name + " " + data.data[i].last_name);
					}
				}
				else if (data.config.url.indexOf("teachers") > 0) {
					for (i = 0; i < data.data.length; i++) {
						conformedData.push(data.data[i].first_name + " " + data.data[i].last_name);
					}
				}
				else if (data.config.url.indexOf("classrooms") > 0) {
					for (i = 0; i < data.data.length; i++) {
						conformedData.push(data.data[i].room_number);
					}
				}
				else if (data.config.url.indexOf("courses") > 0) {
					for (i = 0; i < data.data.length; i++) {
						conformedData.push(data.data[i].name);
					}
				}
				else if (data.config.url.indexOf("subjects") > 0) {
					// blank
					conformedData = ["Math", "English", "Programming", "Science", "History"];
				}
				else {
					console.error("tableEntriesService.getConstraintFacts: unexpected url reuturn: " + data.config.url);
				}
				// @NOTE: don't forget about index
				deferred.resolve({data: conformedData, index: index});
			}, function(data) {
				deferred.reject({data: data.data, index: index});
			});
			return deferred.promise;
		}
	};
}]);