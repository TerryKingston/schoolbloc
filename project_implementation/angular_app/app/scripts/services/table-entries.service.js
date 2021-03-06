'use strict';

/**
 * Provides data objects for large tables
 */
angular.module('sbAngularApp').factory('tableEntriesService', ['$q', '$http', 'commonService', 'userAccessService', function($q, $http, commonService, userAccessService) {
	var SERVER_ROOT = "api/",
		CLASSROOM_URL = SERVER_ROOT + "classrooms",
		COURSE_URL = SERVER_ROOT + "courses",
		STUDENT_URL = SERVER_ROOT + "students",
		STUDENT_COURSE_URL = SERVER_ROOT + "student_course",
		STUDENT_GROUP_URL = SERVER_ROOT + "student_groups",
		DAY_URL = SERVER_ROOT + "days",
		SUBJECT_URL = SERVER_ROOT + "subjects",
		TEACHER_URL = SERVER_ROOT + "teachers",
		TIME_URL = SERVER_ROOT + "timeblocks",
		oneMoreAttempt = false;


	// never reinstantiate: reference will be lost with bound controllers
	var tableConfig = {
		tableType: null,
		tableSelection: null,
	};

	var tableTypes = {
		"fact": ["classroom", "course", "student", "student_group", "subject", "teacher", "timeblock"],
		"student": ["student_course"]
	};

	var factTypeConfig = {
		"student_course": [
			{
				key: "student_course",
				value: null,
				error: null,
				required: true,
				type: "constraint",
				multipleValues: false,
				facts: null
			}
		],
		"classroom": [
			{
				key: "room_number",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			// {
			// 	key: "max_student_count",
			// 	value: null,
			// 	required: true,
			// 	type: "number",
			// 	multipleValues: false
			// },
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
				key: "timeblock",
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
				key: "name",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			// {
			// 	key: "term",
			// 	value: null,
			// 	error: null,
			// 	required: true,
			// 	type: "dropdown",
			// 	multipleValues: false,
			// 	possibleAnswers: ["year", "quarter"]
			// },
			{
				key: "student_count",
				value: {
					min: null,
					max: null
				},
				required: false,
				type: "minMax",
				multipleValues: false
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
				key: "student",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "student_group",
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
			},
			{
				key: "timeblock",
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
				key: "uid",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			{
				key: "first_name",
				value: null,
				error: null,
				required: true,
				type: "text",
				multipleValues: false
			},
			{
				key: "last_name",
				value: null,
				error: null,
				required: true,
				type: "text",
				multipleValues: false
			},
			// {
			// 	key: "gender",
			// 	value: null,
			// 	error: null,
			// 	required: true,
			// 	type: "dropdown",
			// 	multipleValues: false,
			// 	possibleAnswers: ["female", "male", "other"]
			// },
			// {
			// 	key: "date_of_birth",
			// 	value: null,
			// 	error: null,
			// 	required: true,
			// 	type: "date",
			// 	multipleValues: false
			// },
			{
				key: "student_group",
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
				canBeElective: true,
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
				key: "timeblock",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		],
		"student_group": [
			{
				key: "name",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
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
				key: "course",
				value: null,
				error: null,
				required: false,
				canBeElective: true,
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
				key: "timeblock",
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
				key: "name",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			{
				key: "course",
				value: null,
				error: null,
				required: false,
				canBeElective: true,
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
				key: "student",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "student_group",
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
			},
			{
				key: "timeblock",
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
				key: "uid",
				value: null,
				error: null,
				required: true,
				type: "uniqueText",
				multipleValues: false
			},
			{
				key: "first_name",
				value: null,
				error: null,
				required: true,
				type: "text",
				multipleValues: false
			},
			{
				key: "last_name",
				value: null,
				error: null,
				required: true,
				type: "text",
				multipleValues: false
			},
			{
				key: "avail_start_time",
				value: null,
				required: false,
				type: "startEnd",
				multipleValues: false
			},
			{
				key: "avail_end_time",
				value: null,
				required: false,
				type: "startEnd",
				multipleValues: false
			},
			{
				key: "day",
				value: "Monday",
				error: null,
				required: true,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				addedValue: true,
				key: "day",
				value: "Tuesday",
				error: null,
				required: true,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				addedValue: true,
				key: "day",
				value: "Wednesday",
				error: null,
				required: true,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				addedValue: true,
				key: "day",
				value: "Thursday",
				error: null,
				required: true,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				addedValue: true,
				key: "day",
				value: "Friday",
				error: null,
				required: true,
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
				key: "subject",
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
			},
			{
				key: "timeblock",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		],
		"timeblock": [
			{
				key: "start_time",
				value: null,
				required: true,
				type: "startEnd",
				multipleValues: false
			},
			{
				key: "end_time",
				value: null,
				required: true,
				type: "startEnd",
				multipleValues: false
			},
			{
				key: "day",
				value: null,
				error: null,
				required: true,
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
				key: "student",
				value: null,
				error: null,
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "student_group",
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
				key: "subject",
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
		var i, j, daysAbbr,
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
			// add in days of the week
			if (constraintArr[i].days && constraintArr[i].days.length) {
				daysAbbr = "";
				for (j = 0; j < constraintArr[i].days.length; j++) {
					if (constraintArr[i].days[j] === "Monday") {
						daysAbbr = daysAbbr + "M";
					}
					else if (constraintArr[i].days[j] === "Tuesday") {
						daysAbbr = daysAbbr + "T";
					}
					else if (constraintArr[i].days[j] === "Wednesday") {
						daysAbbr = daysAbbr + "W";
					}
					else if (constraintArr[i].days[j] === "Thursday") {
						daysAbbr = daysAbbr + "H";
					}
					else if (constraintArr[i].days[j] === "Friday") {
						daysAbbr = daysAbbr + "F";
					}
					else if (constraintArr[i].days[j] === "Saturday") {
						daysAbbr = daysAbbr + "Sa";
					}
					else if (constraintArr[i].days[j] === "Sunday") {
						daysAbbr = daysAbbr + "Su";
					}
				}
				value = value + daysAbbr + " ";
			}
			if (constraintArr[i].first_name) {
				value = value + constraintArr[i].first_name + " ";
			}
			if (constraintArr[i].last_name) {
				value = value + constraintArr[i].last_name + " ";
			}
			if (constraintArr[i].name) {
				value = value + constraintArr[i].name + " ";
			}
			if (constraintArr[i].room_number) {
				value = value + constraintArr[i].room_number + " ";
			}
			if ((constraintArr[i].start_time || constraintArr[i].start_time === 0) && (constraintArr[i].end_time || constraintArr[i].end_time === 0)) {
				value = value + commonService.formatTimeM2S(constraintArr[i].start_time, constraintArr[i].end_time);
			}
			if (constraintArr[i].course) {
				value = value + constraintArr[i].course;
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

		getValueWithIdString: function(value, id) {
			return getDubValue(value, id);
		},

		addFact: function(factEntry, factType) {
			var url, rank, i, self = this;
			var manageStudents;
			var deferred = $q.defer();
			if (!factEntry) {
				deferred.reject("ERROR: needed parameter not provided.")
				return deferred.promise;
			}

			// convert URL as for each fact type
			if (factType === "timeblock") {
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
			else if (factType === "student_group") {
				url = STUDENT_GROUP_URL;
			}
			// special case because of POST student_course requirement (such as rank)
			else if (factType === "student_course") {
				manageStudents = userAccessService.getUsersManagedStudents();

				url = STUDENT_COURSE_URL;
				if (manageStudents && manageStudents.selectedStudent) {
					url = url + "?user_id=" + manageStudents.selectedStudent.id;
				}
				url = commonService.conformUrl(url);
				
				factEntry = {
					"id": factEntry.student_course[0].id,
					"priority": "high",
					"rank": null // @TODO
				};

				if (tableConfig.entries) {
					// set it to highest rank among all electives
					rank = 1;
					for (i = 0; i < tableConfig.entries.length; i++) {
						if (tableConfig.entries[i].priority === "high") {
							rank++;
						}
					}
					factEntry.rank = rank;
				}
				else {
					console.error("tableEntriesService.addFact: unexpected state");
					deferred.reject("ERROR: Not entries given.");
				}

				$http.post(url, factEntry).then(function(data) {
					// update the list since this fact should now be removed
					self.updateFactTypeFacts('student_course');
					deferred.resolve(data.data);

				}, function(data) {
					deferred.reject(data.data);
				});

				return deferred.promise;
			}
			else if (factType === "day") {
				url = DAY_URL;
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

		editStudentCourse: function(newRankArr) {
			var url, manageStudents;
			var deferred = $q.defer();

			if (!newRankArr || !newRankArr.length) {
				deferred.reject("ERROR: needed parameter not provided.")
				return deferred.promise;
			}

			url = STUDENT_COURSE_URL;
			manageStudents = userAccessService.getUsersManagedStudents();
			if (manageStudents && manageStudents.selectedStudent) {
				url = url + "?user_id=" + manageStudents.selectedStudent.id;
			}
			url = commonService.conformUrl(url);

			$http.put(url, newRankArr).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				deferred.reject(data.data);
			});
			return deferred.promise;
		},

		editFact: function(factEntry, factId, factType) {
			var url;
			var deferred = $q.defer();
			if (!factEntry || !factId) {
				deferred.reject("ERROR: needed parameter not provided.")
				return deferred.promise;
			}

			// convert URL as for each fact type
			if (factType === "timeblock") {
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
			else if (factType === "student_group") {
				url = STUDENT_GROUP_URL;
			}
			else if (factType === "day") {
				url = DAY_URL;
			}
			else {
				console.error("tableEntriesService.addFact: unexpected state: invalid factType: " + factType);
				deferred.reject("ERROR: Unexpected front-end input.");
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url + "/" + factId);

			$http.put(url, factEntry).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				deferred.reject(data.data);
			});
			return deferred.promise;
		},

		deleteFact: function(factId, factType) {
			var url, manageStudents, self = this;
			var deferred = $q.defer();
			if (!factId) {
				deferred.reject("ERROR: needed parameter not provided.")
				return deferred.promise;
			}

			// convert URL as for each fact type
			if (factType === "timeblock") {
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
			else if (factType === "student_group") {
				url = STUDENT_GROUP_URL;
			}
			else if (factType === "day") {
				url = DAY_URL;
			}
			else if (factType === "student_course") {
				// done later as constrains=true is added
			}
			else {
				console.error("tableEntriesService.addFact: unexpected state: invalid factType: " + factType);
				deferred.reject("ERROR: Unexpected front-end input.");
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url + "/" + factId);

			if (factType === "student_course") {
				manageStudents = userAccessService.getUsersManagedStudents();
				url = STUDENT_COURSE_URL + "?course_id=" + factId;
				if (manageStudents && manageStudents.selectedStudent) {
					url = url + "&user_id=" + manageStudents.selectedStudent.id;
				}
				url = commonService.conformUrl(url);
			}

			$http.delete(url).then(function(data) {
				if (factType === 'student_course') {
					// update the list since this fact should now be removed
					self.updateFactTypeFacts('student_course');
				}
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
			var url, manageStudents, self = this;
			var deferred = $q.defer();

			if (!factName) {
				deferred.reject("ERROR: needed parameter not provided.")
				return deferred.promise;
			}

			if (factName === "timeblock") {
				url = TIME_URL;
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
			else if (factName === "student_group") {
				url = STUDENT_GROUP_URL;
			}
			else if (factName === "day") {
				url = DAY_URL;
			}
			else if (factName === "student_course") {
				// done later as constrains=true is added
			}
			else {
				console.error("tableEntriesService.getTableFacts: unexpected state: invalid factName: " + factName);
				deferred.reject("ERROR: Unexpected front-end input.");
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url) + '?constraints=true';

			if (factName === "student_course") {
				manageStudents = userAccessService.getUsersManagedStudents();
				url = STUDENT_COURSE_URL;
				if (manageStudents && manageStudents.selectedStudent) {
					url = url + "?user_id=" + manageStudents.selectedStudent.id;
				}
				url = commonService.conformUrl(url);
			}

			$http.get(url).then(function(data) {
				deferred.resolve(data.data);
			}, function(data) {
				// race condition has caused the user_id not to be removed quick enough, try again
				if (!oneMoreAttempt && factName === "student_course" && data.data.message === "Access denied") {
					userAccessService.resetManagedStudents();
					// make sure this isn't infinitely recursive
					oneMoreAttempt = true;
					self.getTableFacts(factName).then(function(data) {
						oneMoreAttempt = false;
						deferred.resolve(data);
					}, function(data) {
						oneMoreAttempt = false;
						deferred.reject(data);
					});
				}
				else {
					deferred.reject(data.data);
				}
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
					var i, j, k, daysAbbr, timeSplit;
					// fix time to be in standard time
					for (i = 0; i < data.length; i++) {
						if (data[i].start_time || data[i].start_time === 0) {
							data[i].start_time = commonService.formatSingleTimeM2S(data[i].start_time);
						}
						if (data[i].end_time || data[i].end_time === 0) {
							data[i].end_time = commonService.formatSingleTimeM2S(data[i].end_time);
						}
						if (data[i].avail_start_time || data[i].avail_start_time === 0) {
							data[i].avail_start_time = commonService.formatSingleTimeM2S(data[i].avail_start_time);
						}
						if (data[i].avail_end_time || data[i].avail_end_time === 0) {
							data[i].avail_end_time = commonService.formatSingleTimeM2S(data[i].avail_end_time);
						}
						if (data[i].timeblock && data[i].timeblock.length) {
							for (j = 0; j < data[i].timeblock.length; j++) {
								timeSplit = data[i].timeblock[j].value.split(" ");
								data[i].timeblock[j].value = commonService.formatTimeM2S(timeSplit[0], timeSplit[1]);
								// add in days of the week
								if (data[i].timeblock[j].days && data[i].timeblock[j].days.length) {
									daysAbbr = "";
									for (k = 0; k < data[i].timeblock[j].days.length; k++) {
										if (data[i].timeblock[j].days[k] === "Monday") {
											daysAbbr = daysAbbr + "M";
										}
										else if (data[i].timeblock[j].days[k] === "Tuesday") {
											daysAbbr = daysAbbr + "T";
										}
										else if (data[i].timeblock[j].days[k] === "Wednesday") {
											daysAbbr = daysAbbr + "W";
										}
										else if (data[i].timeblock[j].days[k] === "Thursday") {
											daysAbbr = daysAbbr + "H";
										}
										else if (data[i].timeblock[j].days[k] === "Friday") {
											daysAbbr = daysAbbr + "F";
										}
										else if (data[i].timeblock[j].days[k] === "Saturday") {
											daysAbbr = daysAbbr + "Sa";
										}
										else if (data[i].timeblock[j].days[k] === "Sunday") {
											daysAbbr = daysAbbr + "Su";
										}
									}
									data[i].timeblock[j].value = daysAbbr + " " + data[i].timeblock[j].value;
								} 
							}
						}
					}
					tableConfig.entries = data;
					// // DEBUG: go ahead and add disabled for show casing
					for (i = 0; i < tableConfig.entries.length; i++) {
						tableConfig.entries[i].disabled = false;
					}
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
			var url, manageStudents;
			var deferred = $q.defer();

			if (!constraintName) {
				deferred.reject({data: "ERROR: needed parameter not provided.", index: index});
				return deferred.promise;
			}

			if (constraintName === "timeblock") {
				url = TIME_URL;
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
			else if (constraintName === "student_group") {
				url = STUDENT_GROUP_URL;
			}
			else if (constraintName === "day") {
				url = DAY_URL;
			}
			else if (constraintName === "student_course") {
				// performed later since constraints=false is added
			}
			else {
				console.error("tableEntriesService.getConstraintFacts: unexpected state: invalid constraintName: " + constraintName);
				deferred.reject({data: "ERROR: Unexpected front-end input.", index: index});
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url) + '?constraints=false';;

			if (constraintName === "student_course") {
				manageStudents = userAccessService.getUsersManagedStudents();
				url = STUDENT_COURSE_URL + "?electives=true";
				if (manageStudents && manageStudents.selectedStudent) {
					url = url + "&user_id=" + manageStudents.selectedStudent.id;
				}
				url = commonService.conformUrl(url);
			}

			$http.get(url).then(function(data) {
				deferred.resolve({data: data.data, index: index});
			}, function(data) {
				deferred.reject({data: data.data, index: index});
			});
			return deferred.promise;
		}
	};
}]);
