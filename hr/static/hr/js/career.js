// Career progress and the Career Progress Tracker, HR officer view: pick an employee, commend, and export
// the promotion pipeline. Verifying proof lives in verify.js. Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };

  // ── Tracker: one employee at a time; the hash (#rowan-sison) picks who ──
  const picker = document.querySelector("[data-tracker-select]");
  const people = [...document.querySelectorAll("[data-tracker-person]")];
  const show = (slug) => {
    if (!people.some((p) => p.dataset.trackerPerson === slug)) return;
    people.forEach((p) => { p.hidden = p.dataset.trackerPerson !== slug; });
    picker.value = slug;
  };
  if (picker) {
    show(location.hash.slice(1));
    picker.addEventListener("change", () => {
      show(picker.value);
      history.replaceState(null, "", `#${picker.value}`);
    });
  }

  // ── Commend ──
  const commendDialog = document.getElementById("commend-dialog");
  const nameField = commendDialog.querySelector("[data-commend-name]");
  const forField = commendDialog.querySelector("[data-commend-for]");
  const commendError = commendDialog.querySelector("[data-commend-error]");
  document.querySelectorAll("[data-commend]").forEach((btn) => {
    btn.addEventListener("click", () => {
      nameField.value = btn.dataset.commend;
      forField.value = "";
      commendError.hidden = true;
    });
  });
  commendDialog.querySelector("[data-commend-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const name = nameField.value.trim();
    const reason = forField.value.trim();
    if (!name || !reason) {
      commendError.hidden = false;
      (name ? forField : nameField).focus();
      return;
    }
    const list = [...document.querySelectorAll("[data-recognition-list]")].find((l) => !l.closest("[hidden]"));
    const item = document.createElement("li");
    item.innerHTML = '<span class="fms-min0"><span class="fms-schedule-title"></span><span class="fms-muted"></span><span class="fms-caption">From HR · today</span></span>';
    item.querySelector(".fms-schedule-title").textContent = name;
    item.querySelector(".fms-muted").textContent = reason;
    list.prepend(item);
    commendDialog.close();
    say(`Commended ${name}. It shows on their profile and in their feed.`);
  });

  // ── Export the promotion pipeline ──
  document.querySelector("[data-career-csv]")?.addEventListener("click", () => {
    const rows = [...document.querySelectorAll("[data-pipeline-row]")].map((el) => el.dataset.pipelineRow.split("|"));
    const csv = [["Department", "Under 50% met", "50-99% met", "Promotion-ready"], ...rows]
      .map((r) => r.map((v) => (/[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v)).join(",")).join("\r\n");
    const url = URL.createObjectURL(new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8;" })); // BOM so Excel reads UTF-8
    const a = document.createElement("a");
    a.href = url;
    a.download = "promotion-pipeline.csv";
    a.click();
    URL.revokeObjectURL(url);
    say(`Downloaded the promotion pipeline for ${rows.length} departments.`);
  });
})();
