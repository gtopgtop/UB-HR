// Step 2 of the leave approval chain: HR approves, or declines with a remark. Used on Attendance
// (Leave requests tab) and on Leave processing. Rows carry data-leave-row; counters are optional.
// Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const counters = document.querySelectorAll("[data-leave-left], [data-leave-count]");

  function decide(row, approved, remark) {
    const name = row.querySelector(".ds-cell-strong").textContent;
    const step = row.querySelector("[data-hr-step]");
    step.className = approved ? "is-done" : "is-declined";
    step.innerHTML = `<i class="ti ti-${approved ? "check" : "x"}" aria-hidden="true"></i>HR<span class="ds-sr-only">: ${approved ? "approved" : "declined"}</span>`;
    const tone = approved ? "success" : "error";
    row.querySelector("[data-leave-status]").innerHTML = `<span class="ds-status v-${tone}"><span class="ds-dot d-${tone}"></span>${approved ? "Approved" : "Declined"}</span>`;
    const note = row.querySelector("[data-leave-note]");
    if (note) note.textContent = approved ? "HR: Approved today." : `HR: ${remark}`;
    row.querySelector("[data-leave-actions]").remove();
    counters.forEach((c) => { c.textContent = Math.max(0, Number(c.textContent) - 1); });
    say(`${approved ? "Approved" : "Declined"} leave for ${name}. They have been notified.`);
  }

  const dialog = document.getElementById("decline-dialog");
  if (!dialog) return;
  const remark = dialog.querySelector("[data-decline-remark]");
  const error = dialog.querySelector("[data-decline-error]");
  let declining = null;
  document.querySelectorAll("[data-leave-row]").forEach((row) => {
    row.querySelector("[data-leave-approve]")?.addEventListener("click", () => decide(row, true));
    row.querySelector("[data-leave-decline]")?.addEventListener("click", () => {
      declining = row;
      remark.value = "";
      error.hidden = true;
      remark.removeAttribute("aria-invalid");
    });
  });
  dialog.querySelector("[data-decline-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const text = remark.value.trim();
    if (!text) {
      error.hidden = false;
      remark.setAttribute("aria-invalid", "true");
      remark.focus();
      return;
    }
    dialog.close();
    decide(declining, false, text);
    declining = null;
  });
})();
