// Alerts: start an intervention with an owner, an action plan and a follow-up date (usability task 12).
// Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const dialog = document.getElementById("intervention-dialog");
  const form = dialog.querySelector("[data-intervention-form]");
  const plan = form.querySelector("[data-intervention-plan]");
  const error = form.querySelector("[data-intervention-error]");
  const owner = form.querySelector("[data-intervention-owner]");
  const when = form.querySelector("[data-intervention-date]");
  let current = null;

  document.querySelectorAll("[data-intervene]").forEach((btn) => {
    btn.addEventListener("click", () => {
      current = btn;
      form.querySelector("[data-intervention-for]").textContent = btn.dataset.alertTitle;
      plan.value = "";
      error.hidden = true;
      plan.removeAttribute("aria-invalid");
    });
  });

  const short = (value) => new Date(`${value}T00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" });
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = plan.value.trim();
    if (!text) {
      error.hidden = false;
      plan.setAttribute("aria-invalid", "true");
      plan.focus();
      return;
    }
    const id = current.dataset.intervene;
    const follow = when.value ? `follow-up ${short(when.value)}` : "no follow-up date";
    const status = document.querySelector(`[data-intervention-status="${id}"]`);
    status.innerHTML = '<span class="ds-status v-info"><span class="ds-dot d-info"></span>In progress</span> <span class="fms-caption"></span>';
    status.querySelector(".fms-caption").textContent = `${text} · ${owner.value} · ${follow}`;
    const listed = document.querySelector(`[data-intervention-status="${id}-list"]`);
    if (listed) listed.textContent = `${listed.textContent.split(" · ")[0]} · In progress · ${owner.value}`;

    const item = document.createElement("li");
    item.innerHTML = '<span class="fms-min0"><span class="fms-schedule-title"></span><span class="fms-caption"></span></span><span class="ds-badge v-info s-sm">In progress</span>';
    item.querySelector(".fms-schedule-title").textContent = text;
    item.querySelector(".fms-caption").textContent = `${current.dataset.alertTitle} · ${owner.value} · ${follow}`;
    document.querySelector("[data-intervention-list]").prepend(item);

    dialog.close();
    current.disabled = true;
    say(`Intervention started for "${current.dataset.alertTitle}". ${owner.value} owns it, ${follow}.`);
  });
})();
