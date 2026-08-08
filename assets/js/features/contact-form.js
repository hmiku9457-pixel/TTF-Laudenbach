export function initContactForm() {
    const contactForm = document.getElementById("contactForm");
    const submitButton = document.getElementById("contactSubmitButton");
    const status = document.getElementById("contactFormStatus");

    if (!contactForm || !submitButton) {
        return;
    }

    const setStatus = (message = "", type = "") => {
        if (!status) {
            return;
        }
        status.textContent = message;
        status.classList.remove("success", "error");
        if (type) {
            status.classList.add(type);
        }
    };

    function resetContactForm() {
        contactForm.reset();
        submitButton.classList.remove("is-sending", "is-success", "is-error");
        submitButton.textContent = "Nachricht senden";
        submitButton.disabled = false;
        setStatus();
    }

    contactForm.addEventListener("submit", async event => {
        event.preventDefault();

        if (submitButton.classList.contains("is-success")) {
            resetContactForm();
            return;
        }

        submitButton.disabled = true;
        submitButton.classList.remove("is-success", "is-error");
        submitButton.classList.add("is-sending");
        submitButton.textContent = "Wird gesendet...";
        setStatus("Die Nachricht wird gesendet.");

        try {
            const response = await fetch(contactForm.action, {
                method: contactForm.method,
                body: new FormData(contactForm),
                headers: { Accept: "application/json" }
            });

            submitButton.classList.remove("is-sending");
            submitButton.disabled = false;

            if (response.ok) {
                submitButton.classList.add("is-success");
                submitButton.textContent = "✓ Gesendet – Weitere Nachricht senden?";
                setStatus("Vielen Dank! Ihre Nachricht wurde erfolgreich gesendet.", "success");
                return;
            }

            submitButton.classList.add("is-error");
            submitButton.textContent = "✗ Fehler – Erneut versuchen?";
            setStatus("Beim Senden ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.", "error");
        } catch (error) {
            console.error("Fehler beim Senden des Kontaktformulars:", error);
            submitButton.classList.remove("is-sending");
            submitButton.classList.add("is-error");
            submitButton.textContent = "✗ Verbindungsfehler – Erneut versuchen?";
            submitButton.disabled = false;
            setStatus("Es konnte keine Verbindung hergestellt werden. Bitte versuchen Sie es erneut.", "error");
        }
    });
}
