// Engagement surveys, HR officer view: build a survey (title, audience, questions) and save it as a draft.
// Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const dialog = document.getElementById("survey-dialog");
  const name = dialog.querySelector("[data-survey-name]");
  const audience = dialog.querySelector("[data-survey-audience]");
  const closes = dialog.querySelector("[data-survey-closes]");
  const questions = dialog.querySelector("[data-question-list]");
  const text = dialog.querySelector("[data-question-text]");
  const type = dialog.querySelector("[data-question-type]");
  const error = dialog.querySelector("[data-survey-error]");

  function addQuestion() {
    const q = text.value.trim();
    if (!q) { text.focus(); return; }
    const li = document.createElement("li");
    li.innerHTML = '<span class="fms-min0"><span class="fms-schedule-title"></span><span class="fms-caption"></span></span>'
      + '<button type="button" class="ds-row-action"><i class="ti ti-x" aria-hidden="true"></i></button>';
    li.querySelector(".fms-schedule-title").textContent = q;
    li.querySelector(".fms-caption").textContent = type.selectedOptions[0].textContent;
    const remove = li.querySelector("button");
    remove.setAttribute("aria-label", `Remove: ${q}`);
    remove.addEventListener("click", () => { li.remove(); text.focus(); });
    questions.append(li);
    text.value = "";
    text.focus();
  }
  dialog.querySelector("[data-question-add]").addEventListener("click", addQuestion);
  text.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); addQuestion(); }
  });

  dialog.querySelector("[data-survey-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const count = questions.children.length;
    if (!name.value.trim() || !count) {
      error.hidden = false;
      (name.value.trim() ? text : name).focus();
      return;
    }
    const when = closes.value
      ? `Closes ${new Date(`${closes.value}T00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" })}`
      : "Not scheduled";
    const row = document.createElement("tr");
    row.innerHTML = '<td><div class="ds-cell-strong"></div><div class="ds-cell-sub"></div></td><td></td>'
      + '<td><span class="ds-status"><span class="ds-dot"></span>Draft</span></td>'
      + '<td><span class="fms-caption">Not sent yet</span></td><td></td>';
    row.querySelector(".ds-cell-strong").textContent = name.value.trim();
    row.querySelector(".ds-cell-sub").textContent = `${count} question${count === 1 ? "" : "s"} · ${when}`;
    row.cells[1].textContent = audience.value;
    document.querySelector("[data-survey-list]").prepend(row);
    dialog.close();
    say(`Saved "${name.value.trim()}" as a draft for ${audience.value}.`);
    name.value = "";
    closes.value = "";
    questions.replaceChildren();
    error.hidden = true;
  });
})();
