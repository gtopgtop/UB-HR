// Settings: each risk-weight form keeps a running total. Saving is allowed only at exactly 100%;
// Reset puts back the defaults the page was drawn with.
(() => {
  document.querySelectorAll("[data-weights]").forEach((form) => {
    const inputs = [...form.querySelectorAll("[data-weight]")];
    const total = form.querySelector("[data-weight-total]");
    const sum = form.querySelector("[data-weight-sum]");
    const note = form.querySelector("[data-weight-note]");
    const save = form.querySelector("[data-weight-save]");

    function update() {
      const value = inputs.reduce((acc, input) => acc + (Number(input.value) || 0), 0);
      const off = value !== 100;
      sum.textContent = `${value}%`;
      note.textContent = off ? `must be 100% (${value > 100 ? "over" : "under"} by ${Math.abs(value - 100)})` : "of 100%";
      total.classList.toggle("is-off", off);
      inputs.forEach((input) => input.setAttribute("aria-invalid", String(off)));
      save.disabled = off;
    }

    form.addEventListener("input", update);
    form.querySelector("[data-weight-reset]").addEventListener("click", () => {
      inputs.forEach((input) => { input.value = input.dataset.default; });
      update();
    });
    update();
  });
})();
