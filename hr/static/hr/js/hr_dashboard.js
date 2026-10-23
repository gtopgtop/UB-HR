// HR dashboard: the department filter shows one pre-drawn chart set. The tooltip is chart_tip.js.
(() => {
  const filter = document.querySelector("[data-chart-filter]");
  const sets = document.querySelectorAll("[data-chart-set]");
  filter.addEventListener("change", () => {
    sets.forEach((set) => { set.hidden = set.dataset.chartSet !== filter.value; });
  });
})();
