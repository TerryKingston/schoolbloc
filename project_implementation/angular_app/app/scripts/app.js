'use strict';

/**
 * @ngdoc overview
 * @name sbAngularApp
 * @description
 * # sbAngularApp
 *
 * Main module of the application.
 */
angular.module('sbAngularApp', [
		'ngAnimate',
	    'ngCookies',
	    'ngResource',
	    'ngRoute',
	    'ngSanitize',
	    'ngTouch',
  		'pascalprecht.translate',
        'angularFileUpload'
]).constant('LOCALES', {
	'locales': {
        'xx_XX': 'Jibberish',
        'en_US': 'English'
    },
    'preferredLocale': 'en_US'  
}).config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'index.html',
            // default controller
            controller: 'SbRoot'
        })
        // .when('/login', {
        //     templateUrl: 'routes/login/index.html',
        //     controller: 'UserLogin'
        // })
        .otherwise({
            redirectTo: '/'
        });
}]).config(['$translateProvider', function ($translateProvider) {
	$translateProvider.useMissingTranslationHandlerLog();
    $translateProvider.useSanitizeValueStrategy('sanitize');
    $translateProvider.useStaticFilesLoader({
        prefix: 'locales/locale-',
        suffix: '.json'
    });
    $translateProvider.preferredLanguage('en_US');
    $translateProvider.useLocalStorage();
}]).config(['$locationProvider', function ($locationProvider) {
    // the default mode is using a "#" before the URL when using $location.path().  We don't want it to do that
    //$locationProvider.html5Mode(true);
}]);
