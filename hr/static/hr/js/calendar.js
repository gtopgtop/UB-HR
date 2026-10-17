// Calendar and time record on the Attendance page. The layout and behaviour follow the
// Academic Calendar handoff: month grid with multi-day strips (§7.4), day panel, "This Year"
// strip, all-events list, colour overrides (§7.2), CSV (§8.14) and print (§8.15). Your
// daily time record is its attendance layer (§10, adapted: one person, not a school).
// Prototype only: your own events live in memory, so a reload resets them. Colours and the
// two layer toggles are remembered in this browser.
(() => {
  const root = document.querySelector("[data-calendar]");
  if (!root) return;
  const data = JSON.parse(document.getElementById("calendar-data").textContent);

  const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
    "October", "November", "December"];
  const DAYS_SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const SY_ORDER = [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5]; // July to June
  const PERSONAL = "personal";
  const MAX_SLOTS = 3;

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const store = {
    get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* a blocked store keeps it for this visit only */ } },
  };
  const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;
  const $ = (sel) => root.querySelector(sel);

  // ── Event types and per-browser colour overrides (handoff §7.2) ──
  const COLOR_KEY = "cal_event_colors";
  const HEX = /^#[0-9a-f]{6}$/i;
  function loadOverrides() {
    try {
      const saved = JSON.parse(store.get(COLOR_KEY) ?? "{}");
      return Object.fromEntries(Object.entries(saved).filter(([, v]) => HEX.test(v)));
    } catch { return {}; }
  }
  function tints(hex) {
    const ch = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
    const mix = (t) => `#${ch.map((v) => Math.round(v + (255 - v) * t).toString(16).padStart(2, "0")).join("")}`;
    return { bg: mix(0.82), light: mix(0.93) };
  }
  const buildTypes = (over) => data.types.map((t) => {
    const color = over[t.value] ?? t.color;
    return { ...t, color, ...tints(color) };
  });
  let overrides = loadOverrides();
  let TYPES = buildTypes(overrides);
  const meta = (type) => TYPES.find((t) => t.value === type) ?? TYPES.find((t) => t.value === "other");
  const evStyle = (m) => `--ev:${m.color};--ev-bg:${m.bg};--ev-light:${m.light}`;
  const schoolTypes = () => TYPES.filter((t) => t.value !== PERSONAL);

  // ── Dates (handoff §7.3). Strings are parsed as local dates, never as UTC. ──
  const parse = (s) => { const [y, m, d] = s.split("-").map(Number); return new Date(y, m - 1, d); };
  const iso = (y, m, d) => `${y}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
  const keyOf = (d) => iso(d.getFullYear(), d.getMonth(), d.getDate());
  const shortDate = (d) => `${MONTHS[d.getMonth()].slice(0, 3)} ${d.getDate()}`;
  function formatRange(start, end) {
    const s = parse(start);
    if (start === end) return shortDate(s);
    const e = parse(end);
    if (s.getMonth() === e.getMonth()) return `${shortDate(s)}–${e.getDate()}`;
    return `${shortDate(s)} – ${shortDate(e)}`;
  }
  function buildEventMap(list) {
    const map = {};
    for (const ev of list) {
      const end = parse(ev.end_date);
      for (const cur = parse(ev.start_date); cur <= end; cur.setDate(cur.getDate() + 1)) {
        (map[keyOf(cur)] ??= []).push(ev);
      }
    }
    return map;
  }

  const [y1, y2] = data.school_year.split("-").map(Number);
  const yearOf = (month) => (month >= 6 ? y1 : y2); // July–December: first year; January–June: second
  const bounds = { min: `${y1}-07-01`, max: `${y2}-06-30` };
  const today = data.today;
  const noWork = new Set(data.no_work_types);

  // ── State (handoff §8.1) ──
  const toggleKey = (name) => `fms.calendar.${name}`;
  const state = {
    mine: data.mine.map((ev) => ({ ...ev })),
    showMine: store.get(toggleKey("showMine")) !== "0",
    showAttendance: store.get(toggleKey("showAttendance")) !== "0",
    selectedDay: null,
    activeMonth: parse(today).getMonth(),
    printView: "list",
    search: "",
    filter: "",
    collapsed: new Set(),
    nextId: 1000,
  };

  // School events and your own as one list. Their ids come from different tables, so `uid`
  // tells them apart and `mine` says which one owns the row.
  const items = () => [
    ...data.events.map((ev) => ({ ...ev, uid: `school-${ev.event_id}`, mine: false })),
    ...(state.showMine ? state.mine.map((ev) => ({ ...ev, uid: `mine-${ev.event_id}`, mine: true, event_type: PERSONAL })) : []),
  ];

  // ── Attendance layer: your record for a day, never for a day after today ──
  const attendanceOn = () => state.showAttendance;
  const timeShort = (t) => (t ? t.replace(/\s?[AP]M$/, "") : "");
  function noteFor(k) {
    if (!attendanceOn() || k > today) return null;
    const rec = data.attendance[k];
    if (!rec) return null;
    const variant = { present: "success", late: "warning", leave: "info", absent: "error" }[rec.status] ?? "";
    const text = rec.time_in ? timeShort(rec.time_in) : rec.status === "leave" ? "Leave" : "Absent";
    const title = [rec.label, rec.time_in && `in ${rec.time_in}`, rec.time_out && `out ${rec.time_out}`, rec.still_in && "still in"]
      .filter(Boolean).join(" · ");
    return {
      title,
      html: `<span class="ds-badge s-sm v-${variant} cal-note" title="${esc(title)}"><i class="ti ti-user-check" aria-hidden="true"></i><span class="cal-note-text">${esc(text)}</span></span>`,
    };
  }
  const noWorkEvent = (k) => data.events.find((ev) => noWork.has(ev.event_type) && ev.start_date <= k && ev.end_date >= k);

  // ── Header ──
  function renderSub() {
    const mine = state.showMine && state.mine.length ? ` · ${state.mine.length} of yours` : "";
    $("[data-cal-sub]").textContent = `S.Y. ${data.school_year} · ${plural(data.events.length, "event")}${mine}`;
    root.querySelectorAll("[data-cal-toggle]").forEach((input) => {
      input.checked = state[input.dataset.calToggle];
      input.nextElementSibling.className = `ti ti-${input.checked ? input.dataset.on : input.dataset.off}`;
    });
  }

  // ── Month navigation (handoff §8.6) ──
  function renderMonthNav(animate) {
    const title = $("[data-cal-title]");
    title.innerHTML = `${MONTHS[state.activeMonth]} <span>${yearOf(state.activeMonth)}</span>`;
    if (animate) { title.classList.remove("is-entering"); void title.offsetWidth; title.classList.add("is-entering"); }
    $("[data-cal-pills]").innerHTML = SY_ORDER.map((m) =>
      `<button type="button" class="cal-month-pill" data-cal-month="${m}" aria-label="${MONTHS[m]} ${yearOf(m)}"${m === state.activeMonth ? ' aria-current="true"' : ""}>${MONTHS[m].slice(0, 3)}</button>`).join("");
  }

  // ── Month grid (handoff §7.4). Week by week, so a multi-day strip keeps one row (slot)
  // in every cell it crosses that week. ──
  function assignWeekSlots(weekDays, year, month, daysInMonth, map) {
    const slotMap = {};
    const occupied = [];
    for (const day of weekDays) {
      if (!day) continue;
      const k = iso(year, month, day);
      const evs = map[k] ?? [];
      for (const ev of evs) {
        if (slotMap[ev.uid] !== undefined) continue;
        let slot = 0;
        while (occupied[slot] !== undefined) slot++;
        occupied[slot] = ev.uid;
        slotMap[ev.uid] = slot;
      }
      for (const ev of evs) { // free the slots of events that end today
        if (ev.end_date === k || day === daysInMonth) {
          const slot = slotMap[ev.uid];
          if (occupied[slot] === ev.uid) delete occupied[slot];
        }
      }
    }
    return slotMap;
  }

  function stripHtml(ev, k, day, daysInMonth) {
    const m = meta(ev.event_type);
    const single = ev.start_date === ev.end_date;
    const isStart = ev.start_date === k;
    const isEnd = ev.end_date === k;
    const contStart = !isStart && day === 1; // began in an earlier month
    const contEnd = !isEnd && day === daysInMonth; // runs into the next month
    const showTitle = isStart || single || contStart;
    const cls = ["cal-strip", single ? "is-single" : "", isStart ? "is-start" : "", isEnd ? "is-end" : "",
      contStart ? "is-cont-start" : "", contEnd ? "is-cont-end" : "", showTitle ? "" : "is-quiet"].filter(Boolean).join(" ");
    return `<span class="${cls}" style="${evStyle(m)}">${contStart ? '<i class="ti ti-arrow-right is-flip" aria-hidden="true"></i>' : ""}<span>${showTitle ? esc(ev.title) : " "}</span>${contEnd ? '<i class="ti ti-arrow-right" aria-hidden="true"></i>' : ""}</span>`;
  }

  function renderGrid(animate) {
    const month = state.activeMonth;
    const year = yearOf(month);
    const map = buildEventMap(items());
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const weeks = [];
    let week = Array(firstDay).fill(null);
    for (let d = 1; d <= daysInMonth; d++) {
      week.push(d);
      if (week.length === 7) { weeks.push(week); week = []; }
    }
    if (week.length) { while (week.length < 7) week.push(null); weeks.push(week); }

    const head = DAYS_SHORT.map((d, i) => `<span class="${i === 0 || i === 6 ? "is-weekend" : ""}">${d}</span>`).join("");
    const body = weeks.map((weekDays) => {
      const slotMap = assignWeekSlots(weekDays, year, month, daysInMonth, map);
      const slots = Object.values(slotMap);
      const usedSlots = Math.min(MAX_SLOTS, slots.length ? Math.max(...slots) + 1 : 0);
      const cells = weekDays.map((day, ci) => {
        const weekend = ci === 0 || ci === 6;
        if (!day) return `<span class="cal-pad${weekend ? " is-weekend" : ""}" aria-hidden="true"></span>`;
        const k = iso(year, month, day);
        const evs = map[k] ?? [];
        const note = noteFor(k);
        const hasAny = evs.length > 0 || Boolean(note);
        const overflow = evs.filter((ev) => (slotMap[ev.uid] ?? MAX_SLOTS) >= MAX_SLOTS).length;
        const bySlot = {};
        for (const ev of evs) if (slotMap[ev.uid] < MAX_SLOTS) bySlot[slotMap[ev.uid]] = ev;
        const strips = Array.from({ length: usedSlots }, (_, slot) =>
          bySlot[slot] ? stripHtml(bySlot[slot], k, day, daysInMonth) : '<span class="cal-slot"></span>').join("");
        const label = [`${parse(k).toLocaleDateString("en-US", { weekday: "long" })}, ${MONTHS[month]} ${day}`,
          k === today && "today", evs.length && plural(evs.length, "event"), note && note.title].filter(Boolean).join(", ");
        const cls = ["cal-day", weekend && "is-weekend", k === today && "is-today", hasAny && "has-any"].filter(Boolean).join(" ");
        return `<button type="button" class="${cls}" data-date="${k}" aria-pressed="${state.selectedDay === k}" aria-label="${esc(label)}"${k === today ? ' aria-current="date"' : ""}>`
          + `<span class="cal-day-head"><span class="cal-num" aria-hidden="true">${day}</span>${note ? note.html : ""}</span>`
          + `<span class="cal-strips" aria-hidden="true">${strips}${overflow ? `<span class="cal-more">+${overflow} more</span>` : ""}</span></button>`;
      }).join("");
      return `<div class="cal-week">${cells}</div>`;
    }).join("");

    const holder = $("[data-cal-grid]");
    holder.innerHTML = `<div class="cal-grid${animate ? " is-entering" : ""}"><div class="cal-weekdays" aria-hidden="true">${head}</div>${body}</div>`;
  }

  // ── Legend and the month's attendance tally (handoff §8.7) ──
  function renderLegend() {
    const types = state.showMine ? TYPES : schoolTypes();
    const swatches = types.map((t) => `<span class="cal-legend-item"><span class="cal-swatch" style="${evStyle(t)}"></span>${esc(t.label)}</span>`).join("");
    const note = attendanceOn()
      ? '<span class="cal-legend-note"><i class="ti ti-user-check" aria-hidden="true"></i>Your time in · green: on time · amber: late · blue: on leave · red: absent</span>'
      : "";
    $("[data-cal-legend]").innerHTML = swatches + note;

    const tally = $("[data-cal-tally]");
    const year = yearOf(state.activeMonth);
    const prefix = iso(year, state.activeMonth, 1).slice(0, 8);
    tally.hidden = !attendanceOn() || `${prefix}01` > today;
    if (tally.hidden) return;
    const recs = Object.entries(data.attendance).filter(([k]) => k.startsWith(prefix)).map(([, r]) => r);
    const late = recs.filter((r) => r.status === "late");
    const rows = [
      ["Days present", recs.filter((r) => r.status === "present" || r.status === "late").length, "success"],
      ["Late", `${late.length} · ${late.reduce((n, r) => n + r.minutes_late, 0)} min`, "warning"],
      ["On leave", recs.filter((r) => r.status === "leave").length, "info"],
      ["Absent", recs.filter((r) => r.status === "absent").length, "error"],
    ];
    tally.setAttribute("aria-label", `Your attendance, ${MONTHS[state.activeMonth]} ${year}`);
    tally.innerHTML = rows.map(([label, value, tone]) =>
      `<li><span class="ds-dot d-${tone}"></span><span>${label}</span><strong>${value}</strong></li>`).join("");
  }

  // ── "This Year" strip (handoff §8.8) ──
  let statsShown = false;
  function renderStats() {
    const all = items();
    const rows = TYPES.map((t) => ({ ...t, count: all.filter((e) => e.event_type === t.value).length })).filter((t) => t.count);
    const box = $("[data-cal-stats]");
    box.closest(".cal-stats").classList.toggle("is-first", !statsShown);
    statsShown = true;
    box.innerHTML = rows.length
      ? `<ul class="cal-stat-list">${rows.map((t) => `<li class="cal-stat" style="${evStyle(t)}"><span class="cal-stat-icon" aria-hidden="true"><i class="ti ti-${t.icon}"></i></span><span class="cal-stat-label">${esc(t.label)}</span><span class="cal-stat-count">${t.count}</span><span class="cal-stat-bar" aria-hidden="true"><i style="width:${Math.min(100, (t.count / all.length) * 100)}%"></i></span></li>`).join("")}</ul>`
      : '<p class="cal-empty-line">No events this year.</p>';
  }

  // ── Event card (handoff §8.9) ──
  function actionsHtml(ev) {
    if (!ev.mine) return "";
    return `<span class="cal-ev-actions"><button type="button" class="cal-mini-btn" aria-label="Edit ${esc(ev.title)}" data-cal-edit="${ev.uid}"><i class="ti ti-pencil" aria-hidden="true"></i></button><button type="button" class="cal-mini-btn" aria-label="Delete ${esc(ev.title)}" data-cal-delete="${ev.uid}"><i class="ti ti-trash" aria-hidden="true"></i></button></span>`;
  }
  const chipHtml = (m) => `<span class="cal-chip"><i class="ti ti-${m.icon}" aria-hidden="true"></i>${esc(m.label)}</span>`;
  function cardHtml(ev) {
    const m = meta(ev.event_type);
    const audience = ev.mine ? '<span class="cal-audience"><i class="ti ti-lock" aria-hidden="true"></i>Only you</span>' : "";
    return `<article class="cal-ev" style="${evStyle(m)}"><div class="cal-ev-top">${chipHtml(m)}${audience}</div>`
      + `<h4 class="cal-ev-title">${esc(ev.title)}</h4><p class="cal-ev-date"><i class="ti ti-calendar" aria-hidden="true"></i>${formatRange(ev.start_date, ev.end_date)}</p>`
      + `${ev.description ? `<p class="cal-ev-desc">${esc(ev.description)}</p>` : ""}${actionsHtml(ev)}</article>`;
  }

  // ── Selected-day panel (handoff §8.9 and §10.3, for one person) ──
  function attendanceHtml(k) {
    const d = parse(k);
    const rec = data.attendance[k];
    let body;
    if (d.getDay() === 0 || d.getDay() === 6) {
      body = `<p class="cal-att-line">Rest day · ${d.toLocaleDateString("en-US", { weekday: "long" })}</p>`; // weekends win
    } else if (!rec && noWorkEvent(k)) {
      body = `<p class="cal-att-line">No work · ${esc(noWorkEvent(k).title)}</p>`;
    } else if (!rec) {
      body = '<p class="cal-att-line">No time logs for this day.</p>';
    } else if (rec.status === "leave") {
      body = `<span class="ds-status v-info"><span class="ds-dot d-info"></span>On leave · ${esc(rec.label)}</span>`;
    } else if (rec.status === "absent") {
      body = '<span class="ds-status v-error"><span class="ds-dot d-error"></span>Absent</span><p class="cal-att-line">No time logs and no leave filed.</p>';
    } else {
      const tone = rec.status === "late" ? "warning" : "success";
      body = `<span class="ds-status v-${tone}"><span class="ds-dot d-${tone}"></span>${esc(rec.label)}</span>`
        + `<dl class="cal-att-dl"><div><dt>Time in</dt><dd>${esc(rec.time_in)}</dd></div><div><dt>Time out</dt><dd>${rec.time_out ? esc(rec.time_out) : "Still in"}</dd></div><div><dt>Hours</dt><dd>${rec.hours} h</dd></div></dl>`;
    }
    return `<section class="cal-att" aria-label="Your attendance"><h4 class="cal-side-title">Your attendance</h4>${body}</section>`;
  }

  function renderDay() {
    const panel = $("[data-cal-day]");
    const k = state.selectedDay;
    if (!k) {
      panel.innerHTML = `<div class="ds-empty"><div class="ds-empty-icon" aria-hidden="true"><i class="ti ti-calendar-search"></i></div><div class="ds-empty-title">No date selected</div><p class="ds-empty-sub">Click any date on the calendar to view its events${attendanceOn() ? " and attendance" : ""}</p></div>`;
      return;
    }
    const d = parse(k);
    const seen = new Set();
    const evs = (buildEventMap(items())[k] ?? []).filter((ev) => !seen.has(ev.uid) && seen.add(ev.uid));
    panel.innerHTML = `<div class="cal-day-panel-head"><span class="cal-tile" aria-hidden="true"><i class="ti ti-calendar"></i></span>`
      + `<div class="fms-min0"><h3 class="cal-day-panel-title">${MONTHS[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}</h3><p class="cal-day-panel-sub">${plural(evs.length, "event")}</p></div>`
      + `<button type="button" class="ds-icon-btn" aria-label="Close this day's events" data-cal-close-day><i class="ti ti-x" aria-hidden="true"></i></button></div>`
      + `${attendanceOn() && k <= today ? attendanceHtml(k) : ""}`
      + `<div class="cal-cards">${evs.length ? evs.map(cardHtml).join("") : '<p class="cal-empty-line">No events on this day.</p>'}</div>`;
  }

  // ── All Events list (handoff §8.10). An event is listed under every month it spans;
  // months run July to June, the school year's order. ──
  function renderList() {
    const all = items();
    const q = state.search.trim().toLowerCase();
    if (state.filter && !all.some((e) => e.event_type === state.filter)) state.filter = "";
    const filtered = all.filter((e) => (!state.filter || e.event_type === state.filter) && (!q || e.title.toLowerCase().includes(q)));
    $("[data-cal-count]").textContent = `${filtered.length} / ${all.length}`;
    $("[data-cal-search-clear]").hidden = !state.search;

    const counts = TYPES.map((t) => ({ ...t, count: all.filter((e) => e.event_type === t.value).length })).filter((t) => t.count);
    $("[data-cal-filters]").innerHTML = `<button type="button" class="cal-filter" data-cal-filter="" aria-pressed="${!state.filter}">All</button>`
      + counts.map((t) => `<button type="button" class="cal-filter" data-cal-filter="${t.value}" aria-pressed="${state.filter === t.value}">${esc(t.label)} <b>·${t.count}</b></button>`).join("");

    const groups = {};
    for (const ev of filtered) {
      const end = parse(ev.end_date);
      const seen = new Set();
      for (const cur = parse(ev.start_date); cur <= end; cur.setMonth(cur.getMonth() + 1, 1)) {
        if (!seen.has(cur.getMonth())) { seen.add(cur.getMonth()); (groups[cur.getMonth()] ??= []).push(ev); }
      }
    }
    const box = $("[data-cal-groups]");
    if (!filtered.length) {
      box.innerHTML = `<p class="cal-list-empty">${all.length ? "No events match your filter." : "No events this year."}</p>`;
      return;
    }
    box.innerHTML = SY_ORDER.filter((m) => groups[m]).map((m) => {
      const open = !state.collapsed.has(m);
      const rows = groups[m].map((ev) => {
        const t = meta(ev.event_type);
        return `<li class="cal-row" style="${evStyle(t)}"><span class="cal-row-title">${esc(ev.title)}</span><span class="cal-row-meta">${chipHtml(t)}<span>${formatRange(ev.start_date, ev.end_date)}</span></span>${actionsHtml(ev)}</li>`;
      }).join("");
      return `<div class="cal-group"><button type="button" class="cal-group-btn" aria-expanded="${open}" aria-controls="cal-group-${m}" data-cal-group="${m}"><i class="ti ti-chevron-down" aria-hidden="true"></i>${MONTHS[m]} ${yearOf(m)}<span class="cal-count">${groups[m].length}</span></button>`
        + `<ul class="cal-rows" id="cal-group-${m}"${open ? "" : " hidden"}>${rows}</ul></div>`;
    }).join("");
  }

  function renderAll({ animate = false } = {}) {
    renderSub();
    renderMonthNav(animate);
    renderGrid(animate);
    renderLegend();
    renderStats();
    renderDay();
    renderList();
  }

  function goToMonth(month) {
    state.activeMonth = month;
    renderMonthNav(true);
    renderGrid(true);
    renderLegend();
  }

  // Selecting a day only flips aria-pressed, so focus stays on the clicked cell.
  function selectDay(k) {
    state.selectedDay = state.selectedDay === k ? null : k;
    root.querySelectorAll(".cal-day").forEach((cell) => cell.setAttribute("aria-pressed", String(cell.dataset.date === state.selectedDay)));
    renderDay();
  }

  // ── Flash message: the page's success alert ──
  const flash = document.querySelector("[data-flash]");
  function say(text) {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  }

  // ── Own events: add, edit, delete (handoff §8.11–8.12, "Just me") ──
  const findMine = (uid) => state.mine.find((ev) => `mine-${ev.event_id}` === uid);
  const eventDialog = document.getElementById("cal-event-dialog");
  const eventForm = eventDialog.querySelector("[data-cal-event-form]");
  const field = (name) => eventForm.querySelector(`[data-cal-field="${name}"]`);
  const formError = eventForm.querySelector("[data-cal-event-error]");
  let editing = null;

  eventForm.querySelectorAll('input[type="date"]').forEach((input) => { input.min = bounds.min; input.max = bounds.max; });
  const personalIcon = eventDialog.querySelector("[data-cal-event-icon]");

  function openEventDialog(ev) {
    editing = ev ?? null;
    eventDialog.querySelector("[data-cal-event-heading]").textContent = ev ? "Edit My Event" : "Add My Event";
    eventDialog.querySelector("[data-cal-event-save]").textContent = ev ? "Save Changes" : "Add Event";
    personalIcon.setAttribute("style", evStyle(meta(PERSONAL)));
    const start = state.selectedDay && state.selectedDay >= bounds.min && state.selectedDay <= bounds.max ? state.selectedDay : today;
    field("title").value = ev?.title ?? "";
    field("start_date").value = ev?.start_date ?? start;
    field("end_date").value = ev?.end_date ?? start;
    field("description").value = ev?.description ?? "";
    formError.hidden = true;
    eventDialog.showModal();
    field("title").focus();
  }

  field("start_date").addEventListener("change", () => {
    const end = field("end_date");
    if (!end.value || end.value < field("start_date").value) end.value = field("start_date").value;
  });

  // Save-time checks in the handoff's order; the first failure wins.
  function validate(v) {
    if (!v.title) return "Title is required.";
    if (!v.start_date) return "Start date is required.";
    if (!v.end_date) return "End date is required.";
    if (v.start_date > v.end_date) return "Start date must be on or before end date.";
    if (v.start_date < bounds.min || v.end_date > bounds.max) {
      return `Dates must fall within S.Y. ${data.school_year} (${bounds.min} – ${bounds.max}).`;
    }
    return "";
  }

  eventForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const v = {
      title: field("title").value.trim(),
      start_date: field("start_date").value,
      end_date: field("end_date").value,
      description: field("description").value.trim() || null,
    };
    const problem = validate(v);
    if (problem) {
      formError.querySelector(".ds-alert-body").textContent = problem;
      formError.hidden = false;
      return;
    }
    if (editing) Object.assign(editing, v);
    else state.mine.push({ event_id: state.nextId++, ...v });
    if (!state.showMine) { state.showMine = true; store.set(toggleKey("showMine"), "1"); } // a new own event shouldn't vanish
    eventDialog.close();
    say(editing ? "Event updated." : "Event created.");
    editing = null;
    renderAll();
  });

  const deleteDialog = document.getElementById("cal-delete-dialog");
  let toDelete = null;
  function openDelete(ev) {
    toDelete = ev;
    const m = meta(PERSONAL);
    const chip = deleteDialog.querySelector("[data-cal-delete-chip]");
    chip.setAttribute("style", evStyle(m));
    chip.innerHTML = `<i class="ti ti-${m.icon}" aria-hidden="true"></i>${esc(ev.title)}`;
    deleteDialog.showModal();
  }
  deleteDialog.querySelector("[data-cal-delete-confirm]").addEventListener("click", () => {
    state.mine = state.mine.filter((ev) => ev !== toDelete);
    toDelete = null;
    deleteDialog.close();
    say("Event deleted.");
    state.selectedDay = null;
    renderAll();
  });

  // ── Event Colors modal (handoff §8.13) ──
  const colorsDialog = document.getElementById("cal-colors-dialog");
  const colorRows = colorsDialog.querySelector("[data-cal-color-rows]");
  let draft = {};
  function colorRowHtml(t) {
    const m = buildTypes(draft).find((x) => x.value === t.value);
    const changed = draft[t.value] !== undefined;
    return `<div class="cal-color-row" style="${evStyle(m)}" data-type="${t.value}"><span class="cal-stat-icon" aria-hidden="true"><i class="ti ti-${m.icon}"></i></span>`
      + `<span class="cal-color-name">${esc(m.label)}<span class="cal-strip is-single" aria-hidden="true"><span>Sample event</span></span></span>`
      + `<input type="color" class="cal-color-input" value="${m.color}" aria-label="${esc(m.label)} colour" data-cal-color="${t.value}">`
      + `<button type="button" class="cal-mini-btn" aria-label="Reset ${esc(m.label)} colour" data-cal-color-reset="${t.value}"${changed ? "" : " hidden"}><i class="ti ti-refresh" aria-hidden="true"></i></button>`
      + "</div>";
  }
  const renderColorRows = () => { colorRows.innerHTML = data.types.map(colorRowHtml).join(""); };
  // Update a row in place: rebuilding it would close the colour picker mid-pick.
  function paintColorRow(type) {
    const row = colorRows.querySelector(`[data-type="${type}"]`);
    const m = buildTypes(draft).find((x) => x.value === type);
    row.setAttribute("style", evStyle(m));
    row.querySelector("[data-cal-color]").value = m.color;
    row.querySelector("[data-cal-color-reset]").hidden = draft[type] === undefined;
  }
  colorRows.addEventListener("input", (e) => {
    const input = e.target.closest("[data-cal-color]");
    if (!input || !HEX.test(input.value)) return;
    draft[input.dataset.calColor] = input.value;
    paintColorRow(input.dataset.calColor);
  });
  colorRows.addEventListener("click", (e) => {
    const reset = e.target.closest("[data-cal-color-reset]");
    if (!reset) return;
    const type = reset.dataset.calColorReset;
    delete draft[type];
    paintColorRow(type);
    colorRows.querySelector(`[data-cal-color="${type}"]`).focus();
  });
  colorsDialog.querySelector("[data-cal-colors-reset]").addEventListener("click", () => { draft = {}; renderColorRows(); });
  colorsDialog.querySelector("[data-cal-colors-apply]").addEventListener("click", () => {
    overrides = { ...draft };
    store.set(COLOR_KEY, JSON.stringify(overrides));
    TYPES = buildTypes(overrides);
    colorsDialog.close();
    renderAll({ animate: true });
  });

  // ── CSV export: school events only (handoff §8.14) ──
  const quoteCSV = (v) => {
    const s = v == null ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  function exportCSV() {
    const header = ["Date", "End Date", "Title", "Type", "Description", "School Year"];
    const rows = [...data.events].sort((a, b) => a.start_date.localeCompare(b.start_date))
      .map((ev) => [ev.start_date, ev.end_date, ev.title, meta(ev.event_type).label, ev.description ?? "", data.school_year]);
    const csv = [header, ...rows].map((r) => r.map(quoteCSV).join(",")).join("\r\n");
    const url = URL.createObjectURL(new Blob(["﻿", csv], { type: "text/csv;charset=utf-8;" })); // BOM so Excel reads UTF-8
    const a = document.createElement("a");
    a.href = url;
    a.download = `academic-calendar-SY${data.school_year}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── Print: a portal on <body>, the only thing @media print shows (handoff §8.15).
  // School events only, months July to June. ──
  function printHeader() {
    const made = new Date().toLocaleDateString("en-PH", { year: "numeric", month: "long", day: "numeric" });
    return `<div class="calp-head"><div><div class="calp-school">${esc(data.school_name)}</div><div class="calp-sub">Academic Calendar — S.Y. ${esc(data.school_year)}</div></div><div class="calp-sub">Generated on ${made}</div></div>`;
  }
  const printLegend = () => `<div class="calp-legend">${schoolTypes().map((t) => `<span class="calp-type" style="${evStyle(t)}">${esc(t.label)}</span>`).join("")}</div>`;
  const startsIn = (m) => data.events.filter((ev) => { const s = parse(ev.start_date); return s.getMonth() === m && s.getFullYear() === yearOf(m); });
  function eventTable(evs) {
    if (!evs.length) return '<p class="calp-none">No events this month</p>';
    return `<table><thead><tr><th>Date</th><th>Event</th><th>Type</th><th>Description</th></tr></thead><tbody>${evs.map((ev) => {
      const t = meta(ev.event_type);
      return `<tr><td>${formatRange(ev.start_date, ev.end_date)}</td><td>${esc(ev.title)}</td><td><span class="calp-type" style="${evStyle(t)}">${esc(t.label)}</span></td><td>${esc(ev.description ?? "")}</td></tr>`;
    }).join("")}</tbody></table>`;
  }
  function printList() {
    return `<div class="calp">${printHeader()}${SY_ORDER.map((m) => {
      const evs = startsIn(m);
      return `<section class="calp-block"><h3>${MONTHS[m]} ${yearOf(m)} <span>${plural(evs.length, "event")}</span></h3>${eventTable(evs)}</section>`;
    }).join("")}${printLegend()}</div>`;
  }
  function printSheets() {
    const map = buildEventMap(data.events.map((ev) => ({ ...ev, uid: ev.event_id })));
    return `<div class="calp">${SY_ORDER.map((m, i) => {
      const year = yearOf(m);
      const first = new Date(year, m, 1).getDay();
      const days = new Date(year, m + 1, 0).getDate();
      const cells = [...Array(first).fill(null), ...Array.from({ length: days }, (_, d) => d + 1)];
      while (cells.length % 7) cells.push(null);
      const rows = [];
      for (let r = 0; r < cells.length; r += 7) {
        rows.push(`<tr>${cells.slice(r, r + 7).map((d) => {
          if (!d) return "<td></td>";
          const k = iso(year, m, d);
          const starting = (map[k] ?? []).filter((ev) => ev.start_date === k);
          const labels = starting.slice(0, 2).map((ev) => `<span class="calp-label" style="${evStyle(meta(ev.event_type))}">${esc(ev.title)}</span>`).join("");
          return `<td><span class="calp-num">${d}</span>${labels}${starting.length > 2 ? `<span>+${starting.length - 2}</span>` : ""}</td>`;
        }).join("")}</tr>`);
      }
      return `<section class="calp-page">${printHeader()}<h2 class="calp-month-title">${MONTHS[m]} ${year}</h2>`
        + `<table class="calp-grid"><thead><tr>${DAYS_SHORT.map((d) => `<th>${d}</th>`).join("")}</tr></thead><tbody>${rows.join("")}</tbody></table>`
        + `<div class="calp-block"><h3>Events This Month</h3>${eventTable(startsIn(m))}</div>${i === SY_ORDER.length - 1 ? printLegend() : ""}</section>`;
    }).join("")}</div>`;
  }
  function print() {
    let portal = document.getElementById("cal-print-portal");
    if (!portal) {
      portal = document.createElement("div");
      portal.id = "cal-print-portal";
      document.body.append(portal);
    }
    portal.innerHTML = state.printView === "month" ? printSheets() : printList();
    window.print();
  }

  // ── Wiring ──
  root.addEventListener("change", (e) => {
    const toggle = e.target.closest("[data-cal-toggle]");
    if (!toggle) return;
    state[toggle.dataset.calToggle] = toggle.checked;
    store.set(toggleKey(toggle.dataset.calToggle), toggle.checked ? "1" : "0");
    renderAll();
    const icon = toggle.nextElementSibling;
    icon.classList.add("is-pop");
    icon.addEventListener("animationend", () => icon.classList.remove("is-pop"), { once: true });
  });

  root.addEventListener("click", (e) => {
    const t = e.target;
    const step = t.closest("[data-cal-step]");
    if (step) return goToMonth((state.activeMonth + Number(step.dataset.calStep) + 12) % 12);
    const pill = t.closest("[data-cal-month]");
    if (pill) return goToMonth(Number(pill.dataset.calMonth));
    const edit = t.closest("[data-cal-edit]");
    if (edit) return openEventDialog(findMine(edit.dataset.calEdit));
    const del = t.closest("[data-cal-delete]");
    if (del) return openDelete(findMine(del.dataset.calDelete));
    const day = t.closest(".cal-day");
    if (day) return selectDay(day.dataset.date);
    if (t.closest("[data-cal-close-day]")) {
      const was = state.selectedDay;
      selectDay(was);
      root.querySelector(`.cal-day[data-date="${was}"]`)?.focus();
      return undefined;
    }
    const filter = t.closest("[data-cal-filter]");
    if (filter) {
      state.filter = state.filter === filter.dataset.calFilter ? "" : filter.dataset.calFilter;
      return renderList();
    }
    const group = t.closest("[data-cal-group]");
    if (group) { // collapse the group and jump the grid to that month
      const m = Number(group.dataset.calGroup);
      if (state.collapsed.has(m)) state.collapsed.delete(m); else state.collapsed.add(m);
      renderList();
      root.querySelector(`[data-cal-group="${m}"]`).focus();
      if (m !== state.activeMonth) goToMonth(m);
      return undefined;
    }
    if (t.closest("[data-cal-search-clear]")) {
      state.search = "";
      const input = $("[data-cal-search]");
      input.value = "";
      input.focus();
      return renderList();
    }
    const view = t.closest("[data-cal-print-view]");
    if (view) {
      state.printView = view.dataset.calPrintView;
      root.querySelectorAll("[data-cal-print-view]").forEach((b) => b.setAttribute("aria-pressed", String(b === view)));
      return undefined;
    }
    if (t.closest("[data-cal-add]")) return openEventDialog(null);
    if (t.closest("[data-cal-colors]")) { draft = { ...overrides }; renderColorRows(); return colorsDialog.showModal(); }
    if (t.closest("[data-cal-csv]")) return exportCSV();
    if (t.closest("[data-cal-print]")) return print();
    return undefined;
  });

  $("[data-cal-search]").addEventListener("input", (e) => { state.search = e.target.value; renderList(); });

  renderAll({ animate: true });
})();
