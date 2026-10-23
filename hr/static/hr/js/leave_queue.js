// One step of the leave approval chain: approve, or decline with a remark. HR uses it for step 2 (Attendance's
// Leave requests tab, Leave processing) and the department head for step 1 (Leave approvals). Rows carry
// data-leave-row; data-leave-next names where an approved request goes ("With HR"). The step chip
// ([data-my-step], label in data-step-label) and the counters are optional.
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
    const step = row.querySelector("[data-my-step]");
    const label = step?.dataset.stepLabel || row.dataset.stepLabel || "HR";
    if (step) {
      step.className = approved ? "is-done" : "is-declined";
      step.innerHTML = `<i class="ti ti-${approved ? "check" : "x"}" aria-hidden="true"></i>${label}<span class="ds-sr-only">: ${approved ? "approved" : "declined"}</span>`;
    }
    const next = row.dataset.leaveNext;
    const tone = approved ? (next ? "warning" : "success") : "error";
    row.querySelector("[data-leave-status]").innerHTML = `<span class="ds-status v-${tone}"><span class="ds-dot d-${tone}"></span>${approved ? next || "Approved" : "Declined"}</span>`;
    const note = row.querySelector("[data-leave-note]");
    if (note) note.textContent = approved ? `${label}: ${remark || "Approved today."}` : `${label}: ${remark}`;
    row.querySelector("[data-leave-actions]").remove();
    counters.forEach((c) => { c.textContent = Math.max(0, Number(c.textContent) - 1); });
    say(`${approved ? "Approved" : "Declined"} leave for ${name}.${approved && next ? ` It goes to ${next.replace(/^With /, "")} next.` : ""} They have been notified.`);
  }

  // An approve dialog, when the page has one, asks for an optional remark first.
  const approveDialog = document.getElementById("approve-dialog");
  let approving = null;
  if (approveDialog) {
    const approveRemark = approveDialog.querySelector("[data-approve-remark]");
    approveDialog.querySelector("[data-approve-form]").addEventListener("submit", (e) => {
      e.preventDefault();
      approveDialog.close();
      decide(approving, true, approveRemark.value.trim());
    });
    document.querySelectorAll("[data-leave-row] [data-leave-approve]").forEach((btn) => {
      btn.addEventListener("click", () => {
        approving = btn.closest("[data-leave-row]");
        const what = approving.querySelectorAll(".ds-cell-strong");
        approveDialog.querySelector("[data-approve-for]").textContent = `${what[1].textContent}, ${what[0].textContent}`;
        approveRemark.value = "";
      });
    });
  }

  const dialog = document.getElementById("decline-dialog");
  if (!dialog) return;
  const remark = dialog.querySelector("[data-decline-remark]");
  const error = dialog.querySelector("[data-decline-error]");
  let declining = null;
  document.querySelectorAll("[data-leave-row]").forEach((row) => {
    if (!approveDialog) row.querySelector("[data-leave-approve]")?.addEventListener("click", () => decide(row, true));
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
