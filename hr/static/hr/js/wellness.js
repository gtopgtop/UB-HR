// Wellness, HR officer view: export the department aggregates shown on the page (groups of 5 or more only).
// The reminder buttons use the shell's data-say flash. Prototype only: nothing is saved.
(() => {
  const flash = document.querySelector("[data-flash]");
  document.querySelector("[data-wellness-csv]").addEventListener("click", () => {
    const rows = [...document.querySelector("[data-checkin-table]").tBodies[0].rows].map((tr) => {
      const [name, checked, mood, stress] = tr.cells;
      const [value, total] = checked.querySelector(".fms-meter-value").textContent.match(/\d+/g);
      return [name.textContent.trim(), value, total, mood.textContent.trim(), stress.textContent.trim()];
    });
    const csv = [["Department", "Checked in this week", "Headcount", "Average mood", "Average stress"], ...rows]
      .map((r) => r.join(",")).join("\r\n");
    const url = URL.createObjectURL(new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8;" })); // BOM so Excel reads UTF-8
    const a = document.createElement("a");
    a.href = url;
    a.download = "wellness-by-department-2026-10-12.csv";
    a.click();
    URL.revokeObjectURL(url);
    flash.querySelector("[data-flash-text]").textContent = `Downloaded this week's check-in averages for ${rows.length} departments. No individual answers are included.`;
    flash.hidden = false;
  });
})();
