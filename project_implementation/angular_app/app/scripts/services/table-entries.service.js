'use strict';

/**
 * Provides data objects for large tables
 */
angular.module('sbAngularApp').factory('tableEntriesService', [ function() {
	// never reinstantiate: reference will be lost with bound controllers
	var tableConfig = {
		tableType: null,
		tableSelection: null
	};

	var factTypeConfig = {
		"course": [
			{
				key: "course",
				required: true,
				type: "text",
				multipleValues: false
			},
			{
				key: "term",
				required: true,
				type: "dropdown",
				multipleValues: false,
				possibleAnswers: ["year", "quarter"]
			},
			{
				key: "size",
				required: false,
				type: "minMax",
				multipleValues: true
			},
			{
				key: "time",
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "subject",
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "teacher",
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			},
			{
				key: "classroom",
				required: false,
				type: "constraint",
				multipleValues: true,
				facts: null
			}
		]
	}


	return {

		
		getTableConfiguration: function() {
			var self = this;

			self.updateTableConfig();

			return tableConfig;
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
							start: 1420,
							end: 1520
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
								start: 1215,
								end: 1300
							},
							{
								start: 1420,
								end: 1520
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
						start: 1215,
						end: 1300
					},
					{
						start: 1420,
						end: 1520
					},
					{
						start: 1400,
						end: 1445
					}
				];
			}
			else if (constraintName === "subject") {
				return ["Math", "English", "Programming", "Science", "History"]
			}
			else if (constraintName === "teacher") {
				return ["Karyl Heider", "Ralph Winterspoon", "Leeroy Jenkins", "Mrs. Buttersworth"]
			}
			else if (constraintName === "classroom") {
				return ["1001", "1002", "203L", "West 123"]
			}
			else {
				console.error("tableEntriesService.getConstraintFacts: unexpected state: invalid constraintName: " + constraintName);
				return null;
			}
		}
	};
}]);