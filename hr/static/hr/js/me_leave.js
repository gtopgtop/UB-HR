// File leave, employee view (usability task 2): count working days (no weekends or holidays), check the
// balance as you pick dates, ask for a medical certificate for longer sick leave, and update the balance
// and history once sent. Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const data = JSON.parse(document.getElementById("leave-data").textContent);
  const dialog = document.getElementById("leave-dialog");
  const form = dialog.querySelector("[data-leave-form]");
  const field = (name) => form.querySelector(`[data-leave-${name}]`);
  const check = field("check");
  const attach = field("attach");
  const errorBox = field("error");
  const noWork = new Set(data.no_work);
  const flash = document.querySelector("[data-flash]");

  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const short = (value) => new Date(`${value}T00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" });
  function workingDays(from, to) {
    let n = 0;
    for (let d = new Date(`${from}T00:00`); iso(d) <= to; d.setDate(d.getDate() + 1)) {
      if (d.getDay() % 6 !== 0 && !noWork.has(iso(d))) n += 1;
    }
    return n;
  }
  function current() {
    const from = field("from").value;
    const to = field("to").value || from;
    field("half").disabled = false;
    if (!from || to < from) return null;
    const one = from === to;
    field("half").disabled = !one;
    if (!one) field("half").checked = false;
    const days = workingDays(from, to) / (one && field("half").checked ? 2 : 1);
    return { from, to, days, code: field("type").value, balance: data.balances[field("type").value] };
  }
  function update() {
    const req = current();
    errorBox.hidden = true;
    attach.hidden = !(req && req.code === "SL" && req.days >= data.certificate_from);
    if (!req) {
      check.className = "fms-balance";
      check.textContent = field("from").value && field("to").value ? "The end date is before the start date." : "Pick the dates to see your balance.";
      return;
    }
    const after = req.balance.left - req.days;
    check.className = `fms-balance${after < 0 ? " is-over" : ""}`;
    check.textContent = req.days === 0
      ? "Those dates are weekends or holidays, so no leave is needed."
      : after < 0
        ? `${req.days} working day${req.days === 1 ? "" : "s"}, but you have ${req.balance.left} ${req.balance.type.toLowerCase()} days left.`
        : `${req.days} working day${req.days === 1 ? "" : "s"} · ${req.balance.left} left now, ${after} after this request.`;
  }
  ["type", "from", "to", "half"].forEach((name) => field(name).addEventListener("input", update));
  field("from").addEventListener("change", () => { if (!field("to").value) field("to").value = field("from").value; update(); });

  const fail = (text, focus) => {
    field("error-text").textContent = text;
    errorBox.hidden = false;
    focus.focus();
  };
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const req = current();
    if (!req) return fail("Pick a start and end date.", field("from"));
    if (req.days === 0) return fail("Those dates have no working days.", field("from"));
    if (req.days > req.balance.left) return fail(`You have ${req.balance.left} ${req.balance.type.toLowerCase()} days left.`, field("to"));
    if (!attach.hidden && !field("file").files.length) return fail("Attach a medical certificate for 3 or more days of sick leave.", field("file"));

    // The balance: the days are held while the request waits for approval.
    req.balance.left -= req.days;
    const meter = document.querySelector(`[data-balance="${req.code}"]`);
    meter.querySelector("[data-balance-left]").textContent = req.balance.left;
    meter.querySelector("[data-balance-bar]").style.width = `${Math.round((req.balance.left / req.balance.total) * 100)}%`;
    const note = meter.querySelector("[data-balance-note]");
    const waiting = (Number((note.textContent.match(/^(\d+(?:\.5)?) day/) || [0, 0])[1]) || 0) + req.days;
    note.textContent = `${waiting} day${waiting === 1 ? "" : "s"} waiting for approval`;

    const row = document.createElement("tr");
    const dates = req.from === req.to ? short(req.from) : `${short(req.from)}–${short(req.to)}`;
    row.innerHTML = '<td><div class="ds-cell-strong"></div><div class="ds-cell-sub"></div></td><td class="a-right"></td><td>Today</td>'
      + '<td><ol class="fms-approval"><li class="is-pending"><i class="ti ti-hourglass" aria-hidden="true"></i>Principal<span class="ds-sr-only">: waiting for a decision</span></li>'
      + '<li class="is-waiting"><i class="ti ti-clock" aria-hidden="true"></i>HR<span class="ds-sr-only">: not reached yet</span></li></ol></td>'
      + '<td><span class="ds-status v-warning"><span class="ds-dot d-warning"></span>With your principal</span></td><td class="fms-remarks"></td>';
    row.querySelector(".ds-cell-strong").textContent = req.balance.type;
    row.querySelector(".ds-cell-sub").textContent = dates;
    row.cells[1].textContent = req.days;
    row.querySelector(".fms-remarks").textContent = field("reason").value.trim() || "—";
    document.querySelector("[data-leave-history]").prepend(row);
    const count = document.querySelector("[data-leave-open]");
    count.textContent = Number(count.textContent) + 1;

    dialog.close();
    flash.querySelector("[data-flash-text]").textContent = `Sent ${req.days} day${req.days === 1 ? "" : "s"} of ${req.balance.type.toLowerCase()} (${dates}) to your principal. You have ${req.balance.left} days left.`;
    flash.hidden = false;
    form.reset();
    update();
  });
})();
