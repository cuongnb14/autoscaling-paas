'use strict';

var modal = angular.module('ABModal');

modal.controller('ModalController', function ($scope) {
    var mc = this;
    mc.showModal = false;
    mc.showModal = function(name){
        $('#'+name).modal('show')
    };
  });

modal.directive('modal', function () {
    return {
      template: '<div class="modal fade" tabindex="-1" role="dialog">' +
          '<div class="modal-dialog">' +
            '<div class="modal-content">' +
              '<div class="modal-header">' +
                '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
                '<h4 class="modal-title">{{ title }}</h4>' +
              '</div>' +
              '<div class="modal-body" ng-transclude></div>' +
            '</div>' +
          '</div>' +
        '</div>',
      restrict: 'E',
      transclude: true,
      replace:true,
      scope:true,
      link: function postLink(scope, element, attrs) {
        scope.title = attrs.title;
      }
    };
  });


angular.module('Database')

.controller('GetDatabasesController',
    ['$scope', '$rootScope', 'RESTfulService',
    function ($scope, $rootScope, RESTfulService) {
      var gds = this;

        gds.init = function () {
            RESTfulService.getDatabases(function(response) {
                if(response.status != "error") {
                    gds.databases = response;
                } else {
                    gds.databases = null;
                }
            });
        }

        gds.updatePassword = function (database) {
          RESTfulService.updatePassword(database.id,gds.new_password[database.id], function(response) {
              toastr[response.status](response.message)
              if(response.status == "success") {
                  gds.init();
              }
          });
        };

        gds.addDatabase = function (database) {

          RESTfulService.addDatabase(gds.root_password, function(response) {
              toastr[response.status](response.message)
              if(response.status == "success") {
                  gds.init();
              }
          });
        };

        gds.deleteDatabase = function (database_id) {

          RESTfulService.deleteDatabase(database_id, function(response) {
              toastr[response.status](response.message)
              if(response.status == "success") {
                  gds.init();
              }
          });
        };

        gds.init();

    }])

.controller('GetDatabaseController',
    ['$scope', '$rootScope', 'RESTfulService',
    function ($scope, $rootScope, RESTfulService) {
      var gd = this;

        gd.init = RESTfulService.getDatabases(function(response) {
            if(response.status != "error") {
                gd.database = response;
            } else {
                gd.database = null;
            }
        });

        gd.init()

    }])

.controller('SetDatabaseController',
    ['$scope', '$rootScope', 'RESTfulService',
    function ($scope, $rootScope, RESTfulService) {
      var sd = this;

      sd.addDatabase = function() {
        RESTfulService.addDatabase(sd.database, function(response) {
              toastr[response.status](response.message);
        });
      }






    }]);
