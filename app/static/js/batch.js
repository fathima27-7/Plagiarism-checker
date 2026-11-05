// PlagiScan AI – Multiple Document Comparison (Batch Matrix) Controller (Feature 11)

document.addEventListener('DOMContentLoaded', () => {
  const batchDropzone = document.getElementById('batchDropzone');
  const batchFileInput = document.getElementById('batchFileInput');
  const batchSelectedList = document.getElementById('batchSelectedList');
  const batchFileBadges = document.getElementById('batchFileBadges');
  const btnRunBatch = document.getElementById('btnRunBatch');
  const batchLoading = document.getElementById('batchLoading');
  const batchResultSection = document.getElementById('batchResultSection');
  const matrixTable = document.getElementById('matrixTable');

  let selectedBatchFiles = [];

  if (batchDropzone) {
    ['dragenter', 'dragover'].forEach(name => {
      batchDropzone.addEventListener(name, (e) => {
        e.preventDefault();
        batchDropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      batchDropzone.addEventListener(name, (e) => {
        e.preventDefault();
        batchDropzone.classList.remove('dragover');
      });
    });

    batchDropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files) {
        addFiles(Array.from(e.dataTransfer.files));
      }
    });
  }

  if (batchFileInput) {
    batchFileInput.addEventListener('change', (e) => {
      if (e.target.files) {
        addFiles(Array.from(e.target.files));
      }
    });
  }

  function addFiles(files) {
    const valid = files.filter(f => {
      const n = f.name.toLowerCase();
      return n.endsWith('.pdf') || n.endsWith('.docx') || n.endsWith('.txt');
    });

    if (valid.length === 0) {
      showToast('No valid .pdf, .docx, or .txt documents detected.', true);
      return;
    }

    selectedBatchFiles = selectedBatchFiles.concat(valid);
    renderFileBadges();
  }

  function renderFileBadges() {
    if (selectedBatchFiles.length === 0) {
      batchSelectedList.classList.add('d-none');
      return;
    }

    batchSelectedList.classList.remove('d-none');
    batchFileBadges.innerHTML = selectedBatchFiles.map((f, i) => `
      <span class="badge bg-white text-dark border p-2 d-flex align-items-center gap-2">
        <i class="bi bi-file-earmark-text text-primary"></i> ${escapeHtml(f.name)}
        <button type="button" class="btn-close btn-close-sm" onclick="removeBatchFile(${i})"></button>
      </span>
    `).join('');
  }

  window.removeBatchFile = function(index) {
    selectedBatchFiles.splice(index, 1);
    renderFileBadges();
  };

  if (btnRunBatch) {
    btnRunBatch.addEventListener('click', async () => {
      if (selectedBatchFiles.length < 2) {
        showToast('Please select at least 2 documents for matrix comparison.', true);
        return;
      }

      btnRunBatch.disabled = true;
      batchLoading.classList.remove('d-none');
      batchResultSection.classList.add('d-none');

      const formData = new FormData();
      selectedBatchFiles.forEach(f => {
        formData.append('files', f);
      });

      try {
        const res = await fetch('/api/batch-compare', {
          method: 'POST',
          body: formData
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || 'Failed to compute batch matrix.');
        }

        renderMatrix(data);
      } catch (err) {
        showToast(err.message, true);
      } finally {
        btnRunBatch.disabled = false;
        batchLoading.classList.add('d-none');
      }
    });
  }

  function renderMatrix(data) {
    const filenames = data.filenames;
    const matrix = data.matrix;

    if (!filenames || !matrix) return;

    let headerHtml = '<thead><tr><th class="bg-light">Document</th>';
    filenames.forEach((fn, idx) => {
      headerHtml += `<th title="${escapeHtml(fn)}">Doc #${idx + 1}</th>`;
    });
    headerHtml += '</tr></thead>';

    let bodyHtml = '<tbody>';
    matrix.forEach((row, rIdx) => {
      bodyHtml += `<tr><td class="text-start fw-bold text-dark bg-light" title="${escapeHtml(filenames[rIdx])}">Doc #${rIdx + 1}: ${escapeHtml(filenames[rIdx])}</td>`;
      row.forEach((val, cIdx) => {
        let bgStyle = '';
        let textStyle = '';

        if (rIdx === cIdx) {
          bgStyle = 'background-color: #f1f5f9;';
          textStyle = 'color: #94a3b8; font-weight: normal;';
        } else if (val >= 40) {
          bgStyle = 'background-color: #fee2e2;';
          textStyle = 'color: #dc2626; font-weight: bold;';
        } else if (val >= 20) {
          bgStyle = 'background-color: #fef9c3;';
          textStyle = 'color: #ca8a04; font-weight: bold;';
        } else {
          bgStyle = 'background-color: #f8fafc;';
          textStyle = 'color: #334155;';
        }

        bodyHtml += `<td style="${bgStyle} ${textStyle}">${val}%</td>`;
      });
      bodyHtml += '</tr>';
    });
    bodyHtml += '</tbody>';

    matrixTable.innerHTML = headerHtml + bodyHtml;
    batchResultSection.classList.remove('d-none');
    batchResultSection.scrollIntoView({ behavior: 'smooth' });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
});
