// Verify the proof behind a requirement or a 201-file upload (_verify_dialog.html). A Verify button carries
// data-verify-name, data-verify-item, data-verify-proof and data-verify-done (what accepting it does), and sits in a [data-req-row] whose
// [data-req-status] cell shows the outcome. On the career tracker, an accepted item also moves the
// "met" count. Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const verifyDialog = document.getElementById("verify-dialog");
  const remark = verifyDialog.querySelector("[data-verify-remark]");
  const remarkError = verifyDialog.querySelector("[data-verify-error]");
  let verifying = null;
  document.querySelectorAll("[data-verify]").forEach((btn) => {
    btn.addEventListener("click", () => {
      verifying = btn;
      const { verifyName, verifyItem, verifyProof } = btn.dataset;
      verifyDialog.querySelector("[data-verify-for]").textContent = `${verifyItem} for ${verifyName}`;
      verifyDialog.querySelector("[data-verify-file]").textContent = verifyProof;
      verifyDialog.querySelector("[data-verify-done]").textContent = btn.dataset.verifyDone || "";
      verifyDialog.querySelectorAll("[data-verify-outcome]").forEach((s) => {
        s.setAttribute("aria-pressed", String(s.dataset.verifyOutcome === "accept"));
      });
      remark.value = "";
      remarkError.hidden = true;
      remark.removeAttribute("aria-invalid");
      verifyDialog.showModal();
    });
  });
  verifyDialog.querySelector("[data-verify-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const accepted = verifyDialog.querySelector('[data-verify-outcome="accept"]').getAttribute("aria-pressed") === "true";
    const text = remark.value.trim();
    if (!accepted && !text) {
      remarkError.hidden = false;
      remark.setAttribute("aria-invalid", "true");
      remark.focus();
      return;
    }
    const { verifyName, verifyItem } = verifying.dataset;
    const tone = accepted ? "success" : "error";
    verifying.closest("[data-req-row]").querySelector("[data-req-status]").innerHTML =
      `<span class="ds-status v-${tone}"><span class="ds-dot d-${tone}"></span>${accepted ? "Verified today" : "Sent back"}</span>`;

    // On the tracker, an accepted item moves the "met" count.
    const person = verifying.closest("[data-tracker-person]");
    if (person && accepted) {
      const met = person.querySelector("[data-tracker-met]");
      const total = Number(met.parentElement.textContent.match(/of (\d+)/)[1]);
      met.textContent = Number(met.textContent) + 1;
      person.querySelector("[data-tracker-met-bar]").style.width = `${Math.round((Number(met.textContent) / total) * 100)}%`;
    }
    verifying.remove();
    verifyDialog.close();
    say(accepted
      ? `Verified ${verifyItem} for ${verifyName}. ${verifying.dataset.verifyDone || ""}`.trim()
      : `Sent ${verifyItem} back to ${verifyName}: ${text}`);
  });

})();
