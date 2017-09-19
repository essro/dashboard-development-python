/**
 * @brief onClickAccordionControl
 * @description function handles the show/hide animation for the accordion elements (generic)
 */
$('.accordion').on('click', '.accordion-control', function (e) {
    e.preventDefault();
    $(this)
        .next('.accordion-panel')
        .not(':animated')
        .slideToggle(80);
});

/**
 * @brief onClickAccordionControlSummary
 * @description function handles the show/hide animation for the accordion elements (unique to the dashboard)
 */
$('.accordion-summary').on('click', '.accordion-control-summary', function (e) {
    e.preventDefault();
    $(this)
        .next('.accordion-panel-detail')
        .not(':animated')
        .slideToggle(80);
    $(this)
        .find('.show-hide')
        .text(function(i, v){
       return v === 'Show Details' ? 'Hide Details' : 'Show Details'
    });
    $(this)
        .find('.show-hide-srcs')
        .text(function(i, v){
       return v === 'Show Referral Sources' ? 'Hide Referral Sources' : 'Show Referral Sources'
    });
});