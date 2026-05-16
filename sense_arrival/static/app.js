/**
 * app.js — SenseArrival browser JS
 *
 * BL-005 Voice Layer:
 *  1. TTS playback: "Play Briefing" button on each role card fetches /voice/tts/{card_id}
 *  2. Typed-text observation: textarea → POST /voice/transcribe (source=text) → HTMX OOB swap
 *  3. Mic capture → POST /voice/transcribe (source=mic) with text-mode fallback (P1)
 *  4. Mic permission guard: shows visible "Text mode" banner if mic unavailable
 */

// ---------------------------------------------------------------------------
// TTS playback (TREQ-009 / US-005)
// ---------------------------------------------------------------------------

/**
 * Called by the "Play" button on each role card.
 * Fetches the TTS audio stream for the card's CURRENT briefing (US-005).
 *
 * Extracts the card ID from the closest .role-card's h3 text.
 * Strips any badge text (e.g. "Updated", "Observation noted") before slugifying.
 */
async function playAudio(button) {
  const roleCard = button.closest('.role-card');
  if (!roleCard) {
    console.warn('playAudio: could not find parent .role-card');
    return;
  }

  // Get h3 text node content only (ignore child element text like badges)
  const h3 = roleCard.querySelector('h3');
  let roleName = '';
  if (h3) {
    // Walk text nodes only — ignore badge spans
    for (const node of h3.childNodes) {
      if (node.nodeType === Node.TEXT_NODE) {
        roleName += node.textContent;
      }
    }
    roleName = roleName.trim();
  }

  // Slugify: lowercase, spaces → hyphens, strip non-alphanumeric except hyphens
  const cardId = roleName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z-]/g, '');
  if (!cardId) {
    console.warn('playAudio: could not determine card ID from h3 text:', h3?.textContent);
    return;
  }

  // Update button state immediately
  const originalText = button.textContent;
  button.textContent = '⏳ Loading…';
  button.disabled = true;

  try {
    const resp = await fetch(`/voice/tts/${cardId}`);
    if (!resp.ok) {
      console.warn('TTS fetch failed', resp.status, cardId);
      button.textContent = '⚠ Error';
      setTimeout(() => { button.textContent = originalText; button.disabled = false; }, 2000);
      return;
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);

    button.textContent = '⏸ Playing…';
    await audio.play();

    audio.onended = () => {
      button.textContent = originalText;
      button.disabled = false;
      URL.revokeObjectURL(url);
    };
    audio.onerror = (err) => {
      console.error('Audio playback error', err);
      button.textContent = originalText;
      button.disabled = false;
      URL.revokeObjectURL(url);
    };
  } catch (err) {
    console.error('TTS playback error', err);
    button.textContent = originalText;
    button.disabled = false;
  }
}

// ---------------------------------------------------------------------------
// Mic capture with text-mode fallback (TREQ-010 / ADR-001)
// ---------------------------------------------------------------------------

let micStream = null;
let mediaRecorder = null;
let audioChunks = [];

/**
 * Request mic permission on page load.
 * If denied or unavailable, show the "Text mode" banner (ADR-001 guard).
 * Must never fail silently.
 */
async function initMic() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    console.warn('getUserMedia not supported in this browser');
    showTextModeBanner('Microphone not supported in this browser.');
    return;
  }
  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.info('SenseArrival: mic permission granted');
    // Show mic button if it's present
    const micSection = document.getElementById('mic-capture-section');
    if (micSection) micSection.style.display = 'block';
    // Remove banner if it was shown
    document.getElementById('mic-mode-banner')?.remove();
  } catch (err) {
    console.warn('SenseArrival: mic permission denied or unavailable:', err.name, err.message);
    showTextModeBanner();
  }
}

function showTextModeBanner(reason) {
  const existing = document.getElementById('mic-mode-banner');
  if (existing) return; // Already shown
  const banner = document.createElement('div');
  banner.id = 'mic-mode-banner';
  banner.className = 'text-mode-banner';
  banner.textContent = reason
    || 'Microphone unavailable — Text mode active. Use the text area below to submit observations.';
  // Insert after the offline banner (or at top of body)
  const offlineBanner = document.querySelector('.offline-banner');
  if (offlineBanner) {
    offlineBanner.after(banner);
  } else {
    document.body.prepend(banner);
  }
}

function startRecording() {
  if (!micStream) {
    showTextModeBanner();
    return;
  }
  audioChunks = [];
  const mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg';
  mediaRecorder = new MediaRecorder(micStream, { mimeType });
  mediaRecorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) audioChunks.push(e.data);
  };
  mediaRecorder.onstop = submitAudio;
  mediaRecorder.start(100); // Collect in 100ms chunks for reliability
  const btn = document.getElementById('mic-record-btn');
  if (btn) {
    btn.textContent = '⏹ Stop Recording';
    btn.setAttribute('data-recording', 'true');
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  const btn = document.getElementById('mic-record-btn');
  if (btn) {
    btn.textContent = '🎤 Record Observation';
    btn.removeAttribute('data-recording');
  }
}

async function submitAudio() {
  if (!audioChunks.length) {
    console.warn('submitAudio: no audio chunks captured');
    return;
  }
  const mimeType = audioChunks[0]?.type || 'audio/webm';
  const blob = new Blob(audioChunks, { type: mimeType });
  const form = new FormData();
  form.append('audio', blob, 'recording.webm');
  form.append('source', 'mic');

  const resultEl = document.getElementById('staff-note-result');
  if (resultEl) resultEl.innerHTML = '<p class="obs-loading">Transcribing…</p>';

  try {
    const resp = await fetch('/voice/transcribe', { method: 'POST', body: form });
    const html = await resp.text();
    // The response is HTMX HTML — parse it for the inline part and OOB swap
    if (resp.ok) {
      _applyTranscribeResponse(html, resultEl);
    } else {
      if (resultEl) resultEl.innerHTML = '<p class="observation-error">Transcription failed.</p>';
    }
  } catch (err) {
    console.error('STT submission error', err);
    if (resultEl) resultEl.innerHTML = '<p class="observation-error">Submission failed.</p>';
  }
}

/**
 * Apply the transcribe response HTML:
 * - The OOB swap div (hx-swap-oob) is processed by HTMX automatically when
 *   the response comes via htmx.ajax() or an HTMX-wired form.
 * - For the JS-direct fetch path (mic), we manually apply the OOB swap here.
 */
function _applyTranscribeResponse(html, inlineTarget) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');

  // Extract OOB elements and apply them
  const oobEls = doc.querySelectorAll('[hx-swap-oob]');
  oobEls.forEach(el => {
    const oobVal = el.getAttribute('hx-swap-oob');
    // Parse "innerHTML:#role-cards" style
    const match = oobVal.match(/innerHTML:(.+)/);
    if (match) {
      const targetSelector = match[1].trim();
      const target = document.querySelector(targetSelector);
      if (target) {
        target.innerHTML = el.innerHTML;
      }
    }
    el.remove();
  });

  // The remaining HTML is the inline feedback
  if (inlineTarget) {
    inlineTarget.innerHTML = doc.body.innerHTML;
  }
}

// ---------------------------------------------------------------------------
// HTMX after-swap hook: re-initialise play buttons after OOB role card swap
// ---------------------------------------------------------------------------

document.addEventListener('htmx:afterSwap', function(evt) {
  // Nothing extra needed — play buttons use onclick="playAudio(this)" which
  // works on dynamically inserted elements without re-wiring.
  console.debug('SenseArrival: HTMX swap completed', evt.detail?.target?.id);
});

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  // Attempt mic access on load; degrade gracefully to text mode
  initMic();

  // Wire mic record button if present (P1 path)
  const micBtn = document.getElementById('mic-record-btn');
  if (micBtn) {
    micBtn.addEventListener('click', () => {
      if (micBtn.getAttribute('data-recording')) {
        stopRecording();
      } else {
        startRecording();
      }
    });
  }
});
