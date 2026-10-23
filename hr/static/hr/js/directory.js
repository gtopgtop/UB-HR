// Employee directory: filter the rows by text, department and status, as you type, and add an employee.
// #add (from the Records page) opens the add form. Prototype only: nothing is saved.
(() => {
  const search = document.querySelector("[data-dir-search]");
  const dept = document.querySelector("[data-dir-dept]");
  const status = document.querySelector("[data-dir-status]");
  const body = document.querySelector("[data-dir-body]");
  const count = document.querySelector("[data-dir-count]");
  const empty = document.querySelector("[data-dir-empty]");
  let total = Number(count.textContent.match(/of (\d+)/)[1]);

  function apply() {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    body.querySelectorAll("[data-dir-row]").forEach((row) => {
      const match = (!q || row.dataset.text.includes(q)) && (!dept.value || row.dataset.dept === dept.value)
        && (!status.value || row.dataset.status === status.value);
      row.hidden = !match;
      shown += match;
    });
    count.textContent = `Showing ${shown} of ${total} in this sample`;
    empty.hidden = shown > 0;
  }
  [search, dept, status].forEach((input) => input.addEventListener("input", apply));

  // ── Add employee ──
  const dialog = document.getElementById("add-dialog");
  const field = (name) => dialog.querySelector(`[data-add-${name}]`);
  const tones = { "Full-time": "success", "Part-time": "info", Probationary: "warning" };
  if (location.hash === "#add") dialog.showModal();
  dialog.querySelector("[data-add-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const name = field("name").value.trim();
    const position = field("position").value.trim();
    if (!name || !position) {
      field("error").hidden = false;
      (name ? field("position") : field("name")).focus();
      return;
    }
    const row = body.querySelector("[data-dir-row]").cloneNode(true);
    const kind = field("status").value;
    row.dataset.dept = field("dept").value;
    row.dataset.status = kind;
    row.dataset.text = `${name} ${position}`.toLowerCase();
    row.querySelector(".ds-avatar").textContent = name.split(/\s+/).map((p) => p[0]).slice(0, 2).join("").toUpperCase();
    row.querySelector(".ds-cell-strong").textContent = name;
    row.querySelector(".ds-cell-sub").textContent = position;
    row.cells[1].textContent = field("dept").value;
    row.cells[2].innerHTML = `<span class="ds-badge v-${tones[kind] || "info"} s-sm"></span>`;
    row.cells[2].firstChild.textContent = kind;
    const start = field("start").value;
    row.cells[3].textContent = start
      ? `Starts ${new Date(`${start}T00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}`
      : "—";
    row.querySelector(".ds-row-action").setAttribute("aria-label", `Open ${name}'s record`);
    body.prepend(row);
    total += 1;
    apply();
    dialog.close();
    if (location.hash === "#add") history.replaceState(null, "", location.pathname);
    const flash = document.querySelector("[data-flash]");
    flash.querySelector("[data-flash-text]").textContent = `Added ${name} to ${field("dept").value}. Their record and an empty 201 file are ready, and the sign-in invitation is sent.`;
    flash.hidden = false;
    dialog.querySelector("[data-add-form]").reset();
    field("error").hidden = true;
  });
})();
