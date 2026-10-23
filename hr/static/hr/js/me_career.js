// My career, employee view: move a goal's progress and add a goal. Prototype only: nothing is saved.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const wire = (goal) => {
    const range = goal.querySelector("[data-goal-range]");
    range.addEventListener("input", () => { goal.querySelector("[data-goal-value]").textContent = `${range.value}%`; });
    range.addEventListener("change", () => {
      goal.querySelector("[data-goal-updated]").textContent = "Updated today";
      say(`Saved: ${goal.querySelector("label").textContent} at ${range.value}%.`);
    });
  };
  document.querySelectorAll("[data-goal]").forEach(wire);

  const dialog = document.getElementById("goal-dialog");
  const text = dialog.querySelector("[data-goal-text]");
  let made = 0;
  dialog.querySelector("[data-goal-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!text.value.trim()) {
      dialog.querySelector("[data-goal-error]").hidden = false;
      text.focus();
      return;
    }
    const goal = document.querySelector("[data-goal]").cloneNode(true);
    const id = `goal-new-${(made += 1)}`;
    goal.querySelector("label").textContent = text.value.trim();
    goal.querySelector("label").htmlFor = id;
    const range = goal.querySelector("[data-goal-range]");
    range.id = id;
    range.value = 0;
    goal.querySelector("[data-goal-value]").textContent = "0%";
    goal.querySelector("[data-goal-updated]").textContent = "Added today";
    document.querySelector("[data-goal-list]").append(goal);
    wire(goal);
    dialog.close();
    say(`Added your goal: ${text.value.trim()}. Your principal can see it now.`);
    text.value = "";
    dialog.querySelector("[data-goal-error]").hidden = true;
  });
})();
