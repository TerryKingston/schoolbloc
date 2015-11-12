'use strict';

// @TODO: modify later to make your own
// @CITE: https://scotch.io/tutorials/internationalization-of-angularjs-applications
angular.module('sbAngularApp').service('localeService', function ($translate, LOCALES, $rootScope) {
    var locales = LOCALES.locales;

    // locales and locales display names
    var _LOCALES = Object.keys(locales);
    if (!_LOCALES || _LOCALES.length === 0) {
      console.error('There are no locales provided');
    }
    var _LOCALES_DISPLAY_NAMES = [];
    _LOCALES.forEach(function (locale) {
      _LOCALES_DISPLAY_NAMES.push(locales[locale]);
    });
    
    // STORING CURRENT LOCALE
    var currentLocale = $translate.proposedLanguage();// because of async loading
    
    // METHODS
    var checkLocaleIsValid = function (locale) {
      return _LOCALES.indexOf(locale) !== -1;
    };
    
    var setLocale = function (locale) {
      if (!checkLocaleIsValid(locale)) {
        console.error('Locale name "' + locale + '" is invalid');
        return;
      }
      currentLocale = locale;// updating current locale
    
      // asking angular-translate to load and apply proper translations
      $translate.use(locale);
    };
    
    // EVENTS
    // on successful applying translations by angular-translate
    $rootScope.$on('$translateChangeSuccess', function (event, data) {
      document.documentElement.setAttribute('lang', data.language);// sets "lang" attribute to html
    });
    
    return {
      getLocaleDisplayName: function () {
        return locales[currentLocale];
      },
      setLocaleByDisplayName: function (localeDisplayName) {
        setLocale(
          _LOCALES[
            _LOCALES_DISPLAY_NAMES.indexOf(localeDisplayName)// get locale index
            ]
        );
      },
      getLocalesDisplayNames: function () {
        return _LOCALES_DISPLAY_NAMES;
      }
    };
});