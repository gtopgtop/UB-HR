// Time in and out, employee view (usability task 1): by scanning a station's QR code or on the web.
// The prototype's clock is fixed at the page's "now". Prototype only: nothing is saved.
(() => {
  const card = document.querySelector("[data-clock]");
  if (!card) return;
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const { now, shiftStart, shiftEnd } = card.dataset;
  const minutes = (t) => {
    const [, h, m, ap] = t.match(/(\d+):(\d+) (AM|PM)/);
    return ((Number(h) % 12) + (ap === "PM" ? 12 : 0)) * 60 + Number(m);
  };
  const status = card.querySelector("[data-clock-status]");
  const badge = card.querySelector("[data-clock-badge]");
  const log = card.querySelector("[data-clock-log]");
  const ins = card.querySelectorAll("[data-clock-in-qr], [data-clock-in-web]");
  const out = card.querySelector("[data-clock-out]");
  const addLog = (icon, text) => {
    const li = document.createElement("li");
    li.innerHTML = `<i class="ti ti-${icon}" aria-hidden="true"></i><span></span>`;
    li.querySelector("span").textContent = text;
    log.append(li);
  };

  function timeIn(method) {
    const late = minutes(now) - minutes(shiftStart);
    const onTime = late <= 0;
    log.replaceChildren();
    addLog("login", `In ${now} · ${method}`);
    status.textContent = onTime ? `Timed in at ${now}, before your shift` : `Timed in at ${now}, ${late} min late`;
    badge.className = `ds-badge v-${onTime ? "success" : "warning"}`;
    badge.innerHTML = `<span class="ds-dot d-${onTime ? "success" : "warning"}"></span>${onTime ? "On time" : "Late"}`;
    ins.forEach((b) => { b.hidden = true; });
    out.hidden = false;
    out.focus();
    say(`Timed in at ${now} (${method}).${onTime ? ` Your shift starts at ${shiftStart}.` : ""}`);
  }
  card.querySelector("[data-clock-in-web]").addEventListener("click", () => timeIn("web"));

  const qr = document.getElementById("qr-dialog");
  const station = qr.querySelector("[data-qr-station]");
  const error = qr.querySelector("[data-qr-error]");
  station.addEventListener("change", () => { error.hidden = true; });
  qr.querySelector("[data-qr-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    if (station.value === "offline") {
      error.hidden = false;
      station.focus();
      return;
    }
    qr.close();
    timeIn(`QR at ${station.value}`);
  });

  out.addEventListener("click", () => {
    const early = minutes(shiftEnd) - minutes(now);
    addLog("logout", `Out ${now} · web`);
    status.textContent = early > 0 ? `Timed out at ${now}, ${Math.round(early / 6) / 10} h before your shift ends` : `Timed out at ${now}`;
    out.hidden = true;
    say(early > 0 ? `Timed out at ${now}. Leaving before ${shiftEnd} shows as undertime on your time record.` : `Timed out at ${now}.`);
  });
})();
