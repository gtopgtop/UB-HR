// HR assistant, HR officer view: try the assistant as an employee would, add FAQs (from a handoff or
// blank) and edit answers employees marked not helpful.
// Matching is the assistant's own rule, from faq.js.
// Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const faqs = JSON.parse(document.getElementById("faq-data").textContent);
  const { words } = window.fmsFaq;
  const match = (question) => window.fmsFaq.match(faqs, question);

  // ── Tester ──
  const log = document.querySelector("[data-tester-log]");
  const field = document.querySelector("[data-tester-question]");
  const add = (mine, text, note) => {
    const li = document.createElement("li");
    li.className = `fms-bubble${mine ? " is-mine" : ""}`;
    li.innerHTML = '<div class="fms-caption"></div><p></p>';
    li.querySelector(".fms-caption").textContent = mine ? "Employee" : "HR assistant";
    li.querySelector("p").textContent = text;
    if (note) {
      const small = document.createElement("div");
      small.className = "fms-caption";
      small.textContent = note;
      li.append(small);
    }
    log.append(li);
  };
  function ask(question) {
    add(true, question);
    const { faq, hits } = match(question);
    if (hits >= 2) {
      add(false, faq.answer, `From the FAQ: ${faq.title} · ${hits} matching words`);
    } else {
      add(false, "I'm not sure about that one, so I've passed it to HR. They'll reply in Messages.",
        faq ? `Handed off · closest FAQ: ${faq.title} (low match)` : "Handed off · no FAQ matched");
    }
  }
  document.querySelector("[data-tester-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const q = field.value.trim();
    if (!q) { field.focus(); return; }
    ask(q);
    field.value = "";
  });
  document.querySelectorAll("[data-tester-chip]").forEach((chip) => {
    chip.addEventListener("click", () => ask(chip.textContent.trim()));
  });

  // ── Add an FAQ (from a handoff, or blank) and edit an answer marked not helpful ──
  const dialog = document.getElementById("faq-dialog");
  const question = dialog.querySelector("[data-faq-question]");
  const answer = dialog.querySelector("[data-faq-answer]");
  const keywords = dialog.querySelector("[data-faq-keywords]");
  const error = dialog.querySelector("[data-faq-error]");
  const count = document.querySelector("[data-handoff-count]");
  let from = null;
  let editing = null; // the FAQ being edited, or null when adding
  const prepare = (btn, heading, asker) => {
    from = btn;
    dialog.querySelector("[data-faq-heading]").textContent = heading;
    dialog.querySelector("[data-faq-asker]").textContent = asker;
    dialog.querySelector("[data-faq-asker-note]").hidden = !asker;
    error.hidden = true;
  };
  document.querySelectorAll("[data-add-faq]").forEach((btn) => {
    btn.addEventListener("click", () => {
      prepare(btn, "Add an FAQ", btn.dataset.addFaqName);
      editing = null;
      question.value = btn.dataset.addFaq;
      answer.value = "";
      keywords.value = "";
    });
  });
  document.querySelectorAll("[data-edit-faq]").forEach((btn) => {
    btn.addEventListener("click", () => {
      prepare(btn, "Edit the FAQ answer", "");
      editing = faqs.find((f) => f.title === btn.dataset.editFaq);
      question.value = editing.title;
      answer.value = editing.answer;
      keywords.value = editing.keywords.join(", ");
    });
  });
  dialog.querySelector("[data-faq-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!question.value.trim() || !answer.value.trim()) {
      error.hidden = false;
      (question.value.trim() ? answer : question).focus();
      return;
    }
    // Typed match words, or the question's longer words when none are given.
    const typed = keywords.value.split(",").flatMap((k) => [...words(k)]);
    const own = [...words(question.value)].filter((w) => w.length > 3);
    const entry = { title: question.value.trim(), keywords: typed.length ? typed : own, answer: answer.value.trim() };
    dialog.close();
    if (editing) {
      Object.assign(editing, entry);
      from.closest("li").querySelector(".fms-caption").textContent = "Answer updated today";
      from.remove();
      say(`Updated the "${entry.title}" answer. The assistant uses it from now on.`);
      return;
    }
    faqs.unshift(entry);
    const row = from.closest("[data-handoff-row]");
    if (row) {
      row.remove();
      count.textContent = Math.max(0, Number(count.textContent) - 1);
      say(`Saved "${entry.title}" as an FAQ and answered ${from.dataset.addFaqName}. Try it in the tester.`);
    } else {
      say(`Saved "${entry.title}" as an FAQ. Try it in the tester.`);
    }
  });
})();
