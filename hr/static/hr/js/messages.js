// Messages, HR officer view: switch and filter conversations, reply, start a conversation (with an
// employee, a department group or the HR office), answer anonymous concerns and send announcements.
// Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const list = document.querySelector("[data-thread-list]");
  const panes = document.querySelector("[data-thread-panes]");
  const inboxCount = document.querySelector("#tab-inbox .ds-tab-count");

  // ── Open a conversation ──
  function open(id) {
    list.querySelectorAll("[data-thread]").forEach((btn) => {
      const on = btn.dataset.thread === id;
      if (on) btn.setAttribute("aria-current", "true");
      else btn.removeAttribute("aria-current");
      const unread = on && btn.querySelector("[data-thread-unread]");
      if (unread) {
        inboxCount.textContent = Math.max(0, Number(inboxCount.textContent) - parseInt(unread.textContent, 10));
        unread.remove();
      }
    });
    panes.querySelectorAll("[data-thread-pane]").forEach((p) => { p.hidden = p.dataset.threadPane !== id; });
  }
  list.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-thread]");
    if (btn) open(btn.dataset.thread);
  });

  // ── Filter by kind: employees, groups, the HR office ──
  document.querySelectorAll("[data-thread-filter]").forEach((seg) => {
    seg.addEventListener("click", () => {
      const kind = seg.dataset.threadFilter;
      list.querySelectorAll("li").forEach((li) => { li.hidden = Boolean(kind) && li.dataset.kind !== kind; });
    });
  });

  // ── Reply: adds your message to the open conversation ──
  const bubble = (text) => {
    const li = document.createElement("li");
    li.className = "fms-bubble is-mine";
    li.innerHTML = '<div class="fms-caption">You · just now</div><p></p>';
    li.querySelector("p").textContent = text;
    return li;
  };
  panes.addEventListener("submit", (e) => {
    const form = e.target.closest("[data-reply-form]");
    if (!form) return;
    e.preventDefault();
    const field = form.querySelector("[data-reply-text]");
    const text = field.value.trim();
    if (!text) { field.focus(); return; }
    const pane = form.closest("[data-thread-pane]");
    pane.querySelector("[data-bubbles]").append(bubble(text));
    list.querySelector(`[data-thread="${pane.dataset.threadPane}"] [data-thread-preview]`).textContent = text;
    field.value = "";
  });

  // ── New conversation ──
  const compose = document.getElementById("compose-dialog");
  const to = compose.querySelector("[data-compose-to]");
  const subject = compose.querySelector("[data-compose-subject]");
  const body = compose.querySelector("[data-compose-body]");
  const composeError = compose.querySelector("[data-compose-error]");
  const urgent = compose.querySelector("[data-compose-urgent]");
  let made = 0;
  compose.querySelector("[data-compose-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!subject.value.trim() || !body.value.trim()) {
      composeError.hidden = false;
      (subject.value.trim() ? body : subject).focus();
      return;
    }
    const group = to.selectedOptions[0].parentElement.label;
    const name = to.value;
    const kind = name === "HR office" ? "office" : group === "Groups" ? "group" : "employee";
    const id = `new-${(made += 1)}`;

    const item = list.querySelector("li").cloneNode(true);
    item.dataset.kind = kind;
    item.hidden = false;
    const btn = item.querySelector("[data-thread]");
    btn.dataset.thread = id;
    btn.querySelector("[data-thread-unread]")?.remove();
    btn.querySelector(".ds-avatar").innerHTML = kind === "employee"
      ? name.split(" ").map((p) => p[0]).slice(0, 2).join("")
      : `<i class="ti ti-${kind === "office" ? "building" : "users"}"></i>`;
    btn.querySelector(".fms-schedule-title").textContent = name;
    btn.querySelector(".fms-thread-head .fms-caption").textContent = "Now";
    btn.querySelector(".fms-thread-subject").textContent = subject.value.trim();
    btn.querySelector("[data-thread-preview]").textContent = body.value.trim();
    list.prepend(item);

    const pane = panes.querySelector("[data-thread-pane]").cloneNode(true);
    pane.dataset.threadPane = id;
    pane.setAttribute("aria-labelledby", `thread-${id}-title`);
    const title = pane.querySelector(".ds-panel-title");
    title.id = `thread-${id}-title`;
    title.textContent = subject.value.trim();
    pane.querySelector(".ds-panel-sub").textContent = `${name} · ${urgent.checked ? "Sent now, marked urgent" : "Delivered in their working hours"}`;
    pane.querySelector(".ds-panel-head a")?.remove();
    const bubbles = pane.querySelector("[data-bubbles]");
    bubbles.replaceChildren(bubble(body.value.trim()));
    const field = pane.querySelector("[data-reply-text]");
    field.id = `reply-${id}`;
    field.value = "";
    pane.querySelector(".fms-reply label").htmlFor = field.id;
    pane.querySelector(".fms-reply label").textContent = `Reply to ${name}`;
    panes.prepend(pane);

    document.querySelector('[data-thread-filter=""]').click();
    open(id);
    compose.close();
    say(`Message sent to ${name}.`);
    subject.value = "";
    body.value = "";
    urgent.checked = false;
    composeError.hidden = true;
  });

  // ── Anonymous concerns: reply through the claim code ──
  const concern = document.getElementById("concern-dialog");
  const reply = concern.querySelector("[data-concern-reply]");
  const concernError = concern.querySelector("[data-concern-error]");
  const concernCount = document.querySelector("#tab-concerns .ds-tab-count");
  let answering = null;
  document.querySelectorAll("[data-concern]").forEach((btn) => {
    btn.addEventListener("click", () => {
      answering = btn;
      concern.querySelector("[data-concern-quote]").textContent = `${btn.dataset.concernText} (${btn.dataset.concernCode})`;
      reply.value = "";
      concernError.hidden = true;
    });
  });
  concern.querySelector("[data-concern-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!reply.value.trim()) {
      concernError.hidden = false;
      reply.focus();
      return;
    }
    const status = answering.closest("[data-concern-row]").querySelector("[data-concern-status]");
    if (status.textContent === "New") concernCount.textContent = Math.max(0, Number(concernCount.textContent) - 1);
    status.className = "ds-badge v-success s-sm";
    status.textContent = "Replied";
    concern.close();
    say(`Reply sent on the ${answering.dataset.concern.toLowerCase()} concern. The sender sees it with their claim code.`);
  });

  // ── Announcements ──
  const announce = document.getElementById("announce-dialog");
  const titleField = announce.querySelector("[data-announce-title]");
  const announceError = announce.querySelector("[data-announce-error]");
  announce.querySelector("[data-announce-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const title = titleField.value.trim();
    if (!title) {
      announceError.hidden = false;
      titleField.focus();
      return;
    }
    const audience = announce.querySelector("[data-announce-audience]").value;
    const kind = announce.querySelector("[data-announce-kind]").value;
    const item = document.createElement("div");
    item.className = "fms-meter";
    item.innerHTML = '<div class="fms-meter-head"><span></span><span class="fms-meter-value"><strong>0</strong> read so far</span></div>'
      + '<div class="fms-meter-track" aria-hidden="true"><i style="width: 0%"></i></div><div class="fms-caption"></div>';
    item.querySelector(".fms-meter-head span").textContent = title;
    item.querySelector(".fms-caption").textContent = `${kind} · Today · ${audience}`;
    document.querySelector("[data-announcement-list]").prepend(item);
    announce.close();
    titleField.value = "";
    announceError.hidden = true;
    say(`Announcement sent to ${audience === "All employees" ? "all employees" : audience}.`);
  });
})();
