/**
 * app.js — SenseArrival browser JS
 *
 * Responsibilities:
 *  1. Mic capture → POST /voice/transcribe (with text-mode fallback)
 *  2. ElevenLabs TTS audio playback for role cards
 *  3. Mic permission guard with visible "Text mode" banner
 */

// ---------------------------------------------------------------------------
// TTS playback
// ---------------------------------------------------------------------------

/**
 * Called by the "Play" button on each role card.
 * Fetches the TTS audio stream and plays it inline.
 */
async function playAudio(button) {
  const cardId = button.closest('.role-card').querySelector('h3').textContent
    .toLowerCase().replace(/\s+/g, '-');
  try {
    const resp = await fetch(`/voice/tts/${cardId}`);
    if (!resp.ok) { console.warn('TTS fetch failed', resp.status); return; }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
    button.textContent = '⏸ Playing';
    audio.onended = () => {
      button.textContent = '▶ Play';
      URL.revokeObjectURL(url);
    };
  } catch (err) {
    console.error('TTS playback error', err);
  }
}

// ---------------------------------------------------------------------------
// Mic capture with text-mode fallback
// ---------------------------------------------------------------------------

let micStream = null;
let mediaRecorder = null;
let audioChunks = [];

async function initMic() {
  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.log('Mic permission granted');
    document.getElementById('mic-mode-banner')?.remove();
  } catch (err) {
    console.warn('Mic permission denied or unavailable:', err);
    showTextModeBanner();
  }
}

function showTextModeBanner() {
  const existing = document.getElementById('mic-mode-banner');
  if (existing) return;
  const banner = document.createElement('div');
  banner.id = 'mic-mode-banner';
  banner.style.cssText = 'background:#b8860b;color:white;padding:0.4rem 1rem;font-size:0.85rem;text-align:center;';
  banner.textContent = 'Microphone unavailable — Text mode active. Use the text area below.';
  document.body.prepend(banner);
}

function startRecording() {
  if (!micStream) { showTextModeBanner(); return; }
  audioChunks = [];
  mediaRecorder = new MediaRecorder(micStream);
  mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
  mediaRecorder.onstop = submitAudio;
  mediaRecorder.start();
  document.getElementById('mic-record-btn')?.setAttribute('data-recording', 'true');
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    document.getElementById('mic-record-btn')?.removeAttribute('data-recording');
  }
}

async function submitAudio() {
  const blob = new Blob(audioChunks, { type: 'audio/webm' });
  const form = new FormData();
  form.append('audio', blob, 'recording.webm');
  form.append('source', 'mic');
  try {
    const resp = await fetch('/voice/transcribe', { method: 'POST', body: form });
    const data = await resp.json();
    const resultEl = document.getElementById('staff-note-result');
    if (resultEl) {
      resultEl.innerHTML = `<p><strong>Transcript:</strong> ${data.transcript}</p>`;
    }
  } catch (err) {
    console.error('STT submission error', err);
  }
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  // Attempt mic access on load; degrade gracefully
  initMic();

  // Wire mic record button if present
  const micBtn = document.getElementById('mic-record-btn');
  if (micBtn) {
    micBtn.addEventListener('mousedown', startRecording);
    micBtn.addEventListener('mouseup', stopRecording);
    micBtn.addEventListener('touchstart', startRecording);
    micBtn.addEventListener('touchend', stopRecording);
  }
});
