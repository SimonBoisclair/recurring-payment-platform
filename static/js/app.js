const API = '';
let token = localStorage.getItem('recurpay_token');

// --- Auth ---
function authHeaders() {
    return { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
}

async function apiFetch(path, opts = {}) {
    opts.headers = { ...authHeaders(), ...opts.headers };
    const resp = await fetch(API + path, opts);
    if (resp.status === 401) { logout(); return null; }
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || 'Request failed');
    }
    return resp.json();
}

// --- Login ---
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('login-error');
    errEl.style.display = 'none';
    try {
        const resp = await fetch(API + '/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
            }),
        });
        if (!resp.ok) throw new Error('Invalid credentials');
        const data = await resp.json();
        token = data.access_token;
        localStorage.setItem('recurpay_token', token);
        showApp();
    } catch (err) {
        errEl.textContent = err.message;
        errEl.style.display = 'block';
    }
});

function logout() {
    token = null;
    localStorage.removeItem('recurpay_token');
    document.getElementById('app-view').style.display = 'none';
    document.getElementById('login-view').style.display = 'flex';
}

document.getElementById('logout-btn').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
});

// --- Navigation ---
const pages = ['dashboard', 'clients', 'payments', 'settings'];

document.querySelectorAll('[data-page]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo(link.dataset.page);
    });
});

function navigateTo(page) {
    pages.forEach(p => {
        document.getElementById(`page-${p}`).style.display = p === page ? 'block' : 'none';
    });
    document.querySelectorAll('[data-page]').forEach(a => {
        a.classList.toggle('active', a.dataset.page === page);
    });
    if (page === 'dashboard') loadDashboard();
    if (page === 'clients') loadClients();
    if (page === 'payments') loadPayments();
    if (page === 'settings') loadSettings();
}

// --- Dashboard ---
async function loadDashboard() {
    try {
        const data = await apiFetch('/api/dashboard');
        if (!data) return;
        document.getElementById('stat-clients').textContent = data.total_clients;
        document.getElementById('stat-active').textContent = data.active_subscriptions;
        document.getElementById('stat-revenue').textContent = '$' + data.monthly_revenue.toFixed(2);
        document.getElementById('stat-collected').textContent = '$' + data.total_collected.toFixed(2);

        const tbody = document.getElementById('recent-payments');
        tbody.innerHTML = data.recent_payments.length === 0
            ? '<tr><td colspan="4" style="text-align:center;color:#94a3b8;">No payments yet</td></tr>'
            : data.recent_payments.map(p => `
                <tr>
                    <td>${esc(p.client_name)}</td>
                    <td>$${p.amount.toFixed(2)} ${p.currency}</td>
                    <td><span class="badge badge-${p.status === 'completed' ? 'completed' : 'pending'}">${p.status}</span></td>
                    <td>${formatDate(p.paid_at || p.created_at)}</td>
                </tr>
            `).join('');
    } catch (err) {
        console.error('Dashboard error:', err);
    }
}

// --- Clients ---
let clientsData = [];

async function loadClients() {
    try {
        clientsData = await apiFetch('/api/clients') || [];
        const tbody = document.getElementById('clients-table');
        tbody.innerHTML = clientsData.length === 0
            ? '<tr><td colspan="6" style="text-align:center;color:#94a3b8;">No clients yet. Click "Add Client" to get started.</td></tr>'
            : clientsData.map(c => `
                <tr>
                    <td><strong>${esc(c.name)}</strong><br><small style="color:#94a3b8;">${esc(c.email)}</small></td>
                    <td>${esc(c.company || '—')}</td>
                    <td>$${c.monthly_amount.toFixed(2)} ${c.currency}/mo</td>
                    <td><span class="badge badge-${statusClass(c.subscription_status)}">${c.subscription_status}</span></td>
                    <td>
                        <span class="copy-link" onclick="copyPaymentLink('${c.payment_token}')" title="Click to copy payment link">
                            Copy Link
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline" onclick="editClient('${c.id}')">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteClient('${c.id}', '${esc(c.name)}')">Delete</button>
                    </td>
                </tr>
            `).join('');
    } catch (err) {
        console.error('Clients error:', err);
    }
}

function showAddClientModal() {
    document.getElementById('modal-title').textContent = 'Add New Client';
    document.getElementById('edit-client-id').value = '';
    document.getElementById('client-form').reset();
    document.getElementById('add-client-modal').classList.add('show');
}

function editClient(id) {
    const c = clientsData.find(cl => cl.id === id);
    if (!c) return;
    document.getElementById('modal-title').textContent = 'Edit Client';
    document.getElementById('edit-client-id').value = c.id;
    document.getElementById('client-name').value = c.name;
    document.getElementById('client-email').value = c.email;
    document.getElementById('client-company').value = c.company || '';
    document.getElementById('client-amount').value = c.monthly_amount;
    document.getElementById('client-currency').value = c.currency;
    document.getElementById('client-description').value = c.description || '';
    document.getElementById('add-client-modal').classList.add('show');
}

function closeModal() {
    document.getElementById('add-client-modal').classList.remove('show');
}

document.getElementById('client-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const clientId = document.getElementById('edit-client-id').value;
    const payload = {
        name: document.getElementById('client-name').value,
        email: document.getElementById('client-email').value,
        company: document.getElementById('client-company').value || null,
        monthly_amount: parseFloat(document.getElementById('client-amount').value),
        currency: document.getElementById('client-currency').value,
        description: document.getElementById('client-description').value || null,
    };
    try {
        if (clientId) {
            await apiFetch(`/api/clients/${clientId}`, { method: 'PUT', body: JSON.stringify(payload) });
        } else {
            await apiFetch('/api/clients', { method: 'POST', body: JSON.stringify(payload) });
        }
        closeModal();
        loadClients();
    } catch (err) {
        alert('Error: ' + err.message);
    }
});

async function deleteClient(id, name) {
    if (!confirm(`Delete client "${name}"? This will also cancel their subscription.`)) return;
    try {
        await apiFetch(`/api/clients/${id}`, { method: 'DELETE' });
        loadClients();
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

function copyPaymentLink(paymentToken) {
    const url = `${window.location.origin}/pay/${paymentToken}`;
    navigator.clipboard.writeText(url).then(() => {
        alert('Payment link copied to clipboard!');
    }).catch(() => {
        prompt('Copy this payment link:', url);
    });
}

// --- Payments ---
async function loadPayments() {
    try {
        const payments = await apiFetch('/api/payments') || [];
        const tbody = document.getElementById('payments-table');
        tbody.innerHTML = payments.length === 0
            ? '<tr><td colspan="6" style="text-align:center;color:#94a3b8;">No payments recorded yet</td></tr>'
            : payments.map(p => `
                <tr>
                    <td>${esc(p.client_name)}</td>
                    <td>$${p.amount.toFixed(2)} ${p.currency}</td>
                    <td><span class="badge badge-${p.status === 'completed' ? 'completed' : 'pending'}">${p.status}</span></td>
                    <td><small>${esc(p.paypal_payment_id || '—')}</small></td>
                    <td>${p.wave_invoice_id
                        ? '<span class="badge badge-active">Synced</span>'
                        : '<button class="btn btn-sm btn-outline" onclick="syncWave(\'' + p.id + '\')">Sync</button>'
                    }</td>
                    <td>${formatDate(p.paid_at || p.created_at)}</td>
                </tr>
            `).join('');
    } catch (err) {
        console.error('Payments error:', err);
    }
}

async function syncWave(paymentId) {
    try {
        await apiFetch(`/api/payments/${paymentId}/sync-wave`, { method: 'POST' });
        loadPayments();
    } catch (err) {
        alert('Wave sync error: ' + err.message);
    }
}

// --- Settings ---
function loadSettings() {
    const baseUrl = window.location.origin;
    document.getElementById('webhook-url').textContent = `${baseUrl}/webhooks/paypal`;
    document.getElementById('paypal-status').textContent = 'Configure via .env file (PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)';
    document.getElementById('wave-status').textContent = 'Configure via .env file (WAVE_API_TOKEN, WAVE_BUSINESS_ID)';
}

// --- Helpers ---
function esc(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}

function statusClass(status) {
    status = (status || '').toLowerCase();
    if (status === 'active') return 'active';
    if (status === 'cancelled') return 'cancelled';
    return 'pending';
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
    });
}

// --- Init ---
async function showApp() {
    document.getElementById('login-view').style.display = 'none';
    document.getElementById('app-view').style.display = 'flex';
    navigateTo('dashboard');
}

if (token) {
    apiFetch('/api/dashboard').then(data => {
        if (data) showApp();
    }).catch(() => logout());
} else {
    document.getElementById('login-view').style.display = 'flex';
}
