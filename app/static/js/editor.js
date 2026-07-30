/* Editable-preview controller: rich-text toolbar + download with compliance guard. */
(function () {
  const cfg = window.HRDOC;
  const docEl = document.getElementById('document');
  const statusEl = document.getElementById('status');
  const errBox = document.getElementById('errbox');

  // Keep locked regions truly immutable even against paste/key events.
  docEl.querySelectorAll('.doc-region.locked').forEach(el => {
    el.setAttribute('contenteditable', 'false');
  });

  // Toolbar: apply formatting to the focused editable region.
  document.querySelectorAll('#toolbar button[data-cmd]').forEach(btn => {
    btn.addEventListener('mousedown', e => e.preventDefault()); // keep selection
    btn.addEventListener('click', () => {
      document.execCommand(btn.dataset.cmd, false, null);
    });
  });

  function setStatus(msg, kind) {
    statusEl.textContent = msg || '';
    statusEl.className = 'tb-status' + (kind ? ' ' + kind : '');
  }

  function showErrors(errors) {
    errBox.style.display = 'block';
    errBox.innerHTML = '<strong>Cannot download — compliance check failed:</strong><ul>' +
      errors.map(e => '<li>' + e + '</li>').join('') + '</ul>';
    errBox.scrollIntoView({behavior: 'smooth', block: 'center'});
  }

  function clientCheck() {
    // Fast local check mirroring the server guard.
    const html = docEl.innerHTML;
    const missing = cfg.requiredTags.filter(t => html.indexOf('data-comp="' + t + '"') === -1);
    return missing;
  }

  async function download(fmt) {
    errBox.style.display = 'none';
    const missing = clientCheck();
    if (missing.length) {
      showErrors(missing.map(t => "Required clause '" + t + "' is missing."));
      return;
    }
    setStatus('Rendering ' + fmt.toUpperCase() + '…');
    const url = cfg.downloadUrl.replace('FMT', fmt);
    const form = new URLSearchParams();
    form.set('body_html', docEl.innerHTML);
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: form.toString()
      });
      if (resp.status === 422) {
        const data = await resp.json();
        showErrors(data.errors || ['Compliance validation failed.']);
        setStatus('');
        return;
      }
      if (!resp.ok) { setStatus('Error: ' + resp.status, 'err'); return; }
      const blob = await resp.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = cfg.filename + '.' + fmt;
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(a.href);
      setStatus('Downloaded ' + a.download + (fmt === 'pdf' ? ' · management notified' : ''), 'ok');
    } catch (e) {
      setStatus('Network error: ' + e, 'err');
    }
  }

  document.getElementById('dl-pdf').addEventListener('click', () => download('pdf'));
  document.getElementById('dl-docx').addEventListener('click', () => download('docx'));
})();
