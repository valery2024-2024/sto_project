document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");

    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        let email = document.getElementById("email").value;
        let password = document.getElementById("password").value;

        try {
            let response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email, password })
            });

            let contentType = response.headers.get("content-type");

            if (contentType && contentType.includes("application/json")) {
                let data = await response.json();

                if (response.ok && data.access_token) {
                    localStorage.setItem("access_token", data.access_token);
                    window.location.href = "/profile";
                } else {
                    alert(data.msg || "Невірні дані!");
                }
            } else {
                const html = await response.text();
                console.error("Сервер повернув HTML:", html);
                alert("Неочікувана відповідь від сервера.");
            }

        } catch (error) {
            console.error("Помилка:", error);
            alert("Не вдалося підключитися до сервера.");
        }
    });
});
