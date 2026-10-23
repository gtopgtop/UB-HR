// HR assistant, employee view (usability task 7): answer from the FAQ (faq.js), let the employee rate the
// answer, and hand an unmatched question to HR. Prototype only: nothing is saved.
(() => {
  const faqs = JSON.parse(document.getElementById("faq-data").textContent);
  const log = document.querySelector("[data-chat-log]");
  const field = document.querySelector("[data-chat-question]");
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };

  const bubble = (mine, text, note) => {
    const li = document.createElement("li");
    li.className = `fms-bubble${mine ? " is-mine" : ""}`;
    li.innerHTML = '<div class="fms-caption"></div><p></p>';
    li.querySelector(".fms-caption").textContent = mine ? "You" : "HR assistant";
    li.querySelector("p").textContent = text;
    if (note) {
      const small = document.createElement("div");
      small.className = "fms-caption";
      small.textContent = note;
      li.append(small);
    }
    log.append(li);
    return li;
  };
  const actions = (li, buttons) => {
    const row = document.createElement("div");
    row.className = "fms-row";
    buttons.forEach(([label, onClick]) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "ds-btn ds-btn-ghost ds-btn-sm";
      b.textContent = label;
      b.addEventListener("click", () => { onClick(); row.remove(); });
      row.append(b);
    });
    li.append(row);
  };

  function ask(question) {
    bubble(true, question);
    const { faq, answered } = window.fmsFaq.match(faqs, question);
    if (answered) {
      const li = bubble(false, faq.answer, `From the FAQ: ${faq.title}`);
      actions(li, [
        ["Helpful", () => say("Thanks for the feedback.")],
        ["Not helpful", () => say("Thanks. HR reviews answers marked not helpful.")],
      ]);
    } else {
      const li = bubble(false, "I'm not sure about that one. Shall I pass it to HR? They usually reply within a working day.");
      actions(li, [
        ["Send to HR", () => {
          bubble(false, "Sent to HR. Their reply will appear in your Messages.");
          say("Your question was sent to HR.");
        }],
        ["No, thanks", () => {}],
      ]);
    }
  }
  document.querySelector("[data-chat-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const q = field.value.trim();
    if (!q) { field.focus(); return; }
    ask(q);
    field.value = "";
  });
  document.querySelectorAll("[data-chat-chip]").forEach((chip) => chip.addEventListener("click", () => ask(chip.textContent.trim())));
})();
