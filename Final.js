// Initialize Bootstrap carousel
document.addEventListener("DOMContentLoaded", function () {
    const myCarouselElement = document.querySelector(
        "#carouselExampleSlidesOnly"
    );

    if (myCarouselElement) {
        const carousel = new bootstrap.Carousel(myCarouselElement, {
            interval: 2000, // Slide change every 2 seconds
            pause: "hover", // Pauses carousel when hovered
            wrap: true, // Loops back to the first slide
            touch: true, // Enables touch gestures for mobile
        });
    }
});
// JavaScript to add questions to table
document
    .getElementById("questionForm")
    .addEventListener("submit", function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value;
        const question = document.getElementById("question").value;

        const table = document.getElementById("questionsTable");

        const row = table.insertRow();
        const cell1 = row.insertCell(0);
        const cell2 = row.insertCell(1);

        cell1.textContent = username;
        cell2.textContent = question;

        document.getElementById("questionForm").reset();
    });

function rateProduct(rating) {
    // Reset all stars
    var stars = document.querySelectorAll(".fa-star");
    stars.forEach((star, index) => {
        star.classList.remove("checked");
        if (index < rating) {
            star.classList.add("checked");
        }
    });

    // Display feedback with emoji
    var feedbackText = "";
    var emoji = "";
    switch (rating) {
        case 1:
            feedbackText = "Feeling Ok";
            emoji = "😐";
            break;
        case 2:
            feedbackText = "Good";
            emoji = "🙂";
            break;
        case 3:
            feedbackText = "Below Average";
            emoji = "😕";
            break;
        case 4:
            feedbackText = "Average";
            emoji = "😊";
            break;
        case 5:
            feedbackText = "Super!";
            emoji = "😃";
            break;
    }
    document.getElementById("feedback").innerHTML = feedbackText + " " + emoji;
}
