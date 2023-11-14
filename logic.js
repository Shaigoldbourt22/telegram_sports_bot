document.addEventListener('DOMContentLoaded', function() {  // wait for the website to load before executing function
    // get the html elements
    var howToUseHeading = document.getElementById('how-to-use-heading');
    var howToUseContent = document.getElementById('how-to-use-content');
    var showHowToUseBtn = document.getElementById('show-how-to-use-btn');

    showHowToUseBtn.addEventListener('click', function() { // press on the button to show/hide the info
        howToUseHeading.classList.toggle('hidden');
        howToUseContent.classList.toggle('hidden');
    });
});
