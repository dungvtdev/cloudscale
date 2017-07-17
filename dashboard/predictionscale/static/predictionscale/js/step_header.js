$(document).ready(function () {
    applyIndex(step_index)

    function applyIndex(index) {
        var navListItems = $('div.setup-panel div a');

        navListItems.click(function (e) {
            e.preventDefault();
        })

        navListItems.removeClass('btn-primary').addClass('btn-default')

        $(navListItems.get(index-1)).addClass('btn-primary')
    }
});


