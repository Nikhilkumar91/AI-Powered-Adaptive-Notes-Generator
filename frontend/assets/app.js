const state = {
  file: null,
  level: 'intermediate',
  transcription: '',
  rawTranscription: '',
  transcriptionQuality: '',
  warnings: [],
  topic: '',
  notes: null,
  diagrams: [],
  quiz: [],
  sessionId: null,
};

const mediaInput = document.getElementById('mediaInput');
const fileMeta = document.getElementById('fileMeta');
const processBtn = document.getElementById('processBtn');
const feedback = document.getElementById('feedback');
const previewBtn = document.getElementById('previewBtn');
const pdfBtn = document.getElementById('pdfBtn');
const docxBtn = document.getElementById('docxBtn');
const previewDialog = document.getElementById('previewDialog');
const previewContent = document.getElementById('previewContent');
const submitQuizBtn = document.getElementById('submitQuizBtn');
const quizList = document.getElementById('quizList');
const historyList = document.getElementById('historyList');
const whisperStatus = document.getElementById('whisperStatus');
const mongoStatus = document.getElementById('mongoStatus');
const heroCard = document.querySelector('.hero-card');
const loginShell = document.getElementById('loginShell');
const dashboardShell = document.getElementById('dashboardShell');
const loginForm = document.getElementById('loginForm');
const loginFeedback = document.getElementById('loginFeedback');
const logoutBtn = document.getElementById('logoutBtn');
const TOKEN_KEY = 'adaptive-notes-token';
const TOKEN_STORAGE_KEY = 'adaptive-notes-token-storage';
const USER_KEY = 'adaptive-notes-user';
const rememberMeInput = document.getElementById('rememberMe');
const togglePasswordBtn = document.getElementById('togglePasswordBtn');
const loginSubmitBtn = document.getElementById('loginSubmitBtn');
const tabSignup = document.getElementById('tabSignup');
const tabLogin = document.getElementById('tabLogin');
const footerToggle = document.getElementById('footerToggle');
const nameField = document.getElementById('nameField');
const confirmField = document.getElementById('confirmField');
const signupName = document.getElementById('signupName');
const signupConfirm = document.getElementById('signupConfirm');
const navUser = document.getElementById('navUser');
const overviewUser = document.getElementById('overviewUser');
const overviewSessions = document.getElementById('overviewSessions');
const overviewLastTopic = document.getElementById('overviewLastTopic');
const overviewSystem = document.getElementById('overviewSystem');

loginForm.addEventListener('submit', (event) => {
  event.preventDefault();
  submitAuth().catch(() => {});
});

logoutBtn.addEventListener('click', () => {
  clearToken();
  clearUser();
  showLogin();
  window.history.replaceState({}, '', '/login');
});

togglePasswordBtn?.addEventListener('click', () => {
  const passwordInput = document.getElementById('loginPassword');
  const isPassword = passwordInput.type === 'password';
  passwordInput.type = isPassword ? 'text' : 'password';
  togglePasswordBtn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
});

tabSignup?.addEventListener('click', () => setAuthMode('signup'));
tabLogin?.addEventListener('click', () => setAuthMode('login'));
footerToggle?.addEventListener('click', () => {
  const current = loginForm?.dataset.mode || 'signup';
  setAuthMode(current === 'signup' ? 'login' : 'signup');
});

mediaInput.addEventListener('change', (event) => {
  state.file = event.target.files[0] || null;
  state.transcription = '';
  state.rawTranscription = '';
  state.transcriptionQuality = '';
  state.warnings = [];
  state.topic = '';
  state.notes = null;
  state.diagrams = [];
  state.quiz = [];
  state.sessionId = null;
  fileMeta.textContent = state.file
    ? `${state.file.name} (${(state.file.size / 1024 / 1024).toFixed(2)} MB)`
    : 'No file selected yet';
  setFeedback('Ready to process.');
});

document.getElementById('levelGrid').addEventListener('click', (event) => {
  const button = event.target.closest('[data-level]');
  if (!button) return;
  state.level = button.dataset.level;
  document.querySelectorAll('.level-card').forEach((card) => card.classList.remove('active'));
  button.classList.add('active');
});

processBtn.addEventListener('click', async () => {
  if (!state.file) {
    setFeedback('Choose a file first.', true);
    return;
  }
  processBtn.disabled = true;
  processBtn.textContent = 'Processing...';
  setFeedback('Uploading file and generating notes...');
  try {
    const formData = new FormData();
    formData.append('audio', state.file);
    const transcriptionPayload = await apiFetch('/api/transcribe-audio', {
      method: 'POST',
      body: formData,
    });

    state.transcription = transcriptionPayload.transcription;
    state.rawTranscription = transcriptionPayload.raw_transcription || transcriptionPayload.transcription;
    state.transcriptionQuality = transcriptionPayload.transcription_quality || '';
    state.warnings = transcriptionPayload.warnings || [];
    state.topic = transcriptionPayload.topic;
    renderTranscription();

    const notesPayload = await apiFetch('/api/generate-notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: state.topic,
        transcription: state.transcription,
        level: state.level,
        filename: state.file.name,
      }),
    });

    state.notes = notesPayload.notes;
    state.diagrams = notesPayload.diagrams || [];
    state.quiz = notesPayload.quiz || [];
    state.sessionId = notesPayload.session_id;
    state.topic = state.notes.topic || state.topic;
    renderTranscription();
    renderNotes();
    renderDiagrams();
    renderQuiz();
    await loadHistory();
    const baseMessage = notesPayload.mongodb_connected
      ? 'Notes generated and saved to MongoDB.'
      : 'Notes generated, but MongoDB is not connected yet. Check backend configuration.';
    const warningMessage = state.warnings.length ? ` ${state.warnings.join(' ')}` : '';
    setFeedback(baseMessage + warningMessage, !notesPayload.mongodb_connected || state.transcriptionQuality === 'low');
  } catch (error) {
    setFeedback(error.message || 'Something went wrong.', true);
  } finally {
    processBtn.disabled = false;
    processBtn.textContent = 'Transcribe and Generate Notes';
  }
});

previewBtn.addEventListener('click', async () => {
  if (!state.notes) {
    setFeedback('Generate notes before opening preview.', true);
    return;
  }
  try {
    const payload = await apiFetch('/api/preview-notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes: state.notes, level: state.level }),
    });
    previewContent.innerHTML = payload.html;
    previewDialog.showModal();
  } catch (error) {
    setFeedback(error.message || 'Preview failed.', true);
  }
});

pdfBtn.addEventListener('click', () => exportNotes('/api/export-pdf'));
docxBtn.addEventListener('click', () => exportNotes('/api/export-docx'));
submitQuizBtn.addEventListener('click', submitQuiz);
quizList.addEventListener('change', handleQuizSelection);

async function exportNotes(endpoint) {
  if (!state.notes) {
    setFeedback('Generate notes before exporting.', true);
    return;
  }
  try {
    const payload = await apiFetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: state.sessionId,
        topic: state.notes.topic || state.topic,
        notes: state.notes,
        level: state.notes.level || state.level,
      }),
    });
    window.location.href = payload.download_url;
    await loadHistory();
  } catch (error) {
    setFeedback(error.message || 'Export failed.', true);
  }
}

async function loadHealth() {
  try {
    const payload = await apiFetch('/health');
    whisperStatus.textContent = payload.whisper_available ? 'Whisper Ready' : 'Demo Mode';
    mongoStatus.textContent = payload.mongodb_connected ? 'Connected' : 'Not Connected';
    if (overviewSystem) {
      overviewSystem.textContent = payload.whisper_available && payload.mongodb_connected ? 'All systems go' : 'Attention needed';
    }
    setStatusState(whisperStatus, payload.whisper_available ? 'online' : 'warning');
    setStatusState(mongoStatus, payload.mongodb_connected ? 'online' : 'warning');
    heroCard?.classList.remove('status-offline');
    if (!payload.whisper_available && payload.whisper_error) {
      setFeedback(`Whisper unavailable: ${payload.whisper_error}`, true);
    }
  } catch (error) {
    whisperStatus.textContent = 'Reconnecting...';
    mongoStatus.textContent = 'Reconnecting...';
    if (overviewSystem) overviewSystem.textContent = 'Reconnecting…';
    setStatusState(whisperStatus, 'warning');
    setStatusState(mongoStatus, 'warning');
    heroCard?.classList.add('status-offline');
  }
}

function setStatusState(node, state) {
  const pill = node.closest('.status-pill');
  if (!pill) return;
  pill.classList.remove('is-online', 'is-warning', 'is-offline');
  if (state === 'online') {
    pill.classList.add('is-online');
  } else if (state === 'warning') {
    pill.classList.add('is-warning');
  } else {
    pill.classList.add('is-offline');
  }
}

async function loadHistory() {
  const payload = await apiFetch('/api/history');
  if (!payload.items?.length) {
    historyList.innerHTML = '<p class="empty-state">Nothing generated yet.</p>';
    if (overviewSessions) overviewSessions.textContent = '0';
    if (overviewLastTopic) overviewLastTopic.textContent = 'No sessions yet';
    return;
  }
  if (overviewSessions) overviewSessions.textContent = String(payload.items.length);
  const latestTopic = payload.items?.[0]?.topic;
  if (overviewLastTopic) overviewLastTopic.textContent = latestTopic ? `Last: ${latestTopic}` : 'No sessions yet';
  historyList.innerHTML = payload.items.map((item) => {
    const latest = item.latest_export;
    const exportHtml = latest
      ? `<a href="${latest.download_url}">${latest.type}: ${latest.filename}</a>`
      : 'No export yet';
    return `
      <article class="history-item">
        <div class="history-top">
          <div>
            <h3>${item.topic}</h3>
            <p class="history-meta">${item.level} | source: ${item.source_filename || 'recorded audio'} | ${new Date(item.created_at).toLocaleString()}</p>
          </div>
          <button class="history-clear-btn" data-session-id="${item.id}">Clear</button>
        </div>
        <p>${item.transcription.slice(0, 180)}${item.transcription.length > 180 ? '...' : ''}</p>
        <p><strong>Latest export:</strong> ${exportHtml}</p>
      </article>
    `;
  }).join('');
}

async function apiFetch(url, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();
  if (token && url.startsWith('/api/') && !url.startsWith('/api/auth/')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  const response = await fetch(url, { ...options, headers });
  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('application/json')) {
    const payload = await response.json();
    if (!response.ok || payload.success === false) {
      const trace = payload.trace ? ` ${payload.trace}` : '';
      throw new Error((payload.error || 'Request failed.') + trace);
    }
    return payload;
  }

  const text = await response.text();
  throw new Error(`Server returned non-JSON response (${response.status}). ${text.slice(0, 220)}`);
}

function renderTranscription() {
  const topicSuffix = state.transcriptionQuality ? ` (${state.transcriptionQuality} confidence transcript)` : '';
  document.getElementById('topicText').textContent = `${state.topic}${topicSuffix}`;
  document.getElementById('transcriptionText').textContent = state.transcription;
}

function renderNotes() {
  document.getElementById('introText').textContent = state.notes.introduction;
  document.getElementById('summaryText').textContent = state.notes.summary;
  renderList(document.getElementById('highlightsList'), state.notes.highlights, 'ul');
  renderList(document.getElementById('structureList'), state.notes.structure, 'ol');
}

function renderDiagrams() {
  const diagramList = document.getElementById('diagramList');
  if (!state.diagrams.length) {
    diagramList.innerHTML = '<p class="empty-state">Process a lecture to generate diagram ideas.</p>';
    return;
  }
  diagramList.replaceChildren(...state.diagrams.map((diagram) => {
    const card = document.createElement('article');
    card.className = 'diagram-card';

    const top = document.createElement('div');
    top.className = 'diagram-top';

    const type = document.createElement('span');
    type.className = 'diagram-type';
    type.textContent = diagram.type;

    const title = document.createElement('strong');
    title.textContent = diagram.title;

    const description = document.createElement('p');
    description.textContent = diagram.description;

    const content = document.createElement('div');
    content.className = 'diagram-canvas';
    content.textContent = diagram.content;

    top.append(type, title);
    card.append(top, description, content);
    return card;
  }));
}

function renderQuiz() {
  document.getElementById('quizResult').textContent = 'No quiz submitted yet.';
  if (!state.quiz.length) {
    quizList.innerHTML = '<p class="empty-state">Quiz questions will appear after note generation.</p>';
    return;
  }
  quizList.innerHTML = state.quiz.map((item, questionIndex) => `
    <article class="quiz-card" data-question-index="${questionIndex}">
      <h3>${questionIndex + 1}. ${item.question}</h3>
      <div class="quiz-options">
        ${item.options.map((option, optionIndex) => `
          <label class="quiz-option" data-option-index="${optionIndex}">
            <input type="radio" name="quiz-${questionIndex}" value="${optionIndex}">
            <span>${option}</span>
          </label>
        `).join('')}
      </div>
      <p class="quiz-feedback-line">Select an option to see the correct answer.</p>
    </article>
  `).join('');
}

function handleQuizSelection(event) {
  const input = event.target.closest('input[type="radio"]');
  if (!input) return;

  const questionIndex = Number(input.name.replace('quiz-', ''));
  const question = state.quiz[questionIndex];
  if (!question) return;

  const quizCard = input.closest('.quiz-card');
  const optionNodes = quizCard.querySelectorAll('.quiz-option');
  const feedbackLine = quizCard.querySelector('.quiz-feedback-line');
  const selectedIndex = Number(input.value);

  optionNodes.forEach((node) => {
    const optionIndex = Number(node.dataset.optionIndex);
    node.classList.remove('correct-answer', 'wrong-answer');

    if (optionIndex === question.answer_index) {
      node.classList.add('correct-answer');
    } else if (optionIndex === selectedIndex && selectedIndex !== question.answer_index) {
      node.classList.add('wrong-answer');
    }
  });

  if (selectedIndex === question.answer_index) {
    feedbackLine.textContent = 'Correct answer selected.';
    feedbackLine.style.color = '#2d8a57';
  } else {
    feedbackLine.textContent = `Incorrect. Correct answer: ${question.options[question.answer_index]}`;
    feedbackLine.style.color = '#d14b39';
  }
}

function submitQuiz() {
  if (!state.quiz.length) {
    setQuizResult('Generate notes first to create a quiz.', true);
    return;
  }
  let score = 0;
  state.quiz.forEach((question, index) => {
    const selected = document.querySelector(`input[name="quiz-${index}"]:checked`);
    if (selected && Number(selected.value) === question.answer_index) {
      score += 1;
    }
  });
  const total = state.quiz.length;
  setQuizResult(`You scored ${score}/${total}.`, score < total);
}

function setQuizResult(message, isWarning = false) {
  const quizResult = document.getElementById('quizResult');
  quizResult.textContent = message;
  quizResult.style.color = isWarning ? '#ff8f7a' : '#5d6d8a';
}

function setFeedback(message, isError = false) {
  feedback.textContent = message;
  feedback.style.color = isError ? '#ff8f7a' : '#93a4c3';
}

function showDashboard() {
  loginShell.hidden = true;
  dashboardShell.hidden = false;
  loginFeedback.textContent = 'Sign in to continue.';
  loginFeedback.style.color = '#93a4c3';
  hydrateUserUi();
}

function showLogin() {
  dashboardShell.hidden = true;
  loginShell.hidden = false;
}

function hydrateUserUi() {
  const user = getUser();
  const label = user?.name
    ? `${user.name}${user.email ? ` (${user.email})` : ''}`
    : (user?.email || '—');

  if (overviewUser) overviewUser.textContent = label;
  if (navUser) {
    navUser.textContent = label;
    navUser.hidden = label === '—';
  }
}

function renderList(node, items) {
  node.replaceChildren(...(items || []).map((item) => {
    const listItem = document.createElement('li');
    listItem.textContent = item;
    return listItem;
  }));
}

historyList.addEventListener('click', async (event) => {
  const clearButton = event.target.closest('.history-clear-btn');
  if (!clearButton) return;

  const sessionId = clearButton.dataset.sessionId;
  if (!sessionId) return;

  clearButton.disabled = true;
  clearButton.textContent = 'Clearing...';

  try {
    await apiFetch(`/api/history/${sessionId}`, { method: 'DELETE' });
    await loadHistory();
    setFeedback('History item cleared successfully.');
  } catch (error) {
    clearButton.disabled = false;
    clearButton.textContent = 'Clear';
    setFeedback(error.message || 'Unable to clear history item.', true);
  }
});

loadHealth();
window.setInterval(loadHealth, 7000);
loadHistory().catch(() => {
  historyList.innerHTML = '<p class="empty-state">History is unavailable right now.</p>';
});

function getPreferredStorage() {
  const pref = window.localStorage.getItem(TOKEN_STORAGE_KEY);
  return pref === 'session' ? window.sessionStorage : window.localStorage;
}

function setToken(token, rememberMe) {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, rememberMe ? 'local' : 'session');
  const storage = rememberMe ? window.localStorage : window.sessionStorage;
  window.localStorage.removeItem(TOKEN_KEY);
  window.sessionStorage.removeItem(TOKEN_KEY);
  storage.setItem(TOKEN_KEY, token);
}

function setUser(user, rememberMe) {
  const storage = rememberMe ? window.localStorage : window.sessionStorage;
  window.localStorage.removeItem(USER_KEY);
  window.sessionStorage.removeItem(USER_KEY);
  storage.setItem(USER_KEY, JSON.stringify(user || {}));
}

function getToken() {
  return (
    window.localStorage.getItem(TOKEN_KEY) ||
    window.sessionStorage.getItem(TOKEN_KEY)
  );
}

function getUser() {
  const raw = window.localStorage.getItem(USER_KEY) || window.sessionStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.sessionStorage.removeItem(TOKEN_KEY);
}

function clearUser() {
  window.localStorage.removeItem(USER_KEY);
  window.sessionStorage.removeItem(USER_KEY);
}

function setAuthMode(mode) {
  if (!loginForm) return;
  loginForm.dataset.mode = mode;

  const isSignup = mode === 'signup';
  tabSignup?.classList.toggle('is-active', isSignup);
  tabLogin?.classList.toggle('is-active', !isSignup);
  tabSignup?.setAttribute('aria-selected', isSignup ? 'true' : 'false');
  tabLogin?.setAttribute('aria-selected', !isSignup ? 'true' : 'false');

  if (nameField) nameField.hidden = !isSignup;
  if (confirmField) confirmField.hidden = !isSignup;

  const passwordInput = document.getElementById('loginPassword');
  if (passwordInput) {
    passwordInput.setAttribute('autocomplete', isSignup ? 'new-password' : 'current-password');
  }

  if (loginSubmitBtn) loginSubmitBtn.textContent = isSignup ? 'Create account' : 'Sign in';
  if (footerToggle) footerToggle.textContent = isSignup ? 'Login' : 'Sign up';
  clearAuthFeedback();
}

function clearAuthFeedback() {
  if (!loginFeedback) return;
  loginFeedback.textContent = '';
  loginFeedback.style.color = 'rgba(96, 112, 142, 0.95)';
}

function setAuthError(message) {
  loginFeedback.textContent = message;
  loginFeedback.style.color = '#ff8f7a';
}

async function submitAuth() {
  const mode = loginForm?.dataset.mode || 'signup';
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  const rememberMe = rememberMeInput?.checked ?? true;

  clearAuthFeedback();

  if (!email) {
    setAuthError('Email is required.');
    return;
  }

  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  if (!emailOk) {
    setAuthError('Enter a valid email address.');
    return;
  }

  if (!password) {
    setAuthError('Password is required.');
    return;
  }

  if (mode === 'signup') {
    const confirm = signupConfirm?.value || '';
    if (!confirm) {
      setAuthError('Please confirm your password.');
      return;
    }
    if (confirm !== password) {
      setAuthError('Passwords do not match.');
      return;
    }
  }

  const originalLabel = loginSubmitBtn?.textContent || 'Sign In';
  if (loginSubmitBtn) {
    loginSubmitBtn.disabled = true;
    loginSubmitBtn.textContent = 'Signing in...';
  }

  try {
    const endpoint = mode === 'signup' ? '/api/auth/register' : '/api/auth/login';
    const body =
      mode === 'signup'
        ? { name: (signupName?.value || '').trim(), email, password }
        : { email, password };

    const payload = await apiFetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!payload?.token) {
      setAuthError('Request succeeded but no token was returned.');
      return;
    }

    setToken(payload.token, rememberMe);
    if (payload.user) setUser(payload.user, rememberMe);
    showDashboard();
    window.history.replaceState({}, '', '/dashboard');
  } catch (error) {
    setAuthError(error.message || 'Request failed.');
  } finally {
    if (loginSubmitBtn) {
      loginSubmitBtn.disabled = false;
      loginSubmitBtn.textContent = originalLabel;
    }
  }
}

if (getToken()) {
  showDashboard();
} else {
  showLogin();
  if (window.location.pathname === '/dashboard') {
    loginFeedback.textContent = 'Sign in to continue to the dashboard.';
    loginFeedback.style.color = '#ff8f7a';
    window.history.replaceState({}, '', '/login');
  }
}

setAuthMode(loginForm?.dataset.mode || 'signup');
hydrateUserUi();
