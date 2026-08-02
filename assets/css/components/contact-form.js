export function initContactForm() {
    const contactForm = document.getElementById("contactForm");
    const submitButton = document.getElementById("contactSubmitButton");

    if (!contactForm || !submitButton) {
        return;
    }

    function isMobileView() {
        return window.matchMedia("(max-width: 768px)").matches;
    }

    function resetContactForm() {
        contactForm.reset();
        submitButton.classList.remove("is-sending", "is-success", "is-error");
        submitButton.textContent = "Nachricht senden";
        submitButton.disabled = false;
    }

    contactForm.addEventListener("submit", async event => {
        event.preventDefault();

        if (submitButton.classList.contains("is-success")) {
            resetContactForm();
            return;
        }

        if (submitButton.classList.contains("is-error")) {
            submitButton.classList.remove("is-error");
            submitButton.textContent = "Nachricht senden";
        }

        const formData = new FormData(contactForm);
        submitButton.disabled = true;
        submitButton.classList.remove("is-success", "is-error");
        submitButton.classList.add("is-sending");
        submitButton.textContent = "Wird gesendet...";

        try {
            const response = await fetch(contactForm.action, {
                method: contactForm.method,
                body: formData,
                headers: { Accept: "application/json" }
            });

            submitButton.classList.remove("is-sending");

            if (response.ok) {
                if (isMobileView()) {
                    alert("Vielen Dank! Ihre Nachricht wurde erfolgreich gesendet.");
                    resetContactForm();
                } else {
                    submitButton.classList.add("is-success");
                    submitButton.textContent = "✓ Gesendet – Weitere Nachricht senden?";
                    submitButton.disabled = false;
                }
            } else if (isMobileView()) {
                alert("Beim Senden ist ein Fehler aufgetreten.");
                submitButton.textContent = "Nachricht senden";
                submitButton.disabled = false;
            } else {
                submitButton.classList.add("is-error");
                submitButton.textContent = "✗ Fehler – Erneut versuchen?";
                submitButton.disabled = false;
            }
        } catch (error) {
            console.error("Fehler beim Senden des Kontaktformulars:", error);
            submitButton.classList.remove("is-sending");

            if (isMobileView()) {
                alert("Es konnte keine Verbindung hergestellt werden.");
                submitButton.textContent = "Nachricht senden";
                submitButton.disabled = false;
            } else {
                submitButton.classList.add("is-error");
                submitButton.textContent = "✗ Verbindungsfehler – Erneut versuchen?";
                submitButton.disabled = false;
            }
        }
    });
}
