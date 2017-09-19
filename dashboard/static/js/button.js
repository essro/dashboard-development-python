/**
 * @brief clickOnDashboardMenu
 * @description function controls the show/hide properties of the Dashboard Menu
 */

$('#dashboard-menu-btn').on('click', function () {
    $('#dashboard-navbar').toggle();
});

/**
 * @brief clickOnDashboardSettings
 * @description function controls the show/hide properties of the Settings panel
 */

$('#dashboard-settings-btn').on('click', function () {
    $('#dashboard-prefs').toggle();
});