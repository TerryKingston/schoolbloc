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
		TIME_URL = SERVER_ROOT + "time_blocks";


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
		]
	};

	var getDubValue = function (value, id) {
		return value + " #" + id;
	};

	var mapFactObjectToValue = function (entity, constraintArr) {
		var i,
			factValues = [],
			// make an entity.factsMap object to map the constraintArr id to the unqiue factValues[x] that we create
			factsMap = {},
			keys,
			value;

		if (!entity) {
			return;
		}

		if (!constraintArr || !Array.isArray(constraintArr)) {
			entity.facts = {};
			entity.facts.values = factValues;
			entity.facts.map = factsMap;
			return;
		}

		// go through the array of objects and change the object into a value (obj.first_name + obj.last_name = factValues[x])
		for (i = 0; i < constraintArr.length; i++) {
			value = "";
			if (constraintArr[i].first_name) {
				value = value + constraintArr[i].first_name + " ";
			}
			if (constraintArr[i].last_name) {
				value = value + constraintArr[i].last_name + " ";
			}
			if (constraintArr[i].name) {
				value = value + constraintArr[i].name + " ";
			}
			value = value.trim();

			// if factValues[x] is equal to any factsMap key, we have a duplicate and we should alter all duplicates to contain factValues[x] + " (id)"
			if (factsMap[value]) {
				// keep this factsMap[value] for this check, but remove from factValues array so it doesn't show up in the view
				// check if we need to create a mapping for the old value
				if (!factsMap[getDubValue(value, factsMap[value])]) {
					factsMap[getDubValue(value, factsMap[value])] = factsMap[value];
				}
				// create the new mapping
				factsMap[getDubValue(value, constraintArr[i].id)] = constraintArr[i].id;
			}
			else {
				factsMap[value] = constraintArr[i].id;
			}
		}

		keys = Object.keys(factsMap);
		// add values to factValues, but only the dub values if they exist
		for (i = 0; i < keys.length; i++) {
			// for example, do not add fM['bob'] if fM['bob (1)' exists]
			if (!factsMap[getDubValue(keys[i], factsMap[keys[i]])]) {
				factValues.push(keys[i]);
			} 
		}

		entity.facts = {};
		entity.facts.values = factValues;
		entity.facts.map = factsMap;
	};


	return {

		addFact: function(factEntry, factType) {
			var url;
			var deferred = $q.defer();
			if (!factEntry) {
				deferred.reject("ERROR: needed parameter not provided.")
				return deferred.promise;
			}

			// convert URL as for each fact type
			if (factType === "time") {
				url = TIME_URL;
			}
			else if (factType === "subject") {
				url = SUBJECT_URL;
			}
			else if (factType === "teacher") {
				url = TEACHER_URL;
			}
			else if (factType === "student") {
				url = STUDENT_URL;
			}
			else if (factType === "classroom") {
				url = CLASSROOM_URL;
			}
			else if (factType === "course" || factType === "required course" ) {
				url = COURSE_URL;
			}
			else if (factType === "student group") {
				url = STUDENT_GROUP_URL;
			}
			else {
				console.error("tableEntriesService.addFact: unexpected state: invalid factType: " + factType);
				deferred.reject("ERROR: Unexpected front-end input.");
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url);

			$http.post(url, factEntry).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				deferred.reject(data.data);
			});
			return deferred.promise;
		},

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
				deferred.reject("ERROR: needed parameter not provided.")
				return deferred.promise;
			}

			// @TODO: change to get from back-end instead
			if (factName === "time") {
				url = TIME_URL;
				// deferred.resolve([
				// 	{
				// 		"time": "12:15PM-01:00PM",
				// 		"days": ["monday", "wednesday", "friday"],
				// 		"subjects": null,
				// 		"courses": null,
				// 		"teachers": null,
				// 		"classrooms": null
				// 	},
				// 	{
				// 		"time": "12:20PM-14:20PM",
				// 		"days": ["tuesday", "thursday", "friday"],
				// 		"subjects": null,
				// 		"courses": null,
				// 		"teachers": null,
				// 		"classrooms": null
				// 	},
				// 	{
				// 		"time": "2:00PM-2:45PM",
				// 		"days": ["monday", "wednesday", "friday"],
				// 		"subjects": null,
				// 		"courses": null,
				// 		"teachers": null,
				// 		"classrooms": null
				// 	}
				// ]);
				// return deferred.promise;
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
        		var conformedElement = [];
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
					//for (i = 0; i < data.data.length; i++) {
					//	conformedData.push({
					//		"id": data.data[i].id,
					//		"first name": data.data[i].first_name,
					//		"last name": data.data[i].last_name,
					//		"gender": null,
					//		"date of birth": null,
					//		"student groups": data.data[i].students_student_groups,
					//		"courses": data.data[i].courses_students,
					//		"times": null,
					//		disabled: false
					//	});
					//}
          for(i = 0; i < data.data.length; i++)
          {
            conformedData.push({
              "id": data.data[i].id,
              "first name": data.data[i].first_name,
              "last name": data.data[i].last_name,
              "gender": null,
              "date of birth": null,
              "student groups": data.data[i].students_student_groups.map(function(group){
                return group.student_group.name;
              }),
              "courses": data.data[i].scheduled_classes_student.map(function(course){
                return course.scheduled_class.course.name;
              }),
              "times": null,
              disabled: false
            })
          }
				}
				else if (data.config.url.indexOf("teachers") > 0) {
					for (i = 0; i < data.data.length; i++) {
						//conformedData.push({
						//	"id": data.data[i].id,
						//	"first name": data.data[i].first_name,
						//	"last name": data.data[i].last_name,
						//	"courses": data.data[i].courses_teachers,
						//	"subjects": data.data[i].subjects_teachers,
						//	"classrooms": data.data[i].classrooms_teachers,
						//	"times": null,
						//	disabled: false
						//});

          conformedData.push({
            "id": data.data[i].id,
            "first name": data.data[i].first_name,
            "last name": data.data[i].last_name,
            "courses": data.data[i].scheduled_class.map(function(course){
              return course.name;
            }),
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
							"subjects": data.data[i].courses_subjects.map(function(course_subjects){
                return course_subjects.subject.name;
              }),
							"teachers": data.data[i].courses_teachers,
							"students": data.data[i].courses_students,
							"student groups": data.data[i].courses_student_groups.map(function(group) {
                return group.student_group.name;
              }),
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
						mapFactObjectToValue(ftc[data.index], data.data);
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
				deferred.reject({data: "ERROR: needed parameter not provided.", index: index});
				return deferred.promise;
			}

			// @TODO: change to get from back-end instead
			if (constraintName === "time") {
				url = TIME_URL;
				// deferred.resolve({
				// 	index: index,
				// 	data: [
				// 		"12:15PM-01:00PM",
				// 		"12:20PM-14:20PM",
				// 		"2:00PM-2:45PM"
				// 	]
				// });
				// return deferred.promise;
			}
			else if (constraintName === "subject") {
				url = SUBJECT_URL;
			}
			else if (constraintName === "teacher") {
				url = TEACHER_URL;
			}
			else if (constraintName === "student") {
				url = STUDENT_URL;
			}
			else if (constraintName === "classroom") {
				url = CLASSROOM_URL;
			}
			else if (constraintName === "course" || constraintName === "required course" ) {
				url = COURSE_URL;
			}
			else if (constraintName === "student group") {
				url = STUDENT_GROUP_URL;
			}
			else {
				console.error("tableEntriesService.getConstraintFacts: unexpected state: invalid constraintName: " + constraintName);
				deferred.reject({data: "ERROR: Unexpected front-end input.", index: index});
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url);

			$http.get(url).then(function(data) {
				deferred.resolve({data: data.data, index: index});
			}, function(data) {
				deferred.reject({data: data.data, index: index});
			});
			return deferred.promise;
		}
	};
}]);
