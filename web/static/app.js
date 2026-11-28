"use strict";
(function () {
  var $ = function (s) { return document.querySelector(s); };
  var KEY = { conv: "nvqs.conversations", saved: "nvqs.saved", theme: "nvqs.theme", size: "nvqs.size", cur: "nvqs.current" };
  var THEMES = [["light", "Sáng"], ["dark", "Tối"], ["sepia", "Đọc sách"], ["contrast", "Tương phản cao"], ["gray", "Xám dịu"], ["auto", "Theo thiết bị"]];
  var SIZES = [["sm", "Nhỏ"], ["md", "Vừa"], ["lg", "Lớn"]];
  var info = { mode: "", max_chars: 4000, wait_s: 90 };
  var storageOk = true, storageWarned = false;
  var convs = [], saved = [], curId = null, busy = false, lastCites = [];

  /* ---------- lưu trữ an toàn ---------- */
  function warn(msg) { var n = $("#notice"); n.textContent = msg; n.hidden = false; }
  function read(k, def) {
    try { var v = localStorage.getItem(k); return v == null ? def : JSON.parse(v); }
    catch (e) { warn("Dữ liệu đã lưu trên trình duyệt bị hỏng hoặc không đọc được, đã bỏ qua phần đó."); return def; }
  }
  function write(k, v) {
    try { localStorage.setItem(k, typeof v === "string" ? v : JSON.stringify(v)); return true; }
    catch (e) {
      storageOk = false;
      if (!storageWarned) { storageWarned = true; warn("Không lưu được vào trình duyệt (bị chặn hoặc đầy). Chat vẫn chạy nhưng lịch sử, mục đã lưu và cài đặt có thể không được giữ."); }
      return false;
    }
  }
  function readRaw(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function persist() { write(KEY.conv, convs); write(KEY.saved, saved); write(KEY.cur, curId || ""); }
  function uid() { return (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2); }
  function fmt(t) { try { return new Date(t).toLocaleString("vi-VN"); } catch (e) { return ""; } }

  /* ---------- chọn thiết kế #1 / #2 ---------- */
  var DESIGN = document.documentElement.getAttribute("data-design") || "main";
  KEY.design = "nvqs.design";
  var pref = readRaw(KEY.design);
  if ((pref === "main" || pref === "legacy") && pref !== DESIGN) { location.replace(pref === "legacy" ? "/legacy" : "/"); return; }
  var dsw = $("#design-switch");
  if (dsw) {
    dsw.textContent = DESIGN === "legacy" ? "Chuyển sang giao diện mới" : "Chuyển sang giao diện cũ";
    dsw.addEventListener("click", function () { var to = DESIGN === "legacy" ? "main" : "legacy"; write(KEY.design, to); location.href = to === "legacy" ? "/legacy" : "/"; });
  }

  /* ---------- giao diện ---------- */
  function applyTheme(t) {
    var eff = t === "auto" ? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light") : t;
    document.documentElement.setAttribute("data-theme", eff);
  }
  function applySize(s) { document.documentElement.setAttribute("data-size", s); }
  function pill(box, list, cur, onPick) {
    box.textContent = "";
    list.forEach(function (it) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "opt"; b.textContent = it[1];
      b.setAttribute("aria-pressed", String(it[0] === cur));
      b.addEventListener("click", function () { onPick(it[0]); });
      box.appendChild(b);
    });
  }
  var theme = readRaw(KEY.theme) || "light", size = readRaw(KEY.size) || "md";
  if (!THEMES.some(function (x) { return x[0] === theme; })) theme = "light";
  if (!SIZES.some(function (x) { return x[0] === size; })) size = "md";
  function drawSettings() {
    pill($("#themes"), THEMES, theme, function (v) { theme = v; write(KEY.theme, v); applyTheme(v); drawSettings(); });
    pill($("#sizes"), SIZES, size, function (v) { size = v; write(KEY.size, v); applySize(v); drawSettings(); });
  }
  applyTheme(theme); applySize(size);
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () { if (theme === "auto") applyTheme("auto"); });

  /* ---------- hiển thị câu trả lời (chỉ textContent, không innerHTML) ---------- */
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  var KEYS = /^(Giải thích|Cần biết thêm|Việc cần làm|Nguồn|Tham khảo[^:]*|Lưu ý|LOI):\s*(.*)$/;
  function renderBody(box, output, refs) {
    refs = refs || {};
    var lines = output.split("\n");
    if (/^NHAN:/.test(lines[0]) && /^CAN_CU:/.test(lines[1] || "")) lines = lines.slice(2);
    var ul = null;
    lines.forEach(function (ln) {
      if (!ln.trim()) { ul = null; return; }
      if (/^\s*-\s+/.test(ln)) {
        if (!ul) { ul = el("ul"); box.appendChild(ul); }
        var item = ln.replace(/^\s*-\s+/, ""), mm = item.match(/^([\w.-]+) — (.*)$/), li = el("li");
        if (mm && refs[mm[1]]) {
          var rf = refs[mm[1]], dt = mm[2].match(/kiểm tra ngày [\d\/]+/);
          if (rf.url) { var a = el("a", "", rf.ten); a.href = rf.url; a.target = "_blank"; a.rel = "noopener noreferrer"; li.appendChild(a); }
          else li.appendChild(document.createTextNode(rf.ten));
          if (dt) li.appendChild(document.createTextNode(" · " + dt[0]));
        } else li.textContent = item;
        ul.appendChild(li); return;
      }
      ul = null;
      var m = ln.match(KEYS), p = el("p");
      if (m && m[1] === "Lưu ý") {
        p.className = "note";
        var cut = m[2].indexOf(". "), head = cut > 0 ? m[2].slice(0, cut + 1) : m[2], rest = cut > 0 ? m[2].slice(cut + 2) : "";
        p.appendChild(el("span", "k", "Lưu ý: ")); p.appendChild(document.createTextNode(head));
        if (rest) { var dd = el("details", "more"); dd.appendChild(el("summary", "", "Xem thêm")); dd.appendChild(el("span", "", rest)); p.appendChild(dd); }
      } else if (m) { p.appendChild(el("span", "k", m[1] + ": ")); p.appendChild(document.createTextNode(m[2])); }
      else p.textContent = ln;
      box.appendChild(p);
    });
  }
  function citeNodes(cites) {
    var wrap = el("div", "cites");
    cites.forEach(function (c) {
      var n;
      if (c.url) { n = el("a", "cite", c.ten); n.href = c.url; n.target = "_blank"; n.rel = "noopener noreferrer"; n.title = c.id; }
      else { n = el("span", "cite", c.ten); n.title = c.id; }
      wrap.appendChild(n);
    });
    return wrap;
  }
  var HELP_QS = ["Em đang học đại học chính quy, có thể được xem xét tạm hoãn không?", "Em học cao đẳng hệ chính quy, tạm hoãn gọi nhập ngũ cần điều kiện gì?", "Em đã học xong đại học và muốn học thêm thạc sĩ, có được tạm hoãn không?"];
  function followUp(m) {
    var f = el("div", "follow");
    f.appendChild(el("p", "k", "Mình hỗ trợ tốt nhất câu hỏi về tạm hoãn vì học tập. Bạn có thể thử:"));
    var row = el("div", "follow-row");
    HELP_QS.forEach(function (q) {
      var c = el("button", "chip-q small", q); c.type = "button";
      c.addEventListener("click", function () { show("chat"); var i = $("#input"); i.value = q; autosize(); i.focus(); });
      row.appendChild(c);
    });
    f.appendChild(row);
    var src = el("button", "mini", "Xem nguồn dữ liệu của trợ lý"); src.type = "button";
    src.addEventListener("click", function () { lastCites = m.cites || []; drawCited(); openSources(true); });
    f.appendChild(src);
    return f;
  }
  function botBubble(m, opts) {
    opts = opts || {};
    var li = el("li", "m bot"), b = el("div", "bubble");
    var err = m.error || /^LOI:/.test(m.text || "");
    if (err) b.appendChild(el("div", "label err", "Lỗi"));
    if (m.error) b.appendChild(el("p", "", m.text));
    else renderBody(b, m.text, m.refs);
    if (m.cites && m.cites.length) {
      b.appendChild(el("div", "k", "Căn cứ agent trả về:"));
      b.appendChild(citeNodes(m.cites));
    }
    li.appendChild(b);
    if (!m.error && !opts.readonly && (m.nhan === "out_of_scope" || m.nhan === "refuse")) li.appendChild(followUp(m));
    if (!m.error && !opts.readonly) {
      var a = el("div", "acts");
      var sv = el("button", "mini", isSaved(m.id) ? "Bỏ lưu" : "Lưu");
      sv.type = "button"; sv.setAttribute("aria-pressed", String(isSaved(m.id)));
      sv.addEventListener("click", function () { toggleSave(m); sv.textContent = isSaved(m.id) ? "Bỏ lưu" : "Lưu"; sv.setAttribute("aria-pressed", String(isSaved(m.id))); });
      a.appendChild(sv);
      li.appendChild(a);
    }
    return li;
  }

  /* ---------- hội thoại ---------- */
  function cur() { return convs.filter(function (c) { return c.id === curId; })[0] || null; }
  function newConv() { curId = null; drawChat(); }
  function drawChat() {
    var c = cur(), box = $("#msgs"); box.textContent = "";
    $("#welcome").hidden = !!(c && c.msgs.length);
    if (c) c.msgs.forEach(function (m) {
      if (m.role === "user") { var li = el("li", "m user"); li.appendChild(el("div", "bubble", m.text)); box.appendChild(li); }
      else box.appendChild(botBubble(m));
    });
    scrollEnd();
  }
  function scrollEnd() { var s = $("#scroll"); s.scrollTop = s.scrollHeight; }

  function setBusy(v) { busy = v; $("#send").disabled = v; $("#input").readOnly = v; }

  function ensureConv(q) {
    var c = cur();
    if (!c) { c = { id: uid(), title: q.slice(0, 60), created: Date.now(), msgs: [] }; convs.unshift(c); curId = c.id; }
    return c;
  }

  function send(q, retryNode) {
    if (busy) return;
    q = (q || "").trim();
    if (!q) return;
    if (q.length > info.max_chars) { warn("Câu hỏi dài quá " + info.max_chars + " ký tự. Hãy rút gọn."); return; }
    $("#notice").hidden = !storageWarned;
    var c = ensureConv(q);
    if (retryNode) retryNode.remove();
    else c.msgs.push({ role: "user", text: q, time: Date.now() });
    $("#welcome").hidden = true;
    if (!retryNode) { var u = el("li", "m user"); u.appendChild(el("div", "bubble", q)); $("#msgs").appendChild(u); }
    var wait = el("li", "m bot"); var wb = el("div", "bubble wait", "Đang xử lý… (có thể mất vài giây)");
    wait.appendChild(wb); $("#msgs").appendChild(wait); scrollEnd();
    $("#input").value = ""; autosize(); setBusy(true);
    var ctl = new AbortController(), timer = setTimeout(function () { ctl.abort(); }, (info.wait_s + 15) * 1000);
    fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: q, session_id: c.id }), signal: ctl.signal })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        wait.remove();
        if (res.ok && typeof res.j.output === "string") {
          var m = { role: "bot", id: uid(), text: res.j.output, nhan: res.j.nhan || "", cites: res.j.citations || [], refs: res.j.refs || {}, time: Date.now(), q: q };
          c.msgs.push(m); persist(); $("#msgs").appendChild(botBubble(m)); lastCites = m.cites; drawCited();
        } else fail(res.j && res.j.error || "Có lỗi, hãy thử lại.", q);
      })
      .catch(function (e) { wait.remove(); fail(e && e.name === "AbortError" ? "Quá thời gian chờ. Hãy thử lại." : "Không kết nối được máy chủ. Hãy kiểm tra và thử lại.", q); })
      .then(function () { clearTimeout(timer); setBusy(false); persist(); scrollEnd(); $("#input").focus(); });
  }
  function fail(msg, q) {
    var li = botBubble({ error: true, text: msg });
    var rt = el("button", "mini retry", "Thử lại"); rt.type = "button";
    rt.addEventListener("click", function () { send(q, li); });
    li.querySelector(".bubble").appendChild(rt);
    $("#msgs").appendChild(li);
    $("#input").value = q; autosize();
  }

  /* ---------- đã lưu ---------- */
  function isSaved(id) { return saved.some(function (s) { return s.id === id; }); }
  function toggleSave(m) {
    if (isSaved(m.id)) saved = saved.filter(function (s) { return s.id !== m.id; });
    else saved.unshift({ id: m.id, q: m.q || "", text: m.text, nhan: m.nhan || "", cites: m.cites || [], refs: m.refs || {}, time: Date.now() });
    persist();
  }

  /* ---------- xác nhận xóa ---------- */
  function confirmDel(text, yes) {
    var d = $("#confirm"); $("#confirm-text").textContent = text;
    if (!d.showModal) { if (window.confirm(text)) yes(); return; }
    d.returnValue = ""; d.onclose = function () { if (d.returnValue === "yes") yes(); };
    d.showModal();
  }

  /* ---------- danh sách lịch sử / đã lưu ---------- */
  function drawHistory() {
    var ul = $("#hist-list"); ul.textContent = "";
    if (!convs.length) { ul.appendChild(el("li", "empty", "Chưa có cuộc trò chuyện nào.")); return; }
    convs.forEach(function (c) {
      var li = el("li"), t = el("div", "t");
      t.appendChild(el("div", "", c.title || "(không tiêu đề)")); t.appendChild(el("div", "sub", fmt(c.created) + " · " + c.msgs.length + " tin nhắn"));
      var open = el("button", "btn", "Mở"); open.type = "button";
      open.addEventListener("click", function () { curId = c.id; persist(); show("chat"); });
      var del = el("button", "btn danger", "Xóa"); del.type = "button";
      del.addEventListener("click", function () {
        confirmDel("Xóa cuộc trò chuyện này?", function () { convs = convs.filter(function (x) { return x.id !== c.id; }); if (curId === c.id) curId = null; persist(); drawHistory(); });
      });
      var r = el("div", "opts"); r.appendChild(open); r.appendChild(del);
      li.appendChild(t); li.appendChild(r); ul.appendChild(li);
    });
  }
  function drawSaved() {
    var ul = $("#saved-list"); ul.textContent = "";
    if (!saved.length) { ul.appendChild(el("li", "empty", "Chưa lưu câu trả lời nào.")); return; }
    saved.forEach(function (s) {
      var li = el("li"), d = el("details", "t");
      d.appendChild(el("summary", "", s.q || "(không có câu hỏi)"));
      var holder = el("ul", "msgs-ro"); holder.appendChild(botBubble({ id: s.id, text: s.text, nhan: s.nhan, cites: s.cites, refs: s.refs }, { readonly: true }));
      holder.style.listStyle = "none"; holder.style.padding = "0";
      d.appendChild(holder);
      var un = el("button", "btn", "Bỏ lưu"); un.type = "button";
      un.addEventListener("click", function () { saved = saved.filter(function (x) { return x.id !== s.id; }); persist(); drawSaved(); });
      li.appendChild(d); li.appendChild(un); ul.appendChild(li);
    });
  }

  /* ---------- nguồn tham khảo ---------- */
  function drawCited() {
    var box = $("#src-cited"); box.textContent = "";
    if (!lastCites.length) { box.appendChild(el("p", "hint", "Câu trả lời gần nhất không trích căn cứ cụ thể nào.")); return; }
    box.appendChild(el("h3", "", "Căn cứ trong câu trả lời gần nhất")); box.appendChild(citeNodes(lastCites));
  }
  function drawSources(list) {
    var ul = $("#src-list"); ul.textContent = "";
    list.forEach(function (s) {
      var li = el("li", "src"), t = el("div", "t");
      t.appendChild(el("div", "", s.ten)); t.appendChild(el("div", "sub", s.so_hieu + (s.hieu_luc ? " · " + s.hieu_luc : "")));
      if (s.url) { var a = el("a", "", "Mở văn bản gốc"); a.href = s.url; a.target = "_blank"; a.rel = "noopener noreferrer"; t.appendChild(a); }
      else t.appendChild(el("div", "sub", "(không có liên kết)"));
      li.appendChild(t); ul.appendChild(li);
    });
    if (!list.length) ul.appendChild(el("li", "empty", "Không tải được danh mục nguồn."));
  }
  function openSources(open) {
    var s = $("#sources"); s.hidden = !open; $("#src-btn").setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("src", open); $("#scrim").hidden = !open && !document.body.classList.contains("menu");
  }

  /* ---------- điều hướng ---------- */
  function show(view) {
    ["chat", "history", "saved", "settings"].forEach(function (v) { $("#view-" + v).hidden = v !== view; });
    document.querySelectorAll(".rail-btn").forEach(function (b) { b.setAttribute("aria-current", String(b.dataset.view === view)); });
    if (view === "chat") drawChat(); if (view === "history") drawHistory(); if (view === "saved") drawSaved(); if (view === "settings") drawSettings();
    document.body.classList.remove("menu"); $("#scrim").hidden = !document.body.classList.contains("src");
  }
  function autosize() { var t = $("#input"); t.style.height = "auto"; var h = Math.min(t.scrollHeight, 160); t.style.height = h + "px"; t.style.overflowY = t.scrollHeight > 160 ? "auto" : "hidden"; }

  /* ---------- khởi động ---------- */
  convs = read(KEY.conv, []); saved = read(KEY.saved, []);
  if (!Array.isArray(convs)) convs = []; if (!Array.isArray(saved)) saved = [];
  convs = convs.filter(function (c) { return c && c.id && Array.isArray(c.msgs); });
  saved = saved.filter(function (s) { return s && s.id && typeof s.text === "string"; });
  curId = null;  // luôn mở phiên mới khi tải lại; phiên cũ nằm ở Lịch sử

  document.querySelectorAll(".rail-btn").forEach(function (b) { b.addEventListener("click", function () { show(b.dataset.view); }); });
  document.querySelectorAll(".chip-q").forEach(function (b) { b.addEventListener("click", function () { var i = $("#input"); i.value = b.textContent; autosize(); i.focus(); }); });
  $("#composer").addEventListener("submit", function (e) { e.preventDefault(); send($("#input").value); });
  $("#input").addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); send($("#input").value); } });
  $("#input").addEventListener("input", autosize);
  $("#src-btn").addEventListener("click", function () { openSources($("#sources").hidden); });
  $("#src-close").addEventListener("click", function () { openSources(false); });
  $("#scrim").addEventListener("click", function () { document.body.classList.remove("menu"); openSources(false); });
  $("#menu-btn").addEventListener("click", function () { document.body.classList.add("menu"); $("#scrim").hidden = false; });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { openSources(false); document.body.classList.remove("menu"); } });
  $("#new-chat").addEventListener("click", function () { newConv(); show("chat"); });
  $("#clear-hist").addEventListener("click", function () { confirmDel("Xóa toàn bộ lịch sử trò chuyện trên trình duyệt này?", function () { convs = []; curId = null; persist(); warn("Đã xóa lịch sử."); }); });
  $("#clear-saved").addEventListener("click", function () { confirmDel("Xóa toàn bộ mục đã lưu trên trình duyệt này?", function () { saved = []; persist(); warn("Đã xóa mục đã lưu."); }); });

  fetch("/api/info").then(function (r) { return r.json(); }).then(function (j) {
    info = j;
    if (j.memory) {
      $("#count").textContent = "Enter để gửi, Shift+Enter xuống dòng. Mình nhớ các câu trước trong cuộc trò chuyện này.";
      document.querySelectorAll("#privacy li").forEach(function (li) { if (/xử lý độc lập/.test(li.textContent)) li.textContent = "Mình nhớ các câu trước trong cuộc trò chuyện này; bấm “Cuộc trò chuyện mới” để bắt đầu lại từ đầu."; });
    }
    if (j.mode === "fake") { var b = $("#mode-badge"); b.textContent = "Model giả (chưa phải model thật)"; b.hidden = false; }
    $("#input").maxLength = j.max_chars;
  }).catch(function () {});
  fetch("/api/sources").then(function (r) { return r.json(); }).then(function (j) { drawSources(j.sources || []); }).catch(function () { drawSources([]); });
  drawCited(); show("chat");
})();
