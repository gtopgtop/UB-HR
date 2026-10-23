// Evaluation breakdown, employee view (usability tasks 8 and 9): copy the AI interpretation as plain text,
// download the breakdown and the interpretation as a PDF (the browser's Save as PDF), and request a recheck.
// The disclaimer goes with every copy (plan §5.5). Prototype only: nothing is saved.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };
  const ai = document.querySelector("[data-ai]");
  const clean = (el) => el.textContent.replace(/\s+/g, " ").trim();

  ai.querySelector("[data-ai-copy]").addEventListener("click", async () => {
    const parts = [...ai.querySelectorAll("[data-ai-part]")].map((part) => {
      const items = [...part.querySelectorAll("li")].map((li) => `- ${clean(li)}`);
      return `${clean(part.querySelector("h3"))}\n${items.length ? items.join("\n") : clean(part.querySelector("p"))}`;
    });
    const text = [clean(ai.querySelector("[data-ai-label]")), ...parts].join("\n\n");
    try {
      await navigator.clipboard.writeText(text);
      say("Copied the interpretation, with its disclaimer.");
    } catch {
      say("Your browser blocked copying. Select the text and copy it instead.");
    }
  });

  ai.querySelector("[data-ai-pdf]").addEventListener("click", (e) => {
    const copy = ai.cloneNode(true);
    copy.querySelectorAll("[data-print-hide]").forEach((el) => el.remove());
    window.fmsPrint([...document.querySelector("[data-print-part]").children, copy], e.currentTarget.dataset.printTitle);
  });

  const dialog = document.getElementById("recheck-dialog");
  const reason = dialog.querySelector("[data-recheck-reason]");
  dialog.querySelector("[data-recheck-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!reason.value.trim()) {
      dialog.querySelector("[data-recheck-error]").hidden = false;
      reason.focus();
      return;
    }
    dialog.close();
    const open = document.querySelector("[data-recheck-open]");
    open.disabled = true;
    open.lastChild.textContent = "Recheck requested";
    say("Recheck sent to HR. Your rating stays as it is until HR resolves it, and you'll see their remarks here.");
  });
})();
