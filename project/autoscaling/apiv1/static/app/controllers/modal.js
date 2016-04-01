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
