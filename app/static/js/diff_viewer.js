// PlagiScan AI – Side-by-Side Dual-Pane Comparison Controller (Feature 7)

document.addEventListener('DOMContentLoaded', () => {
  const selectDoc1 = document.getElementById('selectDoc1');
  const selectDoc2 = document.getElementById('selectDoc2');
  const btnRunCompare = document.getElementById('btnRunCompare');
  const diffMetricsBar = document.getElementById('diffMetricsBar');
  const diffSimilarityScore = document.getElementById('diffSimilarityScore');
  const syncScrollToggle = document.getElementById('syncScrollToggle');

  const pane1 = document.getElementById('pane1');
  const pane2 = document.getElementById('pane2');
  const pane1Title = document.getElementById('pane1Title');
  const pane2Title = document.getElementById('pane2Title');
  const pane1Content = document.getElementById('pane1Content');
  const pane2Content = document.getElementById('pane2Content');
  const pane1MatchCount = document.getElementById('pane1MatchCount');
  const pane2MatchCount = document.getElementById('pane2MatchCount');

  let isSyncingScroll = false;

  // Auto-run if query params exist
  const urlParams = new URLSearchParams(window.location.search);
  const paramDoc1 = urlParams.get('doc1_id');
  const paramDoc2 = urlParams.get('doc2_id');

  if (paramDoc1 && paramDoc2 && selectDoc1 && selectDoc2) {
    selectDoc1.value = paramDoc1;
    selectDoc2.value = paramDoc2;
    runComparison();
  }

  if (btnRunCompare) {
    btnRunCompare.addEventListener('click', runComparison);
  }

  async function runComparison() {
    const id1 = selectDoc1.value;
    const id2 = selectDoc2.value;

    if (!id1 || !id2) {
      showToast('Please select two documents for comparison.', true);
      return;
    }

    if (id1 === id2) {
      showToast('Please select two distinct documents.', true);
      return;
    }

    btnRunCompare.disabled = true;
    pane1Content.innerHTML = '<div class="text-center py-5 text-muted"><div class="spinner-border spinner-border-sm text-primary me-2"></div> Comparing documents...</div>';
    pane2Content.innerHTML = '<div class="text-center py-5 text-muted"><div class="spinner-border spinner-border-sm text-primary me-2"></div> Aligning sentences...</div>';

    try {
      const res = await fetch('/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc1_id: id1, doc2_id: id2 })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to compare documents.');
      }

      renderDiffView(data);
    } catch (err) {
      showToast(err.message, true);
    } finally {
      btnRunCompare.disabled = false;
    }
  }

  function renderDiffView(data) {
    pane1Title.textContent = data.doc1_title || 'Document 1';
    pane2Title.textContent = data.doc2_title || 'Document 2';

    diffMetricsBar.classList.remove('d-none');
    diffSimilarityScore.textContent = `${data.overall_similarity}%`;

    let matches1 = 0;
    let matches2 = 0;

    // Render Pane 1
    let html1 = '';
    data.doc1_sentences.forEach(s => {
      if (s.is_match) {
        matches1++;
        html1 += `<p class="mb-2"><mark class="plag-highlight sent-match-1" id="sent1_${s.index}" data-match-target="sent2_${s.matched_with_index}" title="Similarity: ${s.score}% with Doc 2 sentence #${s.matched_with_index + 1}">[${s.index + 1}] ${escapeHtml(s.text)}</mark></p>`;
      } else {
        html1 += `<p class="mb-2 text-muted" id="sent1_${s.index}">[${s.index + 1}] ${escapeHtml(s.text)}</p>`;
      }
    });

    // Render Pane 2
    let html2 = '';
    data.doc2_sentences.forEach(s => {
      if (s.is_match) {
        matches2++;
        html2 += `<p class="mb-2"><mark class="plag-highlight sent-match-2" id="sent2_${s.index}" data-match-target="sent1_${s.matched_with_index}" title="Similarity: ${s.score}% with Doc 1 sentence #${s.matched_with_index + 1}">[${s.index + 1}] ${escapeHtml(s.text)}</mark></p>`;
      } else {
        html2 += `<p class="mb-2 text-muted" id="sent2_${s.index}">[${s.index + 1}] ${escapeHtml(s.text)}</p>`;
      }
    });

    pane1Content.innerHTML = html1 || '<div class="text-muted text-center py-4">No content</div>';
    pane2Content.innerHTML = html2 || '<div class="text-muted text-center py-4">No content</div>';

    pane1MatchCount.textContent = `${matches1} matched sentence(s)`;
    pane2MatchCount.textContent = `${matches2} matched sentence(s)`;

    setupInteractiveAlignment();
    setupSynchronizedScroll();
  }

  function setupInteractiveAlignment() {
    // Click on Doc 1 match -> scroll and highlight Doc 2 match
    pane1.querySelectorAll('.sent-match-1').forEach(el => {
      el.addEventListener('click', () => {
        const targetId = el.getAttribute('data-match-target');
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
          clearActiveHighlights();
          el.classList.add('matched-sentence-active');
          targetEl.classList.add('matched-sentence-active');
          targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    });

    // Click on Doc 2 match -> scroll and highlight Doc 1 match
    pane2.querySelectorAll('.sent-match-2').forEach(el => {
      el.addEventListener('click', () => {
        const targetId = el.getAttribute('data-match-target');
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
          clearActiveHighlights();
          el.classList.add('matched-sentence-active');
          targetEl.classList.add('matched-sentence-active');
          targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    });
  }

  function clearActiveHighlights() {
    document.querySelectorAll('.matched-sentence-active').forEach(e => {
      e.classList.remove('matched-sentence-active');
    });
  }

  function setupSynchronizedScroll() {
    pane1.addEventListener('scroll', () => {
      if (!syncScrollToggle.checked || isSyncingScroll) return;
      isSyncingScroll = true;
      const ratio = pane1.scrollTop / (pane1.scrollHeight - pane1.clientHeight);
      pane2.scrollTop = ratio * (pane2.scrollHeight - pane2.clientHeight);
      setTimeout(() => { isSyncingScroll = false; }, 40);
    });

    pane2.addEventListener('scroll', () => {
      if (!syncScrollToggle.checked || isSyncingScroll) return;
      isSyncingScroll = true;
      const ratio = pane2.scrollTop / (pane2.scrollHeight - pane2.clientHeight);
      pane1.scrollTop = ratio * (pane1.scrollHeight - pane1.clientHeight);
      setTimeout(() => { isSyncingScroll = false; }, 40);
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
});
