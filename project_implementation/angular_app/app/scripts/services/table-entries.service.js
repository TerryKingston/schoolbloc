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
				key: "course name",
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
				multipleValues: true
			},
			{
				key: "subject",
				required: false,
				type: "constraint",
				multipleValues: true
			},
			{
				key: "teacher",
				required: false,
				type: "constraint",
				multipleValues: true
			},
			{
				key: "classroom",
				required: false,
				type: "constraint",
				multipleValues: true
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
						size: "15-30",
						time: null,
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
						size: "8-22",
						time: null,
						disabled: false
					}
				];
			}
		},

		getFactTypeConfig: function(factType) {
			return factTypeConfig[factType];
		}
	};
}]);