// My records, employee view: switch payslips, print one, upload to the 201 file and request a correction.
// Government IDs use the shell's Show/Hide. Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };

  // ── Payslips ──
  document.querySelectorAll("[data-payslip]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-payslip]").forEach((b) => {
        if (b === btn) b.setAttribute("aria-current", "true");
        else b.removeAttribute("aria-current");
      });
      document.querySelectorAll("[data-payslip-pane]").forEach((p) => { p.hidden = p.dataset.payslipPane !== btn.dataset.payslip; });
    });
  });
  // Print only the payslip on screen.
  document.querySelectorAll("[data-print-payslip]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const pane = btn.closest("[data-payslip-pane]");
      window.fmsPrint([pane], btn.dataset.printTitle);
    });
  });

  const row = (cells) => {
    const tr = document.createElement("tr");
    tr.innerHTML = cells;
    return tr;
  };

  // ── 201 file upload ──
  const upload = document.getElementById("upload-dialog");
  upload.querySelector("[data-upload-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const file = upload.querySelector("[data-upload-file]");
    if (!file.files.length) {
      upload.querySelector("[data-upload-error]").hidden = false;
      file.focus();
      return;
    }
    const name = upload.querySelector("[data-upload-name]").value;
    const tr = row('<th scope="row" class="ds-cell-strong"></th><td><span class="ds-status v-info"><span class="ds-dot d-info"></span>HR is checking</span></td><td>Uploaded today</td>');
    tr.querySelector("th").textContent = name;
    document.querySelector("[data-file-list]").prepend(tr);
    upload.close();
    upload.querySelector("[data-upload-form]").reset();
    upload.querySelector("[data-upload-error]").hidden = true;
    say(`Uploaded ${name}. HR checks it before it joins your 201 file.`);
  });

  // ── Correction request ──
  const corr = document.getElementById("correction-dialog");
  const value = corr.querySelector("[data-correction-new]");
  corr.querySelector("[data-correction-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!value.value.trim()) {
      corr.querySelector("[data-correction-error]").hidden = false;
      value.focus();
      return;
    }
    const field = corr.querySelector("[data-correction-field]").value;
    const proof = corr.querySelector("[data-correction-proof]").files[0];
    const tr = row('<th scope="row" class="ds-cell-strong"></th><td></td><td>Today</td><td><span class="ds-status v-warning"><span class="ds-dot d-warning"></span>With HR</span></td>');
    tr.querySelector("th").textContent = field;
    if (proof) {
      const sub = document.createElement("div");
      sub.className = "ds-cell-sub";
      sub.textContent = proof.name;
      tr.querySelector("th").append(sub);
    }
    tr.cells[1].textContent = `Change to: ${value.value.trim()}`;
    document.querySelector("[data-correction-list]").prepend(tr);
    corr.close();
    corr.querySelector("[data-correction-form]").reset();
    corr.querySelector("[data-correction-error]").hidden = true;
    say(`Sent your ${field.toLowerCase()} correction to HR. You'll get a notification when it's reviewed.`);
  });
})();
