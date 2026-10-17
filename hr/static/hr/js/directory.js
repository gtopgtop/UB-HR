// Employee directory: filter the rows by text, department and status, as you type.
(() => {
  const search = document.querySelector("[data-dir-search]");
  const dept = document.querySelector("[data-dir-dept]");
  const status = document.querySelector("[data-dir-status]");
  const rows = [...document.querySelectorAll("[data-dir-row]")];
  const count = document.querySelector("[data-dir-count]");
  const empty = document.querySelector("[data-dir-empty]");
  const total = count.textContent.match(/of (\d+)/)[1];

  function apply() {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    rows.forEach((row) => {
      const match = (!q || row.dataset.text.includes(q)) && (!dept.value || row.dataset.dept === dept.value)
        && (!status.value || row.dataset.status === status.value);
      row.hidden = !match;
      shown += match;
    });
    count.textContent = `Showing ${shown} of ${total} in this sample`;
    empty.hidden = shown > 0;
  }
  [search, dept, status].forEach((input) => input.addEventListener("input", apply));
})();
