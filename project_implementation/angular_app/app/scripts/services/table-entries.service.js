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
		TIME_URL = SERVER_ROOT + "timeblocks";


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
				key: "course",
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
				key: "user_id",
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
				key: "user_id",
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
			// {
			// 	key: "days",
			// 	value: null,
			// 	error: null,
			// 	required: true,
			// 	type: "dropdown",
			// 	multipleValues: true,
			// 	possibleAnswers: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "weekdays"]
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
			if (constraintArr[i].room_number) {
				value = value + constraintArr[i].room_number + " ";
			}
			if ((constraintArr[i].start_time || constraintArr[i].start_time === 0) && (constraintArr[i].end_time || constraintArr[i].end_time === 0)) {
				value = value + commonService.formatTimeM2S(constraintArr[i].start_time, constraintArr[i].end_time);
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
			var url;
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
			var url;
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
			else {
				console.error("tableEntriesService.addFact: unexpected state: invalid factType: " + factType);
				deferred.reject("ERROR: Unexpected front-end input.");
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url + "/" + factId);

			$http.delete(url).then(function(data) {
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
			else if (factName === "student_course") {
				// @TODO: change later
				url = COURSE_URL;
			}
			else {
				debugger;
				console.error("tableEntriesService.getTableFacts: unexpected state: invalid factName: " + factName);
				deferred.reject("ERROR: Unexpected front-end input.");
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url) + '?constraints=true';

			$http.get(url).then(function(data) {
				deferred.resolve(data.data);
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
					var i, j, timeSplit;
					// fix time to be in standard time
					for (i = 0; i < data.length; i++) {
						if (data[i].start_time || data[i].start_time === 0) {
							data[i].start_time = commonService.formatSingleTimeM2S(data[i].start_time);
						}
						if (data[i].end_time || data[i].end_time === 0) {
							data[i].end_time = commonService.formatSingleTimeM2S(data[i].end_time);
						}
						if (data[i].timeblock && data[i].timeblock.length) {
							for (j = 0; j < data[i].timeblock.length; j++) {
								timeSplit = data[i].timeblock[j].value.split(" ");
								data[i].timeblock[j].value = commonService.formatTimeM2S(timeSplit[0], timeSplit[1]);
							}
						}
					}
					tableConfig.entries = data;
					// DEBUG: go ahead and add disabled for show casing
					for (i = 0; i < tableConfig.entries.length; i++) {
						tableConfig.entries[i].disabled = Math.random() < 0.2;
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
			var url;
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
			else {
				console.error("tableEntriesService.getConstraintFacts: unexpected state: invalid constraintName: " + constraintName);
				deferred.reject({data: "ERROR: Unexpected front-end input.", index: index});
				return deferred.promise;
			}

			// conform the url to change the port
			url = commonService.conformUrl(url) + '?constraints=false';;

			$http.get(url).then(function(data) {
				deferred.resolve({data: data.data, index: index});
			}, function(data) {
				deferred.reject({data: data.data, index: index});
			});
			return deferred.promise;
		}
	};
}]);
