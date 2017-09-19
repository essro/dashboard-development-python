/**
 * @brief onReadyDocument
 * @description function initializes the text of the show/hide links
 */
$(document).ready(function() {
    $('.show-hide').text("Show Details");
    $('.show-hide-srcs').text("Show Referral Sources");
});

/**
 * @brief onClickActionDetail
 * @description function controls the action (recommendation) dialog show/hide
 */
$('.action-detail').on('click', function() {
    $(this)
        .parent()
        .parent()
        .next('.ui-dialog').dialog(
        {
            resizable: false,
            height: "auto",
            width: 500,
            modal: true,
            position: {
                my: 'center',
                at: 'center'
            }
        }
    );
});