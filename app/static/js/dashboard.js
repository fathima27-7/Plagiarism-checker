// PlagiScan AI – Interactive Analysis Dashboard & Annotation Renderer

document.addEventListener('DOMContentLoaded', () => {
  if (!window.ANALYSIS_DATA) return;

  const data = window.ANALYSIS_DATA;
  const container = document.getElementById('annotatedTextContainer');
  const toggleAI = document.getElementById('toggleAIHighlight');
  const togglePlag = document.getElementById('togglePlagHighlight');
  const inspectorCard = document.getElementById('inspectorCard');
  const inspectorTitle = document.getElementById('inspectorTitle');
  const inspectorText = document.getElementById('inspectorText');
  const inspectorDetails = document.getElementById('inspectorDetails');
  const btnDeleteAnalysis = document.getElementById('btnDeleteAnalysis');

  // Initialize visual charts
  initCharts(data);

  // Render annotated text with highlights (Feature 4)
  renderAnnotatedDocument(data);

  // Highlight toggle events
  if (toggleAI) {
    toggleAI.addEventListener('change', () => {
      const marks = container.querySelectorAll('.ai-highlight');
      marks.forEach(m => {
        m.style.backgroundColor = toggleAI.checked ? '#fef08a' : 'transparent';
        m.style.borderBottom = toggleAI.checked ? '2px solid #ca8a04' : 'none';
      });
    });
  }

  if (togglePlag) {
    togglePlag.addEventListener('change', () => {
      const marks = container.querySelectorAll('.plag-highlight');
      marks.forEach(m => {
        m.style.backgroundColor = togglePlag.checked ? '#fecaca' : 'transparent';
        m.style.borderBottom = togglePlag.checked ? '2px solid #dc2626' : 'none';
      });
    });
  }

  // Delete analysis handler
  if (btnDeleteAnalysis) {
    btnDeleteAnalysis.addEventListener('click', async () => {
      const docId = btnDeleteAnalysis.getAttribute('data-doc-id');
      const analysisId = btnDeleteAnalysis.getAttribute('data-analysis-id');
      if (confirm('Permanently delete this document and all associated analytical data?')) {
        try {
          const res = await fetch(`/api/history/document/${docId}`, { method: 'DELETE' });
          if (res.ok) {
            window.location.href = '/history';
          } else {
            showToast('Failed to delete document.', true);
          }
        } catch (err) {
          showToast(err.message, true);
        }
      }
    });
  }

  function renderAnnotatedDocument(d) {
    const raw = d.rawText || '';
    if (!raw) {
      container.innerHTML = '<div class="text-muted text-center py-4">No text content available.</div>';
      return;
    }

    // Split text into paragraphs
    const paragraphs = raw.split(/\n\s*\n/);
    let html = '';

    // Create lookup sets for fast matching
    const plagMap = new Map();
    d.matches.forEach(m => {
      if (m.queryText) {
        plagMap.set(m.queryText.trim().toLowerCase(), m);
      }
    });

    const aiMap = new Map();
    d.aiSentences.forEach(s => {
      if (s.sentenceText && s.isFlagged) {
        aiMap.set(s.sentenceText.trim().toLowerCase(), s);
      }
    });

    paragraphs.forEach(p => {
      const cleanP = p.trim();
      if (!cleanP) return;

      // Split paragraph into approximate sentences
      const sentences = cleanP.match(/[^.!?]+[.!?]+(\s|$)|[^.!?]+$/g) || [cleanP];
      let pContent = '';

      sentences.forEach(s => {
        const sTrim = s.trim();
        const sKey = sTrim.toLowerCase();

        const plagMatch = plagMap.get(sKey);
        const aiMatch = aiMap.get(sKey);

        if (plagMatch && aiMatch) {
          pContent += `<mark class="both-highlight" data-type="both" data-plag-source="${escapeHtml(plagMatch.sourceTitle)}" data-plag-sim="${plagMatch.similarity}" data-ai-prob="${aiMatch.aiProb}" data-perp="${aiMatch.perplexity}" data-burst="${aiMatch.burstiness}" data-text="${escapeHtml(sTrim)}" title="Suspected AI & Plagiarism overlap">${escapeHtml(s)}</mark> `;
        } else if (plagMatch) {
          pContent += `<mark class="plag-highlight" data-type="plag" data-plag-source="${escapeHtml(plagMatch.sourceTitle)}" data-plag-sim="${plagMatch.similarity}" data-matched-text="${escapeHtml(plagMatch.matchedText)}" data-text="${escapeHtml(sTrim)}" title="Plagiarism Match: ${plagMatch.similarity}% with ${escapeHtml(plagMatch.sourceTitle)}">${escapeHtml(s)}</mark> `;
        } else if (aiMatch) {
          pContent += `<mark class="ai-highlight" data-type="ai" data-ai-prob="${aiMatch.aiProb}" data-perp="${aiMatch.perplexity}" data-burst="${aiMatch.burstiness}" data-text="${escapeHtml(sTrim)}" title="Suspected AI-Generated (${Math.round(aiMatch.aiProb * 100)}% likelihood)">${escapeHtml(s)}</mark> `;
        } else {
          pContent += escapeHtml(s) + ' ';
        }
      });

      html += `<p class="mb-3">${pContent.trim()}</p>`;
    });

    container.innerHTML = html;

    // Attach click events on marks for the Inspector Card
    container.querySelectorAll('mark').forEach(m => {
      m.addEventListener('click', (e) => {
        const type = m.getAttribute('data-type');
        const text = m.getAttribute('data-text');

        inspectorCard.classList.remove('d-none');
        inspectorText.textContent = `"${text}"`;

        if (type === 'ai') {
          const prob = Math.round(parseFloat(m.getAttribute('data-ai-prob')) * 100);
          const perp = m.getAttribute('data-perp');
          const burst = m.getAttribute('data-burst');
          inspectorTitle.innerHTML = '<span class="badge bg-warning text-dark me-2">AI-Generated Suspect</span> Stylometric Markers';
          inspectorDetails.innerHTML = `
            <div><strong>AI Probability:</strong> ${prob}%</div>
            <div><strong>Perplexity (Entropy):</strong> ${perp}</div>
            <div><strong>Burstiness:</strong> ${burst}</div>
          `;
        } else if (type === 'plag') {
          const src = m.getAttribute('data-plag-source');
          const sim = m.getAttribute('data-plag-sim');
          const matched = m.getAttribute('data-matched-text');
          inspectorTitle.innerHTML = '<span class="badge bg-danger me-2">Plagiarism Overlap</span> Reference Corpus Match';
          inspectorDetails.innerHTML = `
            <div><strong>Matching Source:</strong> ${src}</div>
            <div><strong>Similarity:</strong> ${sim}%</div>
            <div class="w-100 mt-2 p-2 bg-white rounded border"><strong>Matched Passage:</strong> <i>"${matched}"</i></div>
          `;
        } else {
          inspectorTitle.innerHTML = '<span class="badge bg-warning text-dark me-2">Combined Alert</span> AI & Plagiarism Overlap';
          inspectorDetails.innerHTML = `
            <div><strong>Matching Source:</strong> ${m.getAttribute('data-plag-source')} (${m.getAttribute('data-plag-sim')}%)</div>
            <div><strong>AI Probability:</strong> ${Math.round(parseFloat(m.getAttribute('data-ai-prob')) * 100)}%</div>
          `;
        }

        inspectorCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    });
  }

  function initCharts(d) {
    // 1. Section Score Chart (Bar chart)
    const sectionCanvas = document.getElementById('sectionScoreChart');
    if (sectionCanvas && d.sections && d.sections.length > 0) {
      const labels = d.sections.map(s => s.name);
      const plagScores = d.sections.map(s => s.plagiarism);
      const aiScores = d.sections.map(s => s.ai);

      new Chart(sectionCanvas, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Plagiarism %',
              data: plagScores,
              backgroundColor: '#ef4444',
              borderRadius: 6
            },
            {
              label: 'AI Likelihood %',
              data: aiScores,
              backgroundColor: '#eab308',
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: { callback: v => v + '%' }
            }
          },
          plugins: {
            legend: { position: 'top' }
          }
        }
      });
    }

    // 2. Composition Doughnut Chart
    const doughnutCanvas = document.getElementById('compositionDoughnut');
    if (doughnutCanvas) {
      const plagP = Math.min(100, d.plagiarismScore || 0);
      const aiP = Math.min(100 - plagP, d.aiScore || 0);
      const originalP = Math.max(0, 100 - plagP - aiP);

      new Chart(doughnutCanvas, {
        type: 'doughnut',
        data: {
          labels: ['Original Content', 'Corpus Plagiarism', 'Suspected AI'],
          datasets: [{
            data: [originalP, plagP, aiP],
            backgroundColor: ['#22c55e', '#ef4444', '#eab308'],
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 12 } }
          },
          cutout: '68%'
        }
      });
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
