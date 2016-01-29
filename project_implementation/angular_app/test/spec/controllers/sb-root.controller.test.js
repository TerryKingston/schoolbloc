'use strict';

describe('Controller: SbRoot', function () {
  var SbRoot,
      scope;

  // load the controller's module
  beforeEach(module('sbAngularApp'));

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($rootScope, $controller) {
    // controller setup
    scope = $rootScope.$new();

    SbRoot = $controller('SbRoot', {
      $scope: scope
    });
  }));

  it('should test if determineJwtState was called', function () {
    expect(scope.sbRoot.initialLoading).toBe(false);
  });
});