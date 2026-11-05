// PlagiScan AI – Upload & Scan Controller

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const fileInfoCard = document.getElementById('fileInfoCard');
  const selectedFileName = document.getElementById('selectedFileName');
  const selectedFileSize = document.getElementById('selectedFileSize');
  const btnRemoveFile = document.getElementById('btnRemoveFile');
  const btnStartScan = document.getElementById('btnStartScan');
  const optSaveReference = document.getElementById('optSaveReference');

  const directTitleInput = document.getElementById('directTitleInput');
  const directTextInput = document.getElementById('directTextInput');

  const progressContainer = document.getElementById('progressContainer');
  const progressBar = document.getElementById('progressBar');
  const progressStatusText = document.getElementById('progressStatusText');
  const progressPercentText = document.getElementById('progressPercentText');

  let currentSelectedFile = null;

  // Dropzone drag-and-drop events
  if (dropzone) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
      }
    });
  }

  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
      }
    });
  }

  function handleFileSelection(file) {
    const validExtensions = ['.pdf', '.docx', '.doc', '.txt'];
    const lowerName = file.name.toLowerCase();
    const isValid = validExtensions.some(ext => lowerName.endsWith(ext));

    if (!isValid) {
      showToast('Please select a valid document (.pdf, .docx, or .txt).', true);
      return;
    }

    currentSelectedFile = file;
    selectedFileName.textContent = file.name;
    selectedFileSize.textContent = formatBytes(file.size);
    fileInfoCard.classList.remove('d-none');
    dropzone.classList.add('d-none');
  }

  if (btnRemoveFile) {
    btnRemoveFile.addEventListener('click', () => {
      currentSelectedFile = null;
      fileInput.value = '';
      fileInfoCard.classList.add('d-none');
      dropzone.classList.remove('d-none');
    });
  }

  function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  // Scan execution trigger
  if (btnStartScan) {
    btnStartScan.addEventListener('click', async () => {
      const activeTab = document.querySelector('#uploadTab .nav-link.active').id;
      const isReference = optSaveReference ? optSaveReference.checked : false;

      if (activeTab === 'file-tab') {
        if (!currentSelectedFile) {
          showToast('Please select or drop a document to scan.', true);
          return;
        }
        await uploadAndAnalyzeFile(currentSelectedFile, isReference);
      } else {
        const text = directTextInput ? directTextInput.value.trim() : '';
        const title = (directTitleInput && directTitleInput.value.trim()) || 'Pasted_Academic_Document.txt';
        if (!text || text.split(/\s+/).length < 25) {
          showToast('Please provide at least 25 words of academic text for analysis.', true);
          return;
        }
        const textBlob = new Blob([text], { type: 'text/plain' });
        const textFile = new File([textBlob], title.endsWith('.txt') ? title : title + '.txt', { type: 'text/plain' });
        await uploadAndAnalyzeFile(textFile, isReference);
      }
    });
  }

  function setProgress(percent, status) {
    progressContainer.classList.remove('d-none');
    progressBar.style.width = `${percent}%`;
    progressPercentText.textContent = `${percent}%`;
    progressStatusText.textContent = status;
  }

  async function uploadAndAnalyzeFile(file, isReference) {
    btnStartScan.disabled = true;
    setProgress(15, 'Extracting text and verifying format...');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_reference', isReference ? 'true' : 'false');

    try {
      // Step 1: Upload and extract document
      const uploadRes = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      const uploadData = await uploadRes.json();
      if (!uploadRes.ok) {
        throw new Error(uploadData.error || 'Failed to upload document.');
      }

      const docId = uploadData.document.id;
      setProgress(40, 'Computing TF-IDF vectors against academic corpus...');

      // Step 2: Trigger analytical pipeline
      setTimeout(() => {
        setProgress(70, 'Evaluating sentence perplexity, burstiness & stylometrics...');
      }, 700);

      setTimeout(() => {
        setProgress(88, 'Auditing citations, sections & generating readability profile...');
      }, 1400);

      const analyzeRes = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: docId })
      });

      const analyzeData = await analyzeRes.json();
      if (!analyzeRes.ok) {
        throw new Error(analyzeData.error || 'Analysis pipeline failed.');
      }

      setProgress(100, 'Analysis complete! Redirecting to report...');
      setTimeout(() => {
        window.location.href = analyzeData.redirect_url;
      }, 500);

    } catch (err) {
      showToast(err.message, true);
      btnStartScan.disabled = false;
      progressContainer.classList.add('d-none');
    }
  }
});
