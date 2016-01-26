'use strict';

// @CITE: https://scotch.io/tutorials/internationalization-of-angularjs-applications
// @TODO: Remove later - not our code and only a demo of how to change languages
angular.module('sbAngularApp').directive('ngTranslateLanguageSelect', function (localeService) { 

        return {
            restrict: 'A',
            replace: true,
            template: ''+
            '<div class="language-select" ng-if="visible">'+
                '<label>'+
                    '{{"global.LANGUAGE" | translate}}:'+
                    '<select ng-model="currentLocaleDisplayName"'+
                        'ng-options="localesDisplayName for localesDisplayName in localesDisplayNames"'+
                        'ng-change="changeLanguage(currentLocaleDisplayName)">'+
                    '</select>'+
                '</label>'+
            '</div>'+
            '',
            controller: function ($scope) {
                $scope.currentLocaleDisplayName = localeService.getLocaleDisplayName();
                $scope.localesDisplayNames = localeService.getLocalesDisplayNames();
                $scope.visible = $scope.localesDisplayNames &&
                $scope.localesDisplayNames.length > 1;
    
                $scope.changeLanguage = function (locale) {
                    localeService.setLocaleByDisplayName(locale);
                };
            }
        };
    });