// 'use strict';

// describe('Directive: sbUserAuthContainer', function () {
//   var scope, element, iScope;

//   // load the controller's module
//   // issue with angular-translate and unit testing:
//   // SOURCE: http://angular-translate.github.io/docs/#/guide/22_unit-testing-with-angular-translate
//   beforeEach(module('sbAngularApp', function ($provide, $translateProvider) {
   
//     // not loading the locale files
//     $provide.factory('customLoader', function ($q) {
//       return function () {
//         var deferred = $q.defer();
//         deferred.resolve({});
//         return deferred.promise;
//       };
//     });
   
//     $translateProvider.useLoader('customLoader');
//   }));

//   // this is given in karma.conf.js to load our templateUrls from directives
//   beforeEach(module('sbTemplates'));

//   // Initialize the controller and a mock scope
//   beforeEach(inject(function ($rootScope, $compile) {
//     // directive setup
//     scope = $rootScope.$new();
//     element = '<sb-user-auth-container info="{{userAuthContainer}}"></sb-user-auth-container>';
//     scope.userAuthContainer = {};

//     element = $compile(element)(scope);
//     //scope.$digest();
//     iScope = element.isolateScope();
//   }));

//   describe('isValidUsername', function () {
//     it('should return false with bad username', function () {
//       scope.$digest();
//       debugger;
//       scope.isValidUsername();
//       expect(scope.sbRoot.initialLoading).toBe(true);
//     });
//   });
// });