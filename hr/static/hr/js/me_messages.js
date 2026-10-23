// My messages, employee view: open and reply to conversations with HR, start a new one, and acknowledge
// announcements. Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const list = document.querySelector("[data-thread-list]");
  const panes = document.querySelector("[data-thread-panes]");

  const open = (id) => {
    list.querySelectorAll("[data-thread]").forEach((b) => {
      if (b.dataset.thread === id) b.setAttribute("aria-current", "true");
      else b.removeAttribute("aria-current");
    });
    panes.querySelectorAll("[data-thread-pane]").forEach((p) => { p.hidden = p.dataset.threadPane !== id; });
  };
  list.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-thread]");
    if (btn) open(btn.dataset.thread);
  });

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
    if (!field.value.trim()) { field.focus(); return; }
    const pane = form.closest("[data-thread-pane]");
    pane.querySelector("[data-bubbles]").append(bubble(field.value.trim()));
    list.querySelector(`[data-thread="${pane.dataset.threadPane}"] [data-thread-preview]`).textContent = field.value.trim();
    field.value = "";
  });

  // ── New conversation with HR ──
  const dialog = document.getElementById("new-dialog");
  const subject = dialog.querySelector("[data-new-subject]");
  const body = dialog.querySelector("[data-new-body]");
  let made = 0;
  dialog.querySelector("[data-new-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!subject.value.trim() || !body.value.trim()) {
      dialog.querySelector("[data-new-error]").hidden = false;
      (subject.value.trim() ? body : subject).focus();
      return;
    }
    const id = `new-${(made += 1)}`;
    const item = list.querySelector("li").cloneNode(true);
    const btn = item.querySelector("[data-thread]");
    btn.dataset.thread = id;
    btn.querySelector(".ds-badge")?.remove();
    btn.querySelector(".fms-schedule-title").textContent = subject.value.trim();
    btn.querySelector(".fms-thread-head .fms-caption").textContent = "Now";
    btn.querySelector("[data-thread-preview]").textContent = body.value.trim();
    list.prepend(item);
    const pane = panes.querySelector("[data-thread-pane]").cloneNode(true);
    pane.dataset.threadPane = id;
    pane.setAttribute("aria-labelledby", `thread-${id}-title`);
    const title = pane.querySelector(".ds-panel-title");
    title.id = `thread-${id}-title`;
    title.textContent = subject.value.trim();
    pane.querySelector("[data-bubbles]").replaceChildren(bubble(body.value.trim()));
    const field = pane.querySelector("[data-reply-text]");
    field.id = `reply-${id}`;
    field.value = "";
    pane.querySelector(".fms-reply label").htmlFor = field.id;
    panes.prepend(pane);
    open(id);
    dialog.close();
    say("Message sent to the HR office. You'll get a notification when they reply.");
    subject.value = "";
    body.value = "";
    dialog.querySelector("[data-new-error]").hidden = true;
  });

  // ── Acknowledge an announcement ──
  const count = document.querySelector("[data-ack-count]");
  document.querySelectorAll("[data-ack]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const badge = document.createElement("span");
      badge.className = "ds-badge v-success s-sm";
      badge.textContent = "Acknowledged";
      btn.replaceWith(badge);
      count.textContent = Math.max(0, Number(count.textContent) - 1);
      say("Acknowledged. HR can see that you've read it.");
    });
  });
})();
