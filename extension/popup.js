const chatEl = document.getElementById('chat');
const askBtn = document.getElementById('askBtn');
const queryInput = document.getElementById('query');
const statustxt = document.getElementById('statustxt');

function addMessage(text, who='bot') {
  const d = document.createElement('div');
  d.className = 'msg ' + (who==='user'?'user':'bot');
  d.innerText = text;
  chatEl.appendChild(d);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function setStatus(s){ statustxt.innerText = s; }

// helper to get video id from active tab or chrome.storage (content script saves it)
async function getVideoId() {
  const stored = await new Promise(resolve => chrome.storage.local.get(['transcript_videoId'], resolve));
  if (stored && stored.transcript_videoId) return stored.transcript_videoId;
  const tabs = await chrome.tabs.query({active:true,currentWindow:true});
  if (tabs && tabs[0] && tabs[0].url) {
    try {
      const url = new URL(tabs[0].url);
      if (url.hostname === 'youtu.be') return url.pathname.slice(1);
      return url.searchParams.get('v');
    } catch(e){}
  }
  return null;
}

async function askBackend(videoId, question) {
  setStatus('Asking backend...');
  try {
    const resp = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: videoId, question })
    });
    if (!resp.ok) {
      const text = await resp.text();
      addMessage('Backend error: ' + text, 'bot');
      setStatus('Error');
      return;
    }
    const data = await resp.json();
    addMessage(data.answer, 'bot');
    setStatus('Done');
  } catch (err) {
    addMessage('Could not contact backend. Is it running on http://localhost:8000 ?', 'bot');
    setStatus('Offline');
  }
}

askBtn.addEventListener('click', async ()=>{
  const q = queryInput.value.trim();
  if (!q) return;
  addMessage(q, 'user');
  queryInput.value='';
  setStatus('Getting video id...');
  const vid = await getVideoId();
  if (!vid) {
    addMessage('No video id found. Open a YouTube video and click the floating "YT Chatbot" button, or refresh extension.', 'bot');
    setStatus('No video');
    return;
  }
  await askBackend(vid, q);
});

queryInput.addEventListener('keypress',(e)=>{ if (e.key==='Enter') askBtn.click(); });

setStatus('Ready');
