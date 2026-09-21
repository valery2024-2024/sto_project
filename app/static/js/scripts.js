document.addEventListener('DOMContentLoaded', () => {
    // Випадаюче меню
    const dropdownButton = document.querySelector('.dropdown-button');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownButton && dropdownMenu) {
        dropdownButton.addEventListener('click', (e) => {
            e.preventDefault();
            dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
        });

        document.addEventListener('click', (e) => {
            if (!dropdownButton.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.style.display = 'none';
            }
        });
    }
    // Видалення запису
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function(event) {
            const confirmDelete = confirm("Ви впевнені, що хочете видалити цей запис?");
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });
    // 🔹 Слайдер відгуків
let currentReview = 0;
const reviews = document.querySelectorAll('.review-slide');
const prevButton = document.querySelector('.review-prev');
const nextButton = document.querySelector('.review-next');

function showReview(index) {
    reviews.forEach((review, i) => {
        review.classList.remove("active");
        if (i === index) {
            review.classList.add("active");
        }
    });
}

function nextReview() {
    currentReview = (currentReview + 1) % reviews.length;
    showReview(currentReview);
}

function prevReview() {
    currentReview = (currentReview - 1 + reviews.length) % reviews.length;
    showReview(currentReview);
}

// Автоматичне переключення кожні 5 секунд
if (reviews.length > 0) {
    if (prevButton) {
        prevButton.addEventListener("click", prevReview);
    }

    if (nextButton) {
        nextButton.addEventListener("click", nextReview);
    }

    setInterval(nextReview, 5000);
}
});
