
(() => {
    let mediaRecorder;
    let audioChunks = [];
    let audioBlob = null;

    window.startRecording = function () {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                audioChunks = [];
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                mediaRecorder.start();
                document.getElementById("status").innerText = "Recording...";
            });
    }

    window.stopRecording = function () {
        mediaRecorder.stop();
        mediaRecorder.onstop = () => {
            audioBlob = new Blob(audioChunks, { type: "audio/wav" });

            const audioURL = URL.createObjectURL(audioBlob);
            const player = document.getElementById("audioPlayer");
            player.src = audioURL;
            player.style.display = "block";

            document.getElementById("saveBtn").style.display = "inline-block";
            document.getElementById("discardBtn").style.display = "inline-block";
            document.getElementById("status").innerText = "Preview your recording.";
        };
    }

    window.discardRecording = function () {
        audioBlob = null;
        document.getElementById("audioPlayer").style.display = "none";
        document.getElementById("saveBtn").style.display = "none";
        document.getElementById("discardBtn").style.display = "none";
        document.getElementById("status").innerText = "Recording discarded. Please re-record.";
    }

    window.uploadRecording = async function () {
        const form = document.getElementById("uploadForm");
        const formData = new FormData(form);
        formData.append("file", audioBlob, "recording.wav");

        const res = await fetch("/upload/", {
            method: "POST",
            body: formData
        });

        const json = await res.json();
        document.getElementById("status").innerText = res.ok
            ? json.message
            : "⚠️ " + json.message;

        document.getElementById("audioPlayer").style.display = "none";
        document.getElementById("saveBtn").style.display = "none";
        document.getElementById("discardBtn").style.display = "none";
        form.reset();
    }

    window.stopRecordingTest = async function () {
        mediaRecorder.stop();
        mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunks, { type: "audio/wav" });
            const formData = new FormData();
            formData.append("file", blob, "test.wav");

            const res = await fetch("/identify/", {
                method: "POST",
                body: formData
            });

            const json = await res.json();
            document.getElementById("result").innerText =
                json.identified_speaker
                    ? `Detected: ${json.identified_speaker} (similarity: ${json.similarity})`
                    : "No match found.";
        };
    }
})();
