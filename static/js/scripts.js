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

    // Видалення запису (з чекінгом завантажених кнопок)
    setTimeout(() => {
        const deleteButtons = document.querySelectorAll(".delete-btn");

        if (deleteButtons.length === 0) {
            console.log("❌ Кнопки видалення не знайдені!");
        } else {
            console.log(`✅ Знайдено ${deleteButtons.length} кнопок видалення`);
        }

        deleteButtons.forEach(button => {
            button.addEventListener("click", function(event) {
                event.preventDefault(); // Запобігає миттєвому видаленню
                const confirmDelete = confirm("Ви впевнені, що хочете видалити цей запис?");
                if (confirmDelete) {
                    console.log(`🔴 Видаляємо запис з ID: ${this.closest("form").action}`);
                    this.closest("form").submit(); // Виконує видалення, якщо підтверджено
                } else {
                    console.log("❌ Видалення скасовано");
                }
            });
        });
    }, 500); // Додаємо невелику затримку для перевірки кнопок
});
