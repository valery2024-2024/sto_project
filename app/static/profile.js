document.addEventListener("DOMContentLoaded", async () => {
    let token = localStorage.getItem("access_token");

    if (!token) {
        alert("🔒 Ви не авторизовані!");
        window.location.href = "/login";
        return;
    }

    try {
        const res = await fetch("/profile", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await res.json();

        if (res.ok) {
            document.body.innerHTML = `<h2>👋 Вітаємо!</h2><p>Email: ${data.email}</p>`;
        } else {
            alert(data.msg || "Помилка доступу");
            window.location.href = "/login";
        }

    } catch (err) {
        console.error("❌ Помилка профілю:", err);
        alert("Сервер недоступний");
    }
});
