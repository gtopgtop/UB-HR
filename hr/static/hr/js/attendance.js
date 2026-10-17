// Attendance page: the time clock, the QR scan stand-in and the leave form's live balance check.
// Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  document.querySelector("[data-flash-close]").addEventListener("click", () => { flash.hidden = true; });

  const clockTime = () => new Date().toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });

  // ── Time clock: each action logs the opposite of the current state. ──
  const clock = document.querySelector("[data-clock]");
  const action = clock.querySelector("[data-clock-action]");

  function punch(method, station) {
    const goingOut = clock.dataset.state === "in";
    const direction = goingOut ? "Out" : "In";
    const time = clockTime();
    clock.dataset.state = goingOut ? "out" : "in";

    const item = document.createElement("li");
    item.innerHTML = `<i class="ti ti-${goingOut ? "logout" : "login"}" aria-hidden="true"></i>`;
    item.append(`${direction} · ${time} · ${method}`);
    clock.querySelector("[data-clock-log]").append(item);

    clock.querySelector("[data-clock-status]").textContent = `Timed ${direction.toLowerCase()} at ${time}`;
    action.querySelector(".ti").className = `ti ti-${goingOut ? "login" : "logout"}`;
    action.querySelector("span").textContent = goingOut ? "Time in" : "Time out";
    say(`Timed ${direction.toLowerCase()} at ${time}${station ? ` by QR at ${station}` : ""}.`);
  }

  action.addEventListener("click", () => punch("Web"));
  const scan = document.querySelector("[data-qr-scan]");
  scan.addEventListener("click", () => {
    scan.closest("dialog").close();
    punch("QR", scan.dataset.station);
  });

  // ── Leave form ──
  const form = document.querySelector("[data-leave-form]");
  const type = form.querySelector("[data-leave-type]");
  const start = form.querySelector("[data-leave-start]");
  const end = form.querySelector("[data-leave-end]");
  const half = form.querySelector("[data-leave-half]");
  const check = form.querySelector("[data-leave-check]");
  const error = form.querySelector("[data-leave-error]");
  const attachment = form.querySelector("[data-leave-attachment]");

  const toDate = (value) => (value ? new Date(`${value}T00:00`) : null);
  const short = (d) => d.toLocaleDateString("en-US", { month: "short", day: "numeric" });

  function workingDays(from, to) {
    let days = 0;
    for (const d = new Date(from); d <= to; d.setDate(d.getDate() + 1)) {
      if (d.getDay() !== 0 && d.getDay() !== 6) days += 1;
    }
    return days;
  }

  // Returns {days, from, to, problem}. `problem` is the message to show, if any.
  function assess() {
    const option = type.selectedOptions[0];
    const left = Number(option.dataset.left);
    const from = toDate(start.value);
    const to = toDate(end.value) || from;
    if (!from) return { problem: "Pick the first day of your leave." };
    if (to < from) return { problem: "The last day is before the first day." };
    let days = workingDays(from, to);
    if (half.checked) {
      if (days !== 1) return { problem: "Half day applies to a single working day." };
      days = 0.5;
    }
    if (days === 0) return { problem: "Those dates fall on rest days only." };
    if (days > left) return { days, from, to, problem: `This uses ${days} days, but you have ${left} ${option.dataset.name.toLowerCase()} days left.` };
    return { days, from, to, left };
  }

  function showError(message) {
    error.hidden = !message;
    error.querySelector("span").textContent = message || "";
    [start, end].forEach((input) => {
      input.classList.toggle("is-invalid", Boolean(message));
      input.setAttribute("aria-invalid", String(Boolean(message)));
    });
  }

  function update() {
    attachment.hidden = type.selectedOptions[0].dataset.attachment !== "true";
    if (!start.value) { check.textContent = "Pick the dates to see how many days this uses."; return; }
    const result = assess();
    check.classList.toggle("is-over", Boolean(result.problem));
    if (result.problem) { check.textContent = result.problem; return; }
    showError("");
    check.textContent = `${result.days} working day${result.days === 1 ? "" : "s"} · ${result.left} left now · ${result.left - result.days} left after approval`;
  }
  [type, start, end, half].forEach((input) => input.addEventListener("input", update));

  form.addEventListener("submit", (e) => {
    const result = assess();
    if (result.problem) {
      e.preventDefault();
      showError(result.problem);
      start.focus();
      return;
    }
    const option = type.selectedOptions[0];
    const dates = result.from.getTime() === result.to.getTime() ? short(result.from) : `${short(result.from)}–${short(result.to)}`;

    // Hold the days on the balance card.
    const pending = document.querySelector(`[data-pending="${option.value}"]`);
    pending.dataset.days = Number(pending.dataset.days) + result.days;
    pending.textContent = `${pending.dataset.days} days pending approval`;

    // Add the request to the top of the history.
    const row = document.createElement("tr");
    row.innerHTML = `<td><div class="ds-cell-strong"></div><div class="ds-cell-sub"></div></td><td class="a-right"></td><td>Today</td>
      <td><ol class="fms-approval"><li class="is-pending"><i class="ti ti-hourglass" aria-hidden="true"></i>Department head<span class="ds-sr-only">: waiting for a decision</span></li><li class="is-waiting"><i class="ti ti-clock" aria-hidden="true"></i>HR<span class="ds-sr-only">: not reached yet</span></li></ol></td>
      <td><span class="ds-status v-warning"><span class="ds-dot d-warning"></span>Pending</span></td><td class="fms-remarks">—</td>`;
    row.querySelector(".ds-cell-strong").textContent = option.dataset.name;
    row.querySelector(".ds-cell-sub").textContent = dates;
    row.children[1].textContent = result.days;
    document.querySelector("[data-leave-rows]").prepend(row);
    const count = document.querySelector("[data-leave-count]");
    count.textContent = Number(count.textContent) + 1;

    say(`Leave request sent to your department head: ${option.dataset.name}, ${dates}. ${result.days} day${result.days === 1 ? " is" : "s are"} on hold until a decision.`);
    form.reset();
    showError("");
    update();
  });
  update();
})();
