/* When modal get displayed, scroll to active item. */
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('rdw-date-selector-modal').addEventListener('shown.bs.modal', function () {
        document.querySelector(".list-group-item.active")?.scrollIntoView({ block: "center" });
    });
});