angular.
module('App')
    .controller('ReadlistController', function($scope) {
        $scope.documents = [{
                id: "abc",
                title: "LinkedIn goes IPO",
                date: Date.now()
            }, {
                id: "abc",
                title: "LinkedIn goes IPO",
                date: Date.now()
            },

            {
                id: "abc",
                title: "LinkedIn goes IPO",
                date: Date.now()
            },

            {
                id: "abc",
                title: "LinkedIn goes IPO",
                date: Date.now()
            },

            {
                id: "abc",
                title: "LinkedIn goes IPO",
                date: Date.now()
            }
        ];
    });
