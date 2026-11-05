// PlagiScan AI – History & Data Privacy Controller (Features 12 & 14)

document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.getElementById('historyTableBody');
  const searchInput = document.getElementById('historySearchInput');
  const sortSelect = document.getElementById('historySortSelect');
  const btnRefresh = document.getElementById('btnRefreshHistory');
  const paginationInfo = document.getElementById('paginationInfo');
  const paginationControls = document.getElementById('paginationControls');

  const deleteModalEl = document.getElementById('deleteConfirmModal');
  const btnConfirmDelete = document.getElementById('btnConfirmDelete');
  const deleteModal = deleteModalEl ? new bootstrap.Modal(deleteModalEl) : null;

  let currentPage = 1;
  let targetDocIdToDelete = null;

  loadHistory();

  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        currentPage = 1;
        loadHistory();
      }, 350);
    });
  }

  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      currentPage = 1;
      loadHistory();
    });
  }

  if (btnRefresh) {
    btnRefresh.addEventListener('click', loadHistory);
  }

  async function loadHistory() {
    tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted"><div class="spinner-border spinner-border-sm text-primary me-2"></div> Loading records...</td></tr>';

    const searchVal = searchInput ? searchInput.value.trim() : '';
    const sortVal = sortSelect ? sortSelect.value : 'created_at_desc';
    const [sort, order] = sortVal.split('_');

    const params = new URLSearchParams({
      page: currentPage,
      per_page: 10,
      search: searchVal,
      sort: sort,
      order: order
    });

    try {
      const res = await fetch(`/api/history?${params.toString()}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to fetch history.');

      renderHistoryTable(data);
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-danger">${err.message}</td></tr>`;
    }
  }

  function renderHistoryTable(data) {
    const items = data.items;
    if (!items || items.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-5 text-muted">No historical analyses found matching your query.</td></tr>';
      paginationInfo.textContent = 'Showing 0 records';
      paginationControls.innerHTML = '';
      return;
    }

    let html = '';
    items.forEach(item => {
      const plagBadge = item.plagiarism_score > 25 ? 'bg-danger' : (item.plagiarism_score > 10 ? 'bg-warning text-dark' : 'bg-success');
      const aiBadge = item.ai_likelihood_score > 50 ? 'bg-warning text-dark' : (item.ai_likelihood_score > 25 ? 'bg-info text-dark' : 'bg-success');

      html += `
        <tr>
          <td>
            <div class="fw-bold text-dark">${escapeHtml(item.filename)}</div>
            <small class="text-muted">${item.word_count} words • .${(item.file_type || '').toUpperCase()}</small>
          </td>
          <td>${item.created_at || 'N/A'}</td>
          <td><span class="badge ${plagBadge}">${item.plagiarism_score}%</span></td>
          <td><span class="badge ${aiBadge}">${item.ai_likelihood_score}% (${escapeHtml(item.ai_risk_level)})</span></td>
          <td>Grade ${item.flesch_kincaid_grade}</td>
          <td class="text-end">
            <div class="btn-group btn-group-sm">
              <a href="/analyze/${item.id}" class="btn btn-outline-primary" title="View Detailed Report">
                <i class="bi bi-eye"></i>
              </a>
              <a href="/reports/download/${item.id}" class="btn btn-outline-secondary" title="Download PDF Certificate">
                <i class="bi bi-file-earmark-arrow-down"></i>
              </a>
              <button type="button" class="btn btn-outline-danger" onclick="promptDelete(${item.document_id})" title="Permanently Delete (Privacy Purge)">
                <i class="bi bi-trash3"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    });

    tableBody.innerHTML = html;
    paginationInfo.textContent = `Showing page ${data.page} of ${data.pages} (Total: ${data.total} records)`;

    // Render pagination buttons
    let pButtons = '';
    if (data.has_prev) {
      pButtons += `<button type="button" class="btn btn-outline-secondary" onclick="changePage(${data.page - 1})">&laquo; Prev</button>`;
    }
    pButtons += `<button type="button" class="btn btn-primary active">${data.page}</button>`;
    if (data.has_next) {
      pButtons += `<button type="button" class="btn btn-outline-secondary" onclick="changePage(${data.page + 1})">Next &raquo;</button>`;
    }
    paginationControls.innerHTML = pButtons;
  }

  window.changePage = function(p) {
    currentPage = p;
    loadHistory();
  };

  window.promptDelete = function(docId) {
    targetDocIdToDelete = docId;
    if (deleteModal) {
      deleteModal.show();
    }
  };

  if (btnConfirmDelete) {
    btnConfirmDelete.addEventListener('click', async () => {
      if (!targetDocIdToDelete) return;

      btnConfirmDelete.disabled = true;
      try {
        const res = await fetch(`/api/history/document/${targetDocIdToDelete}`, {
          method: 'DELETE'
        });
        const resData = await res.json();
        if (res.ok) {
          if (deleteModal) deleteModal.hide();
          showToast(resData.message || 'Document erased.');
          loadHistory();
        } else {
          showToast(resData.error || 'Failed to delete document.', true);
        }
      } catch (err) {
        showToast(err.message, true);
      } finally {
        btnConfirmDelete.disabled = false;
        targetDocIdToDelete = null;
      }
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
});
