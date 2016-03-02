'use strict';

/**
 * Provides a lot of quick and basic functions that are useful and common among many areas of the app.
 */
angular.module('sbAngularApp').factory('commonService', ['$translate', '$window', '$location', function($translate, $window, $location) {
	
	/**
	 * Returns true if time is a valid military time, false otherwise
	 * @param  {string} time   string representing time
	 */
	function checkMilitaryTime(time) {
		var timeValue;
		// needs four characters: 0000
		if (Number.isInteger(time)) {
			time = time + "";
		}
		if (!time || !time.length || time.length !== 4) {
			return false;
		}
		timeValue = parseInt(time);
		// needs be between 0000-2359
		if (timeValue < 0 || timeValue > 2359) {
			return false;
		}
		return true;
	}

	/**
	 * Returns true if time is a valid standard time, false otherwise
	 * @param  {string} time   string representing time
	 */
	function checkStandardTime(time) {
		var curCheck;
		var timeValue;
		// needs 7 characters: 00:00XX
		if (!time || !time.length || time.length !== 7) {
			return false;
		}
		// check hour between 01 and 12
		curCheck = time.substring(0,2);
		timeValue = parseInt(curCheck);
		if (timeValue < 1 || timeValue > 12) {
			return false;
		}
		// check :
		if (time.indexOf(':') !== 2) {
			return false;
		}
		// check minute between 00 and 59
		curCheck = time.substring(3,5);
		timeValue = parseInt(curCheck);
		if (timeValue < 0 || timeValue > 59) {
			return false;
		}
		// check AM/PM
		if (time.indexOf('AM') !== 5 && time.indexOf('PM') !== 5) {
			return false;
		}
		return true;
	}

	/**
	 * Generates a standard time out of a validated military time format
	 */
	function generateStandardTime(time) {
		var timeValue = parseInt(time);
		var timeString;
		var amPm = 'AM';

		if (timeValue >= 1200) {
			amPm = 'PM';
			// reduce it to 12 hour format
			timeValue -= 1200;
		}

		// convert 00 --> 12
		if (timeValue < 100) {
			timeValue += 1200;
		}

		// add necessary leading 0s
		timeString = addLeadingZerosMilitary(timeValue);

		return timeString.substring(0,2) + ":" + timeString.substring(2) + amPm;
	}

	/**
	 * Generates a military time out of a validated standard time format
	 */
	function generateMilitaryTime(time) {
		// get 00:00
		var timeString = time.substring(0,5);
		var timeValue;
		var addedHours = 0;

		// get am/pm
		if (time.substring(5) === 'PM') {
			addedHours = 1200;
		}

		// remove :
		timeString = timeString.replace(':', '');

		// 12:00 special case
		// 12 --> 0
		if (timeString.substring(0,2) === '12') {
			timeString = timeString.substring(2);
		}

		// get correct 24-hour time
		timeValue = parseInt(timeString);
		timeValue += addedHours;

		return addLeadingZerosMilitary(timeValue);
	}

	/**
	 * Adds leading zeros to military time is always 4 digits (0000)
	 * @param  {int} time   integer representing military time
	 */
	function addLeadingZerosMilitary(time) { 
		// add any needed leading zeros
		if (time < 10) {
			return "000" + time;
		}
		if (time < 100) {
			return "00" + time;
		}
		if (time < 1000) {
			return "0" + time;
		}
		return time + '';
	}

	return {

		/**
		 * Generates a valid portion of a URL based on the given value
		 * @param  value will be converted into URL
		 * @return       converted URL
		 */
		generateValidUrl: function(value) {
			if (!value) {
				return "";
			}
			return value.replace(/ /g,"-");
		},

		/**
		 * Renders the URL correctly with given port and absolute path if need be
		 */
		conformUrl: function(url) {
			// port of backend
			var port = "5000";
			return $location.protocol() + "://" + $location.host() + ":" + port + "/" + url;
		},

		/**
		 * Formats a given string value to replace all {x} with the given args[x].
		 * For example, "Hi {0}! This is {1}", where args[0] = "Bob" and args[1] = "Alice", then the return will be "Hi Bob! This is Alice"
		 * @param  {string} value The string value needed to be formatted.  Should contain "{x}", where x starts at 0 and incrementally goes up.
		 * @param  {array} args   Array of replacements for the {x} in the string value.
		 * @return {string}       Formatted string.
		 */
		format: function(value, args) {
			// @TODO: later, directly allow for: "This is a {0}".format("string")
			// CITE: https://gist.github.com/litera/9634958
			return value.replace(/\{(\d+)\}/g, function (match, capture) {
				// 1* so we can force capture to be a number
				return args[1*capture];
			});
			// END CITE
		},

		formatDateInput: function(input) {
			var date = input;
			var dateArr, month, day, year;

			var getDateParse = function(dateElement, max, min, isYear) {
				var value = parseInt(dateElement);
				
				// sometimes people might input 00/00/92, meaning 1992.
				// add in proper values
				if (value < 100 && isYear) {
					// @TODO: must update yearly
					// as in 2016 (the current year)
					if (value > 16) {
						value += 1900;
					}
					else {
						value += 2000;
					}
				}

				if (max && value > max) {
					return "ERROR";
				}
				if (min && value < min) {
					return "ERROR";
				}

				// add leading zeros as needed
				if (value < 10) {
					value = '0' + value;
				}
				return value + '';
			};

			// try to get input formatting in a more common way
			date = date.replace(" ", "");
			dateArr = date.split("/");

			if (dateArr.length !== 3) {
				// check - instead
				dateArr = date.split("-");
				if (dateArr.length !== 3) {
					return "ERROR";
				}
			}

			// check month, day, year
			month = getDateParse(dateArr[0], 12, 1, false);
			day = getDateParse(dateArr[1], 32, 1, false);
			// @TODO: must update yearly
			year = getDateParse(dateArr[2], 2016, 1916, true);
			if (month === "ERROR" || day === "ERROR" || year === "ERROR") {
				return "ERROR";
			}
			return month + "/" + day + "/" + year;
		},

		/**
		 * Formats military time (0000 - 2359) into standard time format
		 * @param  {string} time military time
		 * @return {string}       Returns 'ERROR' if improper format of time, or returns string of time in standard format.
		 */
		formatSingleTimeM2S: function(time) {
			if (!checkMilitaryTime(time)) {
				return "ERROR";
			}
			return generateStandardTime(time);
		},

		/**
		 * Formats military time (0000 - 2359) into standard time format
		 * @param  {string} start military time start
		 * @param  {string} end   military time end
		 * @return {string}       Returns 'ERROR' if improper format of timeRange, or returns string of start-end time in standard format.
		 */
		formatTimeM2S: function(start, end) {
			// make sure start and end are valid
			if (!checkMilitaryTime(start) ||
				!checkMilitaryTime(end)) {
				return "ERROR";
			}
			return generateStandardTime(start) + "-" + generateStandardTime(end);
		},

		/**
		 * Formats standard time into military time (0000 - 2359)
		 * @param  {string} time standard format
		 * @return {string}       	  Returns 'ERROR' if improper format of time, or a string in military time.
		 */
		formatSingleTimeS2M: function(time) {
			var timeArr;
			// requires a '-'' to be a range
			if (!time || time.indexOf('-') >= 0) {
				return 'ERROR';
			}
			// make sure start and end are valid
			if (!checkStandardTime(time)) {
				return "ERROR";
			}
			return generateMilitaryTime(time);
		},

		/**
		 * Formats standard time into military time (0000 - 2359)
		 * @param  {string} timeRange standard format start
		 * @return {string}       	  Returns 'ERROR' if improper format of timeRange, or returns {start: x, end: y}, where x and y are strings military time.
		 */
		formatTimeS2M: function(timeRange) {
			var timeArr;
			// requires a '-'' to be a range
			if (!timeRange || timeRange.indexOf('-') < 0) {
				return 'ERROR';
			}
			timeArr = timeRange.split('-');
			if (timeArr.length !== 2) {
				return 'ERROR';
			}
			// make sure start and end are valid
			if (!checkStandardTime(timeArr[0]) ||
				!checkStandardTime(timeArr[1])) {
				return "ERROR";
			}
			return {
				start: generateMilitaryTime(timeArr[0]),
				end: generateMilitaryTime(timeArr[1])
			};
		},

		/**
		 * Attempts to convert a user inputted time into a standard time.
		 * @param  {string} input some user inputted time
		 * @return {[type]}       Returns 'ERROR' if unable to convert range, or returns string of time in standard format.
		 */
		formatTimeInput2S: function(input) {
			var time = input;
			var hour, minutes, amPm, timeSplit;

			var convertHourAmPm = function(isAm, time) {
				var aP = "A";
				if (!isAm) {
					aP = "P";
				}
				hour = parseInt(time.substring(0, time.indexOf(aP)));
				return convertHour(hour);
			};

			/**
			 * hour must be a number or NaN
			 */
			var convertHour = function(hour) {
				// check it
				if (isNaN(hour) || hour < 0 || hour > 12) {
					return "ERROR";
				}
				// add leading zero if needed
				if (hour < 10) {
					return '0' + hour;
				}
				// make sure it's a string
				return '' + hour;
			};

			// try to get input formatting in a more common way
			time = time.toUpperCase();
			time = time.replace(" ", "");
			// at this point acceptable formats should look something like:
			// XX    XXAM    XX:XX    XX:XXAM
			//  X     XAM     X:XX     X:XXAM
			
			// XX    XXAM    X     XAM
			if (time.indexOf(":") < 0) {
				minutes = "00";
				// XXAM    XAM
				if (time.indexOf("AM") >= 0 || time.indexOf("A") >= 0) {
					amPm = "AM";
					hour = convertHourAmPm(true, time);
				}
				// XXPM    XPM
				else if (time.indexOf("PM") >= 0 || time.indexOf("P") >= 0) {
					amPm = "PM";
					hour = convertHourAmPm(false, time);
				}
				// XX      X
				else {
					hour = parseInt(time);
					// determine if problem
					if (convertHour(hour) === "ERROR") {
						return "ERROR";
					}
					// We need to look at the hour to guess am or pm. 
					// 6-11 --> AM, 12-5 --> PM
					amPm = "PM";
					if (hour >= 6 && hour <= 11) {
						amPm = "AM";
					}
					hour = convertHour(hour);
				}
				if (hour === "ERROR") {
					return "ERROR";
				}
				return hour+":"+minutes+amPm;
			}
			// XX:XX    XX:XXAM    X:XX     X:XXAM
			else {
				// split hour up from minutes
				timeSplit = time.split(":");
				if (timeSplit.length !== 2) {
					return "ERROR";
				}

				// get hour
				// XX      X
				hour = parseInt(timeSplit[0]);
				// determine if problem
				if (convertHour(hour) === "ERROR") {
					return "ERROR";
				}
				
				// get am or pm
				// XXAM    XAM
				if (time.indexOf("AM") >= 0 || time.indexOf("A") >= 0) {
					amPm = "AM";
				}
				// XXPM    XPM
				else if (time.indexOf("PM") >= 0 || time.indexOf("P") >= 0) {
					amPm = "PM";
				}
				// XX
				else {
					// We need to look at the hour to guess am or pm. 
					// 6-11 --> AM, 12-5 --> PM
					amPm = "PM";
					if (hour >= 6 && hour <= 11) {
						amPm = "AM";
					}
				}
				hour = convertHour(hour);

				// get minutes
				// XX
				// remove AM, PM, A, or P
				timeSplit[1] = timeSplit[1].replace("A", "");
				timeSplit[1] = timeSplit[1].replace("P", "");
				timeSplit[1] = timeSplit[1].replace("M", "");
				// all what should be left is the number digits
				if (timeSplit[1].length !== 2) {
					return "ERROR";
				}
				// check minutes
				minutes = parseInt(timeSplit[1]);
				if (isNaN(minutes) || minutes < 0 || minutes > 59) {
					return "ERROR";
				}
				// go back to string if no errors
				minutes = timeSplit[1];

				return hour+":"+minutes+amPm;
			}
		}
	};
}]);