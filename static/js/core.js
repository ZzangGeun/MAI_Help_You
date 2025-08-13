// (Removed old placeholder alert for login open)

// Sidebar toggle (mobile)
(function(){
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if(!toggle || !sidebar) return;
  function open(){
    sidebar.classList.add('open');
    document.body.classList.add('sidebar-open');
    overlay?.classList.add('active');
    overlay&&(overlay.hidden=false);
    toggle.setAttribute('aria-expanded','true');
  }
  function close(){
    sidebar.classList.remove('open');
    document.body.classList.remove('sidebar-open');
    overlay?.classList.remove('active');
    overlay&&(overlay.hidden=true);
    toggle.setAttribute('aria-expanded','false');
  }
  toggle.addEventListener('click', ()=>{
    sidebar.classList.contains('open') ? close() : open();
  });
  overlay?.addEventListener('click', close);
  document.addEventListener('keydown', (ev)=>{
    if(ev.key === 'Escape' && sidebar.classList.contains('open')){
      close();
      toggle.focus();
    }
  });
  // Resize guard: if desktop width, ensure sidebar visible & overlay cleared
  window.addEventListener('resize', ()=>{
    if(window.innerWidth > 768){
      sidebar.classList.remove('open');
      overlay?.classList.remove('active');
      overlay&&(overlay.hidden=true);
      document.body.classList.remove('sidebar-open');
      toggle.setAttribute('aria-expanded','false');
    }
  });
})();

// Login Modal logic
(function(){
  const modal = document.getElementById('loginModal');
  if(!modal) return;
  const closeBtn = modal.querySelector('[data-close-modal]');
  const loginForm = modal.querySelector('#loginForm');
  const userArea = document.getElementById('userArea');
  let lastFocused = null;

  function bindOpenButtons(){
    document.querySelectorAll('[data-open-login]').forEach(btn=>{
      if(!btn._loginBound){
        btn.addEventListener('click', (e)=>{ e.preventDefault(); open(); });
        btn._loginBound = true;
      }
    });
  }

  function open(){
    lastFocused = document.activeElement;
  modal.hidden = false;
  modal.removeAttribute('aria-hidden');
  modal.style.display = 'flex';
    document.body.classList.add('modal-open');
    const firstInput = modal.querySelector('input,button,select,textarea');
    firstInput && firstInput.focus();
    trap();
  }
  function close(){
  if(modal.hidden) return; // already closed
  modal.hidden = true;
  modal.setAttribute('aria-hidden','true');
  modal.style.display = 'none';
    document.body.classList.remove('modal-open');
    release();
    lastFocused && lastFocused.focus();
  }

  // Prototype login handler (accept any credentials)
  if(loginForm){
    loginForm.addEventListener('submit', (e)=>{
      e.preventDefault();
      const usernameInput = loginForm.querySelector('input[name="username"]');
      const passwordInput = loginForm.querySelector('input[name="password"]');
      const username = (usernameInput?.value || '').trim();
      if(!username){
        usernameInput && usernameInput.focus();
        return;
      }
      // Simulate success
      if(userArea){
        userArea.innerHTML = `<span class="user-name">${username}</span><button type="button" class="btn-logout" id="protoLogoutBtn">로그아웃</button>`;
        const logoutBtn = document.getElementById('protoLogoutBtn');
        logoutBtn?.addEventListener('click', ()=>{
          userArea.innerHTML = `<button class=\"btn-login\" data-open-login title=\"로그인 없이도 기본 기능 사용 가능\">로그인</button>`;
          bindOpenButtons();
        });
      }
      close();
      loginForm.reset();
    });
  }

  bindOpenButtons();
  closeBtn && closeBtn.addEventListener('click', close);
  modal.addEventListener('click', (e)=>{ if(e.target === modal) close(); });
  document.addEventListener('keydown', (e)=>{ if(e.key==='Escape' && !modal.hidden) close(); });

  // Focus trap
  let focusables = [];
  function trap(){
    focusables = Array.from(modal.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])'));
    if(!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length-1];
    function handle(e){
      if(e.key !== 'Tab') return;
      if(e.shiftKey && document.activeElement === first){ e.preventDefault(); last.focus(); }
      else if(!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); }
    }
    modal.addEventListener('keydown', handle);
    modal._trapHandler = handle;
  }
  function release(){
    if(modal._trapHandler) modal.removeEventListener('keydown', modal._trapHandler);
  }
})();
