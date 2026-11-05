// PlagiScan AI – Shared Utilities & Toast Notification Handler

function showToast(message, isError = false) {
  const toastEl = document.getElementById('appToast');
  const toastMsg = document.getElementById('toastMessage');
  if (!toastEl || !toastMsg) return;

  toastMsg.textContent = message;
  toastEl.className = `toast align-items-center text-white border-0 ${isError ? 'bg-danger' : 'bg-dark'}`;

  const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
  toast.show();
}

window.showToast = showToast;
