'use strict';

describe('Controller: UserAuthContainer', function () {
  var UserAuthContainer,
      scope,
      sandbox, userAuthService;

  // load the controller's module
  beforeEach(module('sbAngularApp'));

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($rootScope, $controller) {
    // controller setup
    scope = $rootScope.$new();

    UserAuthContainer = $controller('UserAuthContainer', {
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

  describe('isValidUsername', function () {

    it('should test null username', function () {
      scope.userAuthContainer.form.username = null;
      expect(scope.isValidUsername()).toBe(false);
    });

    it('should test empty username', function () {
      scope.userAuthContainer.form.username = "";
      expect(scope.isValidUsername()).toBe(false);
    });

    it('should test too short username', function () {
      scope.userAuthContainer.form.username = "a";
      expect(scope.isValidUsername()).toBe(false);
    });

    it('should test shortest possible username', function () {
      scope.userAuthContainer.form.username = "ab";
      expect(scope.isValidUsername()).toBe(true);
    });

    it('should test proper username', function () {
      scope.userAuthContainer.form.username = "1234abcd";
      expect(scope.isValidUsername()).toBe(true);
    });
  });

  describe('isValidPassword', function () {

    it('should test null password', function () {
      scope.userAuthContainer.form.password = null;
      expect(scope.isValidPassword()).toBe(false);
    });

    it('should test empty password', function () {
      scope.userAuthContainer.form.password = "";
      expect(scope.isValidPassword()).toBe(false);
    });

    it('should test too short password', function () {
      scope.userAuthContainer.form.password = "abcd";
      expect(scope.isValidPassword()).toBe(false);
    });

    it('should test shortest possible password', function () {
      scope.userAuthContainer.form.password = "abcde";
      expect(scope.isValidPassword()).toBe(true);
    });

    it('should test proper password', function () {
      scope.userAuthContainer.form.password = "1234abcd";
      expect(scope.isValidPassword()).toBe(true);
    });
  });

  describe('isValidFullName', function () {

    it('should test null fullName', function () {
      scope.userAuthContainer.form.fullName = null;
      expect(scope.isValidFullName()).toBe(false);
    });

    it('should test empty fullName', function () {
      scope.userAuthContainer.form.fullName = "";
      expect(scope.isValidFullName()).toBe(false);
    });

    it('should test too short fullName', function () {
      scope.userAuthContainer.form.fullName = "a";
      expect(scope.isValidFullName()).toBe(false);
    });

    it('should test shortest possible fullName', function () {
      scope.userAuthContainer.form.fullName = "ab";
      expect(scope.isValidFullName()).toBe(true);
    });

    it('should test proper fullName', function () {
      scope.userAuthContainer.form.fullName = "1234abcd";
      expect(scope.isValidFullName()).toBe(true);
    });
  });

  describe('isValidPasswordRe', function () {

    it('should test null passwordRe not matching password', function () {
      scope.userAuthContainer.form.passwordRe = "aaaa";
      scope.userAuthContainer.form.password = "aaaab";
      expect(scope.isValidPasswordRe()).toBe(false);
    });

    it('should test null passwordRe not matching password', function () {
      scope.userAuthContainer.form.passwordRe = "aaaa";
      scope.userAuthContainer.form.password = "aaaa";
      expect(scope.isValidPasswordRe()).toBe(true);
    });
  });

  describe('switchForm', function () {

    it('should toggle isLoginForm', function () {
      scope.userAuthContainer.form.isLoginForm = true;
      scope.switchForm();
      expect(scope.userAuthContainer.form.isLoginForm).toBe(false);
      scope.switchForm();
      expect(scope.userAuthContainer.form.isLoginForm).toBe(true);
      scope.switchForm();
      expect(scope.userAuthContainer.form.isLoginForm).toBe(false);
    });
  });

  describe('getFormTypeText', function () {
    // unneeded: only translations
  });

  describe('getAuthenticationError', function () {
    // unneeded: only translations
  });

  describe('checkForErrors', function () {
    // unneeded: only translations
  });

  describe('submitForm', function () {

    it('should not login with invalid username', function () {
      sandbox.stub(userAuthService, 'loginUser');

      scope.userAuthContainer.form.isLoginForm = true;
      scope.userAuthContainer.form.username = "a";
      scope.userAuthContainer.form.password = "password";

      scope.submitForm();

      expect(userAuthService.loginUser.calledOnce).toBe(false);
    });

    it('should not login with invalid password', function () {
      sandbox.stub(userAuthService, 'loginUser');

      scope.userAuthContainer.form.isLoginForm = true;
      scope.userAuthContainer.form.username = "username";
      scope.userAuthContainer.form.password = "abcd";

      scope.submitForm();

      expect(userAuthService.loginUser.calledOnce).toBe(false);
    });

    it('should login with valid credentials', inject(function($q) {
      sandbox.stub(userAuthService, 'loginUser', function(){
        var deferred = $q.defer();
        deferred.resolve();
        return deferred.promise;
      });

      scope.userAuthContainer.form.isLoginForm = true;
      scope.userAuthContainer.form.username = "username";
      scope.userAuthContainer.form.password = "password";

      scope.submitForm();

      expect(userAuthService.loginUser.calledOnce).toBe(true);
    }));

    it('should not register with invalid username', function () {
      sandbox.stub(userAuthService, 'loginUser');

      scope.userAuthContainer.form.isLoginForm = false;
      scope.userAuthContainer.form.username = "a";
      scope.userAuthContainer.form.fullName = "my name";
      scope.userAuthContainer.form.password = "password";
      scope.userAuthContainer.form.passwordRe = "password";

      scope.submitForm();

      expect(userAuthService.loginUser.calledOnce).toBe(false);
    });

    it('should not register with invalid fullname', function () {
      sandbox.stub(userAuthService, 'loginUser');

      scope.userAuthContainer.form.isLoginForm = false;
      scope.userAuthContainer.form.username = "username";
      scope.userAuthContainer.form.fullName = "a";
      scope.userAuthContainer.form.password = "password";
      scope.userAuthContainer.form.passwordRe = "password";

      scope.submitForm();

      expect(userAuthService.loginUser.calledOnce).toBe(false);
    });

    it('should not register with invalid password', function () {
      sandbox.stub(userAuthService, 'loginUser');

      scope.userAuthContainer.form.isLoginForm = false;
      scope.userAuthContainer.form.username = "username";
      scope.userAuthContainer.form.fullName = "my name";
      scope.userAuthContainer.form.password = "abcd";
      scope.userAuthContainer.form.passwordRe = "password";

      scope.submitForm();

      expect(userAuthService.loginUser.calledOnce).toBe(false);
    });

    it('should not register with invalid re password', function () {
      sandbox.stub(userAuthService, 'loginUser');

      scope.userAuthContainer.form.isLoginForm = false;
      scope.userAuthContainer.form.username = "username";
      scope.userAuthContainer.form.fullName = "my name";
      scope.userAuthContainer.form.password = "password";
      scope.userAuthContainer.form.passwordRe = "password wrong";

      scope.submitForm();

      expect(userAuthService.loginUser.calledOnce).toBe(false);
    });

    it('should register with valid credentials', inject(function($q) {
      sandbox.stub(userAuthService, 'registerUser', function(){
        var deferred = $q.defer();
        deferred.resolve();
        return deferred.promise;
      });

      scope.userAuthContainer.form.isLoginForm = false;
      scope.userAuthContainer.form.username = "username";
      scope.userAuthContainer.form.fullName = "my name";
      scope.userAuthContainer.form.password = "password";
      scope.userAuthContainer.form.passwordRe = "password";

      scope.submitForm();

      expect(userAuthService.registerUser.calledOnce).toBe(true);
    }));
  });

  describe('resetForm', function () {
    it('should reset form object', function() {
      scope.userAuthContainer.form.username = "bob";
      scope.resetForm();
      expect(scope.userAuthContainer.form.username).toBe(null);
    });
  });
});