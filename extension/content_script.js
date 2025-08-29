(function(){
  function getVideoId() {
    const url = new URL(window.location.href);
    if (url.hostname === 'youtu.be') return url.pathname.slice(1);
    return url.searchParams.get('v');
  }
  function createFloatingButton() {
    if (document.getElementById('yt-chatbot-open-btn')) return;
    const btn = document.createElement('button');
    btn.id = 'yt-chatbot-open-btn';
    btn.innerText = 'YT Chatbot';
    Object.assign(btn.style, {
      position: 'fixed',
      right: '16px',
      bottom: '80px',
      zIndex: 999999,
      padding: '8px 12px',
      background: '#FF0000',
      color: '#fff',
      border: 'none',
      borderRadius: '6px',
      cursor: 'pointer',
      boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
    });
    btn.addEventListener('click', async () => {
      const videoId = getVideoId();
      if (videoId) {
        chrome.storage.local.set({ transcript_videoId: videoId }, () => {
          btn.innerText = 'Saved ✓';
          setTimeout(()=> btn.innerText = 'YT Chatbot', 1200);
        });
      } else {
        alert('No video id found on this page.');
      }
    });
    document.body.appendChild(btn);
  }
  const observer = new MutationObserver(() => createFloatingButton());
  observer.observe(document.body, { childList: true, subtree: true });
  createFloatingButton();
})();
