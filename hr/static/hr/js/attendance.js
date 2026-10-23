// Attendance page, HR officer view: the reminder button, the attendance export (usability task 14) and
// the work-hours CSV.
// Step 2 of leave lives in leave_queue.js. Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
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
  const download = (name, rows) => {
    const csv = rows.map((r) => r.map(quoteCSV).join(",")).join("\r\n");
    const url = URL.createObjectURL(new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8;" })); // BOM so Excel reads UTF-8
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    a.click();
    URL.revokeObjectURL(url);
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
    const label = monthField.selectedOptions[0].textContent;
    download(`attendance-${(dept || "whole-school").toLowerCase().replace(/\s+/g, "-")}-2026-${month}.csv`,
      [header, ...rows]);
    exportDialog.close();
    say(`Downloaded ${label} attendance for ${dept || "the whole school"}: ${plural(rows.length, "working day")}.`);
  });

  // ── Work hours: the table as it stands, one row per department ──
  document.querySelector("[data-hours-csv]").addEventListener("click", () => {
    const table = document.querySelector("[data-hours-table]");
    const header = ["Department", "Expected hours", "Logged hours", "Undertime hours", "Overtime hours",
      "Overtime share", "Hours per person weekly"];
    const rows = [...table.tBodies[0].rows].map((tr) => {
      const [name, expected, logged, under, over, weekly] = tr.cells;
      const hours = (cell) => cell.textContent.replace(/[^\d.]/g, "");
      return [name.textContent.trim(), hours(expected), hours(logged), hours(under),
        hours(over.querySelector(".fms-meter-head span")), over.querySelector("strong").textContent, hours(weekly)];
    });
    download("work-hours-2026-10.csv", [header, ...rows]);
    say(`Downloaded October work hours for ${plural(rows.length, "department")}.`);
  });
})();
