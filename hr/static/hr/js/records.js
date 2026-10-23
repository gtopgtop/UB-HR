// Employee records, HR officer view: search the directory, approve or decline correction requests, and
// download a payroll register. Exports use the shell's data-csv-table; verifying uploads is in verify.js.
// Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };

  // ── Directory search ──
  const search = document.querySelector("[data-records-search]");
  search.addEventListener("input", () => {
    const q = search.value.trim().toLowerCase();
    document.querySelectorAll("[data-records-row]").forEach((row) => { row.hidden = Boolean(q) && !row.dataset.text.includes(q); });
  });

  // ── Correction requests: approve, or decline with a remark ──
  const left = document.querySelector("[data-corrections-left]");
  const tabCount = document.querySelector("#tab-corrections .ds-tab-count");
  function decide(row, approved, remark) {
    const tone = approved ? "success" : "error";
    const status = row.querySelector("[data-correction-status]");
    status.innerHTML = `<span class="ds-status v-${tone}"><span class="ds-dot d-${tone}"></span>${approved ? "Approved" : "Declined"}</span><div class="ds-cell-sub"></div>`;
    status.querySelector(".ds-cell-sub").textContent = approved ? "Record updated today · old value kept in the log" : remark;
    row.querySelector("[data-correction-actions]").remove();
    [left, tabCount].forEach((c) => { c.textContent = Math.max(0, Number(c.textContent) - 1); });
    const { name, field } = row.dataset;
    say(approved
      ? `Approved the ${field.toLowerCase()} correction for ${name}. The record is updated and the change is logged.`
      : `Declined the ${field.toLowerCase()} correction for ${name}. They see your remark and can refile.`);
  }
  const dialog = document.getElementById("decline-dialog");
  const remark = dialog.querySelector("[data-correction-remark]");
  const error = dialog.querySelector("[data-correction-error]");
  let declining = null;
  document.querySelectorAll("[data-correction-row]").forEach((row) => {
    row.querySelector("[data-correction-approve]")?.addEventListener("click", () => decide(row, true));
    row.querySelector("[data-correction-decline]")?.addEventListener("click", () => {
      declining = row;
      remark.value = "";
      error.hidden = true;
      remark.removeAttribute("aria-invalid");
    });
  });
  dialog.querySelector("[data-correction-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const text = remark.value.trim();
    if (!text) {
      error.hidden = false;
      remark.setAttribute("aria-invalid", "true");
      remark.focus();
      return;
    }
    dialog.close();
    decide(declining, false, text);
  });

  // ── Payroll register: one run's totals ──
  document.querySelectorAll("[data-register]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const cells = [...btn.closest("tr").cells].slice(0, 5).map((c) => c.textContent.replace(/\s+/g, " ").trim());
      const rows = [["Period", "Status", "Gross", "Deductions", "Net"], cells];
      const csv = rows.map((r) => r.map((v) => `"${v.replace(/"/g, '""')}"`).join(",")).join("\r\n");
      const url = URL.createObjectURL(new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8;" })); // BOM so Excel reads UTF-8
      const a = document.createElement("a");
      a.href = url;
      a.download = `payroll-register-${cells[0].toLowerCase().replace(/[^a-z0-9]+/g, "-")}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      say(`Downloaded the payroll register for ${cells[0]}.`);
    });
  });
})();
