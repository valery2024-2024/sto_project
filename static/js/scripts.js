document.addEventListener('DOMContentLoaded', () => {
    console.log("JavaScript підключено і працює!");

    // Випадаюче меню
    const dropdownButton = document.querySelector('.dropdown-button');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownButton && dropdownMenu) {
        dropdownButton.addEventListener('click', (e) => {
            e.preventDefault();
            dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
            console.log("Меню відкрито!");
        });

        document.addEventListener('click', (e) => {
            if (!dropdownButton.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.style.display = 'none';
                console.log("Меню закрито!");
            }
        });
    } else {
        console.log("Dropdown elements not found!");
    }

    // Видалення запису
    setTimeout(() => {
        const deleteButtons = document.querySelectorAll(".delete-btn");

        if (deleteButtons.length === 0) {
            console.log("❌ Кнопки видалення не знайдені!");
        } else {
            console.log(`✅ Знайдено ${deleteButtons.length} кнопок видалення`);
        }
        
        deleteButtons.forEach(button => {
            button.addEventListener("click", function(event) {
                event.preventDefault();
                const form = this.closest("form");

                if (!form) {
                    console.error("❌ Форма для видалення не знайдена!");
                    return;
                }

                const confirmDelete = confirm("Ви впевнені, що хочете видалити цей запис?");
                if (confirmDelete) {
                    console.log(`🔴 Надсилаємо POST-запит на: ${form.action}`);

                    fetch(form.action, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                    })
                    .then(response => {
                        if (!response.ok) throw new Error(`Помилка: ${response.statusText}`);
                        console.log("✅ Запис успішно видалено");
                        form.closest("tr").remove(); // Видаляємо запис без перезавантаження
                    })
                    .catch(error => console.error("❌ Помилка під час видалення:", error));
                } else {
                    console.log("❌ Видалення скасовано");
                }
            });
        });
        
    }, 500);
    // 🔹 Слайдер відгуків
let currentReview = 0;
const reviews = document.querySelectorAll('.review-slide');

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
setInterval(nextReview, 5000);


});
