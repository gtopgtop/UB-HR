// Attendance page, HR officer view: the reminder button, the attendance export (usability task 14)
// and step 2 of the leave approval chain. Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  document.querySelector("[data-flash-close]").addEventListener("click", () => { flash.hidden = true; });
  const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;

  // ── Remind the people who have not timed in yet ──
  const remind = document.querySelector("[data-remind]");
  remind.addEventListener("click", () => {
    remind.disabled = true;
    say(`Reminder sent to ${plural(Number(remind.dataset.remind), "employee")} who have not timed in yet.`);
  });

  // ── Export: one row per working day, for the school or one department ──
  const data = JSON.parse(document.getElementById("calendar-data").textContent);
  const exportDialog = document.getElementById("export-dialog");
  const deptField = exportDialog.querySelector("[data-export-department-field]");
  const monthField = exportDialog.querySelector("[data-export-month]");
  // A department row's export button opens the dialog with that department picked.
  document.querySelectorAll("[data-export-department]").forEach((btn) => {
    btn.addEventListener("click", () => { deptField.value = btn.dataset.exportDepartment; });
  });
  document.querySelector('[data-dialog-open="export-dialog"]:not([data-export-department])')
    .addEventListener("click", () => { deptField.value = ""; });

  const quoteCSV = (v) => {
    const s = v == null ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  exportDialog.querySelector("[data-export-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const dept = deptField.value;
    const month = String(monthField.value).padStart(2, "0");
    const header = ["Date", "Department", "Staff", "Present", "Late", "Absent", "On leave", "Not timed in"];
    const rows = Object.entries(data.attendance)
      .filter(([k]) => k.startsWith(`2026-${month}-`))
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, rec]) => {
        const r = dept ? rec.departments.find((d) => d.name === dept) : rec;
        return [k, dept || "Whole school", r.staff, r.present, r.late, r.absent, r.on_leave, r.not_timed_in];
      });
    const csv = [header, ...rows].map((r) => r.map(quoteCSV).join(",")).join("\r\n");
    const url = URL.createObjectURL(new Blob(["﻿", csv], { type: "text/csv;charset=utf-8;" })); // BOM so Excel reads UTF-8
    const a = document.createElement("a");
    const label = monthField.selectedOptions[0].textContent;
    a.href = url;
    a.download = `attendance-${(dept || "whole-school").toLowerCase().replace(/\s+/g, "-")}-2026-${month}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    exportDialog.close();
    say(`Downloaded ${label} attendance for ${dept || "the whole school"}: ${plural(rows.length, "working day")}.`);
  });

  // ── Leave, step 2: approve, or decline with a remark ──
  const left = document.querySelector("[data-leave-left]");
  const count = document.querySelector("[data-leave-count]");
  function decide(row, approved, remark) {
    const name = row.querySelector(".ds-cell-strong").textContent;
    const step = row.querySelector("[data-hr-step]");
    step.className = approved ? "is-done" : "is-declined";
    step.innerHTML = `<i class="ti ti-${approved ? "check" : "x"}" aria-hidden="true"></i>HR<span class="ds-sr-only">: ${approved ? "approved" : "declined"}</span>`;
    const tone = approved ? "success" : "error";
    row.querySelector("[data-leave-status]").innerHTML = `<span class="ds-status v-${tone}"><span class="ds-dot d-${tone}"></span>${approved ? "Approved" : "Declined"}</span>`;
    row.querySelector("[data-leave-note]").textContent = approved ? "HR: Approved today." : `HR: ${remark}`;
    row.querySelector("[data-leave-actions]").remove();
    const n = Number(left.textContent) - 1;
    left.textContent = n;
    count.textContent = n;
    say(`${approved ? "Approved" : "Declined"} leave for ${name}. They have been notified.`);
  }

  const declineDialog = document.getElementById("decline-dialog");
  const remark = declineDialog.querySelector("[data-decline-remark]");
  const remarkError = declineDialog.querySelector("[data-decline-error]");
  let declining = null;
  document.querySelectorAll("[data-leave-row]").forEach((row) => {
    row.querySelector("[data-leave-approve]")?.addEventListener("click", () => decide(row, true));
    row.querySelector("[data-leave-decline]")?.addEventListener("click", () => {
      declining = row;
      remark.value = "";
      remarkError.hidden = true;
      remark.removeAttribute("aria-invalid");
    });
  });
  declineDialog.querySelector("[data-decline-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const text = remark.value.trim();
    if (!text) {
      remarkError.hidden = false;
      remark.setAttribute("aria-invalid", "true");
      remark.focus();
      return;
    }
    declineDialog.close();
    decide(declining, false, text);
    declining = null;
  });
})();
