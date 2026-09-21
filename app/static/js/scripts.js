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
    document.addEventListener("DOMContentLoaded", async function loadProfile() {
        let token = localStorage.getItem("access_token");//Отримуємо токен
    
        if (!token) {
            console.log("❌ Токен відсутній! Перенаправлення на вхід.");
            window.location.href = "/login"; // Якщо токена немає — перенаправляємо на логін
            return;
        }
        
        console.log("🔧 Токен у заголовку:", "Bearer " + token);

        try {
            //document.cookie = `access_token_cookie=${token}; path=/;`;
            let response = await fetch("/api/profile", {
                method: "GET",
                headers: {
                    "Authorization": "Bearer " + token,  // ✅ Передаємо токен у заголовку
                    "Content-Type": "application/json",
                },
                credentials: "include"  // Додаємо для передачі кукісів
            });
        
    
            let data = await response.json();
            console.log("📝 Відповідь сервера:", data);
    
            if (response.ok) {
                document.getElementById("user-name").innerText = data.name;
                document.getElementById("user-email").innerText = data.email;
                console.log("✅ Профіль завантажено успішно!");
                //document.getElementById("profile-info").innerText = `Привіт, ${data.name}!`;
            } else {
                console.error("❌ Помилка доступу: " + data.msg);
                //alert("Помилка доступу до профілю: " + data.msg);
                window.location.href = "/login"; // Якщо помилка — повертаємо на сторінку входу
            }
        } catch (error) {
            console.error("❌ Помилка отримання профілю:", error);
        }
    });

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
