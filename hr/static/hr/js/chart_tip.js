// Chart tooltip for the server-drawn SVG charts. Every mark's hit target carries data-tip;
// hover or keyboard focus shows it beside the mark. Needs one [data-chart-tip] element on the page.
(() => {
  const tip = document.querySelector("[data-chart-tip]");
  if (!tip) return;
  function show(target) {
    tip.textContent = target.dataset.tip;
    tip.hidden = false;
    const box = target.getBoundingClientRect();
    const x = Math.min(window.innerWidth - tip.offsetWidth - 8, Math.max(8, box.left + box.width / 2 - tip.offsetWidth / 2));
    const y = box.top - tip.offsetHeight - 8;
    tip.style.left = `${x}px`;
    tip.style.top = `${y < 8 ? box.bottom + 8 : y}px`;
    target.closest("svg")?.querySelectorAll(".is-hover").forEach((el) => el.classList.remove("is-hover"));
    target.previousElementSibling?.classList.add("is-hover"); // the mark drawn just before its hit target
  }
  function hide() {
    tip.hidden = true;
    document.querySelectorAll(".fms-chart .is-hover").forEach((el) => el.classList.remove("is-hover"));
  }
  document.querySelectorAll("[data-tip]").forEach((el) => {
    el.addEventListener("pointerenter", () => show(el));
    el.addEventListener("pointerleave", hide);
    el.addEventListener("focus", () => show(el));
    el.addEventListener("blur", hide);
  });
  window.addEventListener("scroll", hide, { passive: true });
})();
