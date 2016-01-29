'use strict';

describe('Controller: MainNavBar', function () {
  var MainNavBar,
      scope,
      sandbox, userAuthService;

  // load the controller's module
  beforeEach(module('sbAngularApp'));

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($rootScope, $controller) {
    // controller setup
    scope = $rootScope.$new();

    MainNavBar = $controller('MainNavBar', {
      $scope: scope
    });
  }));

  // Setup stubs
  beforeEach(inject(function ($injector) {
    sandbox = sinon.sandbox.create();
    userAuthService = $injector.get('userAuthService');
  }));

  afterEach(function () {
    sandbox.restore();
  });

  describe('logout', function () {
    it('should test if userAuthService.logoutUser() was called', function () {
      sandbox.stub(userAuthService, 'logoutUser');

      scope.mainNavBar.logout();

      expect(userAuthService.logoutUser.calledOnce).toBe(true);
    });
  });
});