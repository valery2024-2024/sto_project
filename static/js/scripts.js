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
    document.addEventListener('DOMContentLoaded', () => {
        const dropdownButtons = document.querySelectorAll('.dropdown-button');
    
        dropdownButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const menu = button.nextElementSibling;
                
                // Закриваємо всі відкриті меню
                document.querySelectorAll('.dropdown-menu').forEach(dropdown => {
                    if (dropdown !== menu) {
                        dropdown.style.display = 'none';
                    }
                });
    
                // Перемикаємо стан поточного меню
                menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
            });
        });
    
        // Закриваємо меню при кліку за межами
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    menu.style.display = 'none';
                });
            }
        });
    });

    document.getElementById("login-form").addEventListener("submit", async function(event) {
        event.preventDefault();
    
        let email = document.getElementById("email").value;
        let password = document.getElementById("password").value;
    
        let response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email: email, password: password })
        });
    
        let data = await response.json();
        
        if (response.ok) {
            localStorage.setItem("access_token", data.access_token); // Зберігаємо токен
            window.location.href = "/profile"; // Перенаправляємо на профіль
        } else {
            alert("Помилка входу: " + data.message);
        }
    });
    
    document.addEventListener("DOMContentLoaded", async function() {
        let token = localStorage.getItem("access_token");//Отримуємо токен
    
        if (!token) {
            window.location.href = "/login"; // Якщо токена немає — перенаправляємо на логін
        }
    
        let response = await fetch("/profile", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token // Додаємо токен у заголовок
            }
        });
    
        let data = await response.json();
    
        if (response.ok) {
            document.getElementById("profile-info").innerText = `Привіт, ${data.name}!`;
        } else {
            alert("Помилка доступу до профілю: " + data.msg);
            window.location.href = "/login"; // Якщо помилка — повертаємо на сторінку входу
        }
    });

    document.getElementById("logout").addEventListener("click", function(event) {
        event.preventDefault(); // Зупиняємо стандартний перехід по посиланню
        localStorage.removeItem("access_token"); // Видаляємо токен
        window.location.href = "/login"; // Переходимо на сторінку входу
    });
    
    
    

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
