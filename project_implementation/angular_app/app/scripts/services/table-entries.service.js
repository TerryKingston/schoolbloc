'use strict';

/**
 * Provides data objects for large tables
 */
angular.module('sbAngularApp').factory('tableEntriesService', [ function() {
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

		updateTableConfig: function(tableType, tableSelection) {
			// we're simply requesting an update, but cannot update if there is no given config
			if (!tableType && !tableSelection && !tableConfig.tableType) {
				return;
			}
			else if (tableType) {
				tableConfig.tableType = tableType;
				tableConfig.tableSelection = tableSelection;
			}

			// retrieve the table entries depending on type and selection
			if (tableType === "fact", tableSelection === "course") {
				tableConfig.entries = [
					{
						course: "English III",
						subject: "English",
						teacher: "Karyl Heider",
						classroom: null,
						term: "Year",
						size: {
							min: 15,
							max: 30
						},
						time: {
							start: '1420',
							end: '1520'
						},
						disabled: true
					},
					{
						course: "Programming I",
						subject: null,
						teacher: null,
						classroom: [
							"1001", "1002"
						],
						term: "Quarter",
						size: {
							min: 8,
							max: 22
						},
						time: [
							{
								start: '1215',
								end: '1300'
							},
							{
								start: '1420',
								end: '1520'
							}
						],
						disabled: false
					}
				];
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
					ftc[i].facts = self.getConstraintFacts(ftc[i].key);
				}
			}
		},

		getConstraintFacts: function(constraintName) {
			if (!constraintName) {
				return null;
			}

			// @TODO: change to get from back-end instead
			if (constraintName === "time") {
				return [
					{
						start: '1215',
						end: '1300'
					},
					{
						start: '1420',
						end: '1520'
					},
					{
						start: '1400',
						end: '1445'
					}
				];
			}
			else if (constraintName === "subject") {
				return ["Math", "English", "Programming", "Science", "History"]
			}
			else if (constraintName === "teacher") {
				return ["Karyl Heider", "Ralph Winterspoon", "Leeroy Jenkins", "Mrs. Buttersworth"]
			}
			else if (constraintName === "student") {
				return ["Harry Potter", "Frodo Baggins", "Luke Skywalker", "Tron"]
			}
			else if (constraintName === "classroom") {
				return ["1001", "1002", "203L", "West 123"]
			}
			else if (constraintName === "course" || constraintName === "required course" ) {
				return ["English III"]
			}
			else if (constraintName === "student group") {
				return ["4th grade", "5th grade", "6th grade", "student body"]
			}
			else {
				console.error("tableEntriesService.getConstraintFacts: unexpected state: invalid constraintName: " + constraintName);
				return null;
			}
		}
	};
}]);