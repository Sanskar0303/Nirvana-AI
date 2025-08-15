document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("generateBtn");
    const input = document.getElementById("textInput");
    const audio = document.getElementById("audioPlayer");
    const status = document.getElementById("status");

    btn.addEventListener("click", async () => {
        const text = input.value.trim();
        if (!text) {
            alert("Please enter some text.");
            return;
        }

        status.innerText = "🔄 Generating audio... Please wait.";
        btn.disabled = true;

        try {
            const response = await fetch("/generate_tts", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ text }),
            });

            const data = await response.json();

            if (response.ok && data.audioUrl) {
                audio.src = data.audioUrl;
                audio.style.display = "block";
                audio.play();
                status.innerText = "✅ Audio ready!";
            } else {
                console.error("TTS Error:", data);
                status.innerText = "❌ Error generating audio.";
            }
        } catch (err) {
            console.error("Fetch error:", err);
            status.innerText = "❌ Failed to connect to server.";
        } finally {
            btn.disabled = false;
        }
    });
});
