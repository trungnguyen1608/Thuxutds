from flask import Flask, request, redirect, url_for, render_template_string, flash, jsonify
import json, os
from datetime import datetime
import validators
import uuid

DATA_FILE = "fb_channels.json"
APP_SECRET = "change_this_secret_local_only"

app = Flask(__name__)
app.secret_key = APP_SECRET

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

TEMPLATE = """
<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>FB Sub Swap Board</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;max-width:980px;margin:18px auto;padding:12px;}
.card{border:1px solid #eee;padding:12px;border-radius:8px;margin-bottom:12px;background:#fff;}
form{margin-bottom:16px;padding:12px;border-radius:8px;background:#f8f9fa;border:1px solid #e9ecef;}
input[type=text], textarea, select{width:100%;padding:8px;margin:6px 0;border-radius:6px;border:1px solid #ccc}
button{padding:8px 12px;border-radius:6px;border:0;background:#007bff;color:#fff;cursor:pointer}
.small{font-size:13px;color:#666}
.counter{background:#e9ecef;padding:6px;border-radius:6px;display:inline-block;margin-left:8px}
.copybtn{margin-left:8px;padding:6px 8px;border-radius:6px;border:0;background:#6c757d;color:#fff;cursor:pointer}
.note{color:#333;background:#fff3cd;padding:10px;border-radius:6px;border:1px solid #ffeeba;margin-bottom:12px}
.actions{margin-top:8px}
</style>
<script>
function copyToClipboard(text){
  navigator.clipboard.writeText(text).then(()=>{ alert("Đã copy: "+text); }).catch(()=>{ alert("Không copy được"); });
}
function openAndMark(url, id){
  window.open(url, '_blank');
}
function markFollow(id){
  fetch('/confirm/'+id, {method:'POST'})
    .then(r=>r.json()).then(j=>{
      if(j.ok){
        document.getElementById('count-'+id).innerText = j.count;
      } else alert('Không thể ghi nhận');
    });
}
</script>
</head>
<body>
  <h1>FB Sub Swap Board</h1>
  <p class="note">Đăng link Facebook của bạn để người khác thấy. Mọi hành động follow/like phải do người dùng thực hiện thủ công. Không hỗ trợ bot.</p>

  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <ul>
      {% for m in messages %}
        <li style="color:green">{{ m }}</li>
      {% endfor %}
      </ul>
    {% endif %}
  {% endwith %}

  <form method="post" action="{{ url_for('add') }}">
    <label>Tên (nickname)</label>
    <input name="name" required maxlength="120" placeholder="Ví dụ: Trungdz">

    <label>Link Facebook (profile hoặc page) — bắt đầu bằng http/https</label>
    <input name="url" required placeholder="https://www.facebook.com/yourpage">

    <label>Mô tả ngắn</label>
    <textarea name="desc" rows="3" maxlength="400" placeholder="Nội dung kênh, call-to-action"></textarea>

    <div style="margin-top:8px">
      <button type="submit">Đăng kênh</button>
    </div>
  </form>

  <h2>Danh sách kênh</h2>
  {% if channels %}
    {% for c in channels|reverse %}
      <div class="card">
        <strong>{{ c.name }}</strong> · <span class="small">{{ c.when }}</span>
        <div style="margin-top:6px">{{ c.desc or '' }}</div>

        <div class="actions">
          <button onclick="openAndMark('{{ c.url }}','{{ c.id }}')">Mở kênh</button>
          <button class="copybtn" onclick="copyToClipboard('{{ c.url }}')">Copy link</button>
          <button style="background:#28a745;margin-left:8px" onclick="markFollow('{{ c.id }}')">Tôi đã sub</button>
          <span class="counter">Đã được xác nhận: <strong id="count-{{ c.id }}">{{ c.count }}</strong></span>
          <a href="{{ url_for('remove', id=c.id) }}" onclick="return confirm('Xoá kênh?')" style="margin-left:12px"><button style="background:#dc3545">Xóa</button></a>
        </div>
      </div>
    {% endfor %}
  {% else %}
    <p>Chưa có kênh nào. Hãy đăng kênh của bạn!</p>
  {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    channels = load_data()
    return render_template_string(TEMPLATE, channels=channels)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name","").strip()
    url = request.form.get("url","").strip()
    desc = request.form.get("desc","").strip()
    if not name or not url:
        flash("Tên và URL bắt buộc")
        return redirect(url_for("index"))
    if not validators.url(url):
        flash("URL không hợp lệ. Bắt đầu bằng http:// hoặc https://")
        return redirect(url_for("index"))
    if "facebook.com" not in url.lower():
        flash("Vui lòng cung cấp link Facebook (facebook.com)")
        return redirect(url_for("index"))
    data = load_data()
    item = {
        "id": str(uuid.uuid4()),
        "name": name,
        "url": url,
        "desc": desc,
        "when": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": 0
    }
    data.append(item)
    save_data(data)
    flash("Đã đăng kênh!")
    return redirect(url_for("index"))

@app.route("/confirm/<id>", methods=["POST"])
def confirm(id):
    data = load_data()
    for it in data:
        if it["id"] == id:
            it["count"] = it.get("count",0) + 1
            save_data(data)
            return jsonify({"ok":True,"count":it["count"]})
    return jsonify({"ok":False}), 404

@app.route("/remove/<id>")
def remove(id):
    data = load_data()
    new = [it for it in data if it["id"] != id]
    save_data(new)
    flash("Đã xóa (nếu tồn tại)." )
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
