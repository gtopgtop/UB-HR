// Evaluation breakdown, HR officer view: release a breakdown and resolve a recheck (usability task 13).
// Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  document.querySelector("[data-flash-close]").addEventListener("click", () => { flash.hidden = true; });

  // ── Release ──
  const releaseDialog = document.getElementById("release-dialog");
  const confirm = releaseDialog.querySelector("[data-release-confirm]");
  const opener = document.querySelector("[data-release-open]");
  confirm.addEventListener("click", () => {
    releaseDialog.close();
    document.querySelector("[data-release-status]").innerHTML =
      '<span class="ds-badge v-success"><span class="ds-dot d-success"></span>Released today</span>';
    opener.disabled = true;
    opener.lastChild.textContent = "Released";
    say(`Breakdown released to ${confirm.dataset.name}. They have been notified and can now read it and file a recheck.`);
  });

  // ── Recheck: an outcome and remarks ──
  const recheckDialog = document.getElementById("recheck-dialog");
  const form = recheckDialog.querySelector("[data-recheck-form]");
  const remark = form.querySelector("[data-recheck-remark]");
  const error = form.querySelector("[data-recheck-error]");
  document.querySelector("[data-recheck-open]").addEventListener("click", () => {
    remark.value = "";
    error.hidden = true;
    remark.removeAttribute("aria-invalid");
  });
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!remark.value.trim()) {
      error.hidden = false;
      remark.setAttribute("aria-invalid", "true");
      remark.focus();
      return;
    }
    const corrected = form.querySelector("[data-recheck-outcome]").value === "correct";
    recheckDialog.close();
    const status = document.querySelector("[data-recheck-status]");
    status.className = "ds-badge v-success s-sm";
    status.textContent = corrected ? "Resolved · corrected" : "Resolved · rating stays";
    document.querySelector("[data-recheck-open]").disabled = true;
    say(`Recheck resolved for ${form.dataset.name}. They can read your remarks on their breakdown.`);
  });
})();
