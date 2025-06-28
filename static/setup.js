let mediaRecorder;
let audioChunks = [];
let audioBlob = null;

document.getElementById("contextForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const form = e.target;
    const data = {
        guest_name: form.guest_name.value,
        guest_bio: form.guest_bio.value,
        podcast_goal: form.podcast_goal.value,
        podcast_topic: form.podcast_topic.value,
        starter_questions: form.starter_questions.value.split('\n').map(q => q.trim()).filter(q => q)
    };

    const res = await fetch("/setup_context/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const json = await res.json();
    alert(json.message);
});

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.start();
            document.getElementById("status").innerText = "Recording...";
        });
}

function stopRecording() {
    mediaRecorder.stop();
    mediaRecorder.onstop = async () => {
        // audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        audioBlob = new Blob(audioChunks, { type: "audio/webm" });


        const audioURL = URL.createObjectURL(audioBlob);
        const player = document.getElementById("audioPlayer");
        player.src = audioURL;
        player.style.display = "block";

        const formData = new FormData();
        // formData.append("file", audioBlob, "host.wav");
        formData.append("file", audioBlob, "host.webm");


        const res = await fetch("/upload/", {
            method: "POST",
            body: formData
        });

        const json = await res.json();
        document.getElementById("status").innerText = json.message;
    };
}
