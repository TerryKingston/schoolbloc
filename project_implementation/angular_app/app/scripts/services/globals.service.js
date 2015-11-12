'use strict';

/**
 * Provides global variables.  
 * Very dangerous.  
 * Antipattern.  
 * But gets the job done.
 */
angular.module('sbAngularApp').factory('globalService', [ function() {
	var global = {
	};

	var stateUpdates = {
		// when a user somehow accesses a section that is forbidden
		forbiddenState: false
	}


	return {

		/**
		 * Returns the global reference object.
		 * Please note, that the use of global is a major antipattern, 
		 * but it is a simple way to have global variables.
		 * Do not use global variables for things that could break the app.
		 *
		 * If need be, create other variables so that you can access them separately from "global".
		 */
		getGlobal: function() {
			return global;
		},

		/**
		 * Returns the stateUpdates reference object.
		 * Please note, that the use of a global is a major antipattern, 
		 * but it is a simple way to have global variables.
		 * Do not use global variables for things that could break the app.
		 *
		 * stateUpdates triggers possible redirects as needed.
		 */
		getStateUpdates: function() {
			return stateUpdates;
		}
	};
}]);