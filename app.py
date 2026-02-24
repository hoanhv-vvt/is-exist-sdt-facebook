import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Lưu token trong bộ nhớ
TOKEN_STORE = {
    "bearer_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1SWQiOiI2NTQ0N2E3ZGYwOTdlNTg5MWY3ZTlhMGQiLCJzSWQiOiI4ejB0V2drcFdscTVnVmNWOVlTSlQiLCJpYXQiOjE3NzE4OTg5NDYsImV4cCI6MTc3Mjc2Mjk0Nn0.Y-J_fExkc0DP_LCmcXNNQuS0JeejboM6lyEBkZllVf0"
}

FBNUMBER_API_URL = "https://fbnumber.com/api/v1/phone/find-info-by-phone"

HEADERS_TEMPLATE = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "origin": "https://app.fbnumber.com",
    "referer": "https://app.fbnumber.com/",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
}

# ─── HTML UI ────────────────────────────────────────────────────────────────────

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FB Number Lookup</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #e0e0e0;
        }

        .container {
            width: 100%;
            max-width: 580px;
        }

        .card {
            background: rgba(255, 255, 255, 0.06);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 36px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        }

        h1 {
            text-align: center;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            text-align: center;
            font-size: 0.85rem;
            color: #9ca3af;
            margin-bottom: 28px;
        }

        label {
            display: block;
            font-size: 0.8rem;
            font-weight: 600;
            color: #a78bfa;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }

        input, textarea {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            color: #f0f0f0;
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.25s, box-shadow 0.25s;
        }

        input:focus, textarea:focus {
            border-color: #a78bfa;
            box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.2);
        }

        input::placeholder, textarea::placeholder {
            color: #6b7280;
        }

        textarea {
            resize: vertical;
            min-height: 70px;
            font-size: 0.8rem;
        }

        .field-group { margin-bottom: 18px; }

        .btn-row {
            display: flex;
            gap: 10px;
            margin-top: 6px;
        }

        button {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 12px;
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.15s, opacity 0.2s;
        }

        button:active { transform: scale(0.97); }

        .btn-primary {
            background: linear-gradient(135deg, #7c3aed, #6366f1);
            color: #fff;
        }
        .btn-primary:hover { opacity: 0.9; }

        .btn-save {
            background: linear-gradient(135deg, #059669, #10b981);
            color: #fff;
            flex: 0.5;
        }
        .btn-save:hover { opacity: 0.9; }

        .btn-primary:disabled, .btn-save:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Status indicator */
        .token-status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.75rem;
            color: #9ca3af;
            margin-bottom: 10px;
        }

        .dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: #ef4444;
            animation: pulse 2s infinite;
        }
        .dot.active { background: #10b981; }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        /* Result area */
        .result-box {
            margin-top: 20px;
            display: none;
        }

        .result-box.show { display: block; }

        .result-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .result-header h3 {
            font-size: 0.9rem;
            font-weight: 600;
            color: #60a5fa;
        }

        .result-badge {
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
        }
        .badge-success { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .badge-error { background: rgba(239, 68, 68, 0.2); color: #f87171; }

        .result-content {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px;
            max-height: 400px;
            overflow-y: auto;
        }

        .result-content pre {
            white-space: pre-wrap;
            word-break: break-all;
            font-size: 0.82rem;
            line-height: 1.6;
            color: #d1d5db;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
        }

        /* Info card for FB result */
        .fb-info {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px;
            background: rgba(99, 102, 241, 0.08);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 14px;
            margin-bottom: 12px;
        }

        .fb-avatar {
            width: 64px; height: 64px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #6366f1;
        }

        .fb-details h4 {
            font-size: 1.05rem;
            font-weight: 600;
            color: #e0e7ff;
            margin-bottom: 4px;
        }

        .fb-details p {
            font-size: 0.8rem;
            color: #9ca3af;
        }

        .fb-details a {
            color: #60a5fa;
            text-decoration: none;
            font-size: 0.8rem;
        }
        .fb-details a:hover { text-decoration: underline; }

        /* Spinner */
        .spinner {
            display: none;
            width: 20px; height: 20px;
            border: 2px solid rgba(255,255,255,0.2);
            border-top-color: #a78bfa;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            margin: 0 auto;
        }
        .spinner.active { display: inline-block; }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* Toast */
        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(80px);
            background: rgba(16, 185, 129, 0.95);
            color: #fff;
            padding: 12px 28px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 999;
        }
        .toast.error { background: rgba(239, 68, 68, 0.95); }
        .toast.visible {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    </style>
</head>
<body>

<div class="container">
    <div class="card">
        <h1>🔍 FB Number Lookup</h1>
        <p class="subtitle">Tìm thông tin Facebook từ số điện thoại</p>

        <!-- Token Section -->
        <div class="field-group">
            <label>Bearer Token</label>
            <div class="token-status">
                <span class="dot" id="tokenDot"></span>
                <span id="tokenLabel">Chưa có token</span>
            </div>
            <textarea id="tokenInput" placeholder="Dán Bearer token vào đây..."></textarea>
            <div class="btn-row" style="margin-top: 10px;">
                <button class="btn-save" id="btnSaveToken" onclick="saveToken()">💾 Lưu Token</button>
            </div>
        </div>

        <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 22px 0;">

        <!-- Search Section -->
        <div class="field-group">
            <label>Số điện thoại</label>
            <input type="text" id="phoneInput" placeholder="VD: 0912185198" 
                   onkeydown="if(event.key==='Enter') searchPhone()">
        </div>
        <div class="btn-row">
            <button class="btn-primary" id="btnSearch" onclick="searchPhone()">
                <span id="btnSearchText">🔎 Tra cứu</span>
                <span class="spinner" id="searchSpinner"></span>
            </button>
        </div>

        <!-- Result -->
        <div class="result-box" id="resultBox">
            <div class="result-header">
                <h3>📋 Kết quả</h3>
                <span class="result-badge" id="resultBadge"></span>
            </div>
            <div id="fbCard"></div>
            <div class="result-content">
                <pre id="resultPre"></pre>
            </div>
        </div>
    </div>
</div>

<div class="toast" id="toast"></div>

<script>
    // Load token on page load
    window.addEventListener('DOMContentLoaded', () => {
        fetch('/api/token')
            .then(r => r.json())
            .then(data => {
                if (data.token_preview) {
                    document.getElementById('tokenDot').classList.add('active');
                    document.getElementById('tokenLabel').textContent = 'Token đã thiết lập (' + data.length + ' ký tự)';
                    document.getElementById('tokenInput').placeholder = data.token_preview;
                }
            });
    });

    function showToast(msg, isError = false) {
        const t = document.getElementById('toast');
        t.textContent = msg;
        t.className = 'toast' + (isError ? ' error' : '');
        requestAnimationFrame(() => t.classList.add('visible'));
        setTimeout(() => t.classList.remove('visible'), 2500);
    }

    function saveToken() {
        const token = document.getElementById('tokenInput').value.trim();
        if (!token) { showToast('Vui lòng nhập token!', true); return; }

        const btn = document.getElementById('btnSaveToken');
        btn.disabled = true;

        fetch('/api/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token })
        })
        .then(r => r.json())
        .then(data => {
            showToast('✅ ' + data.message);
            document.getElementById('tokenDot').classList.add('active');
            document.getElementById('tokenLabel').textContent = 'Token đã thiết lập';
            document.getElementById('tokenInput').value = '';
            document.getElementById('tokenInput').placeholder = token.substring(0, 20) + '...' + token.slice(-10);
        })
        .catch(() => showToast('Lỗi lưu token!', true))
        .finally(() => btn.disabled = false);
    }

    function searchPhone() {
        const phone = document.getElementById('phoneInput').value.trim();
        if (!phone) { showToast('Vui lòng nhập số điện thoại!', true); return; }

        const btn = document.getElementById('btnSearch');
        const spinner = document.getElementById('searchSpinner');
        const btnText = document.getElementById('btnSearchText');

        btn.disabled = true;
        btnText.style.display = 'none';
        spinner.classList.add('active');

        fetch('/api/search?phone=' + encodeURIComponent(phone))
            .then(r => r.json())
            .then(data => {
                const box = document.getElementById('resultBox');
                const badge = document.getElementById('resultBadge');
                const pre = document.getElementById('resultPre');
                const fbCard = document.getElementById('fbCard');

                box.classList.add('show');
                fbCard.innerHTML = '';

                if (data.status_code === 200 && data.data) {
                    badge.textContent = 'Thành công';
                    badge.className = 'result-badge badge-success';

                    // Try to render a nice FB card if data has uid/name
                    const d = data.data?.data || data.data;
                    if (d && (d.uid || d.name)) {
                        const avatarUrl = d.uid ? 'https://graph.facebook.com/' + d.uid + '/picture?type=large' : '';
                        const fbUrl = d.uid ? 'https://facebook.com/' + d.uid : '#';
                        fbCard.innerHTML = `
                            <div class="fb-info">
                                ${avatarUrl ? '<img class="fb-avatar" src="' + avatarUrl + '" onerror="this.style.display=\\'none\\'">' : ''}
                                <div class="fb-details">
                                    <h4>${d.name || 'N/A'}</h4>
                                    <p>UID: ${d.uid || 'N/A'}</p>
                                    <a href="${fbUrl}" target="_blank">Xem trên Facebook ↗</a>
                                </div>
                            </div>`;
                    }
                } else {
                    badge.textContent = 'Status ' + (data.status_code || 'Error');
                    badge.className = 'result-badge badge-error';
                }

                pre.textContent = JSON.stringify(data, null, 2);
            })
            .catch(err => {
                document.getElementById('resultBox').classList.add('show');
                document.getElementById('resultBadge').textContent = 'Lỗi';
                document.getElementById('resultBadge').className = 'result-badge badge-error';
                document.getElementById('fbCard').innerHTML = '';
                document.getElementById('resultPre').textContent = 'Lỗi: ' + err.message;
            })
            .finally(() => {
                btn.disabled = false;
                btnText.style.display = 'inline';
                spinner.classList.remove('active');
            });
    }
</script>

</body>
</html>
"""

# ─── ROUTES ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Trang chủ - UI tra cứu."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/token", methods=["POST"])
def update_token():
    """Cập nhật Bearer token."""
    data = request.get_json()
    if not data or "token" not in data:
        return jsonify({"error": "Thiếu trường 'token' trong body"}), 400

    TOKEN_STORE["bearer_token"] = data["token"]
    return jsonify({"message": "Token đã được cập nhật thành công"}), 200


@app.route("/api/token", methods=["GET"])
def get_token():
    """Xem token hiện tại (ẩn bớt để bảo mật)."""
    token = TOKEN_STORE["bearer_token"]
    if not token:
        return jsonify({"token": None, "message": "Chưa có token nào được thiết lập"}), 200

    masked = token[:20] + "..." + token[-10:] if len(token) > 30 else token
    return jsonify({"token_preview": masked, "length": len(token)}), 200


@app.route("/api/search", methods=["GET"])
def search_phone():
    """Tìm thông tin Facebook từ số điện thoại."""
    phone = request.args.get("phone")
    if not phone:
        return jsonify({"error": "Thiếu tham số 'phone'"}), 400

    token = TOKEN_STORE["bearer_token"]
    if not token:
        return jsonify({"error": "Chưa thiết lập Bearer token. Hãy gọi POST /api/token trước"}), 401

    headers = {**HEADERS_TEMPLATE, "authorization": f"Bearer {token}"}

    try:
        resp = requests.get(
            FBNUMBER_API_URL,
            params={"searchPhone": phone},
            headers=headers,
            timeout=30,
        )
        return jsonify({
            "status_code": resp.status_code,
            "data": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text,
        }), resp.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request tới fbnumber.com bị timeout"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Lỗi kết nối: {str(e)}"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5559, debug=True)
