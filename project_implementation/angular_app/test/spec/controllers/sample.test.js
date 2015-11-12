'use strict';

describe('Controller: SampleController', function () {
  var SampleController;
  var $scope;

  // load the controller's module
  beforeEach(module('sbAngularApp'));

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($rootScope, $controller) {
    $scope = $rootScope.$new();
    SampleController = $controller('SampleController', {
      $scope: $scope
    });
  }));

  // it('should (then some test message)', function () {
  //   expect(SampleController.something.length).toBe(3);
  // });

  // it('should (then some test message)', function () {
  //   expect($scope.sampleController.something).toBe(false);
  // });
});