document.addEventListener('DOMContentLoaded', () => {
    const dropdownButton = document.querySelector('.dropdown-button');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    // Показати/сховати меню при кліку
    dropdownButton.addEventListener('click', (e) => {
        e.preventDefault();
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    });

    console.log("Dropdown script is running!");

    console.log("JavaScript підключено і працює!");


    // Закрити меню при кліку поза ним
    document.addEventListener('click', (e) => {
        if (!dropdownButton.contains(e.target) && !dropdownMenu.contains(e.target)) {
            dropdownMenu.style.display = 'none';
            console.log("Меню закрито!");
        }
    });
});
