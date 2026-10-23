// My wellness, employee view (usability tasks 5 and 6): save today's check-in, send an anonymous concern
// with a claim code, share check-ins with the wellness officer, ask for a counselor and take the survey.
// Prototype only: nothing is saved, and a reload resets the page.
(() => {
  const flash = document.querySelector("[data-flash]");
  const say = (text) => {
    flash.querySelector("[data-flash-text]").textContent = text;
    flash.hidden = false;
  };

  // ── Today's check-in: one a day, editable the same day ──
  const checkin = document.querySelector("[data-checkin-form]");
  const badge = document.querySelector("[data-checkin-badge]");
  let saved = false;
  checkin.addEventListener("submit", (e) => {
    e.preventDefault();
    const mood = checkin.querySelector('input[name="mood"]:checked');
    const stress = checkin.querySelector('input[name="stress"]:checked');
    const error = checkin.querySelector("[data-checkin-error]");
    if (!mood || !stress) {
      error.hidden = false;
      (mood ? checkin.querySelector('input[name="stress"]') : checkin.querySelector('input[name="mood"]')).focus();
      return;
    }
    error.hidden = true;
    const rows = document.querySelector("[data-checkin-rows]");
    if (saved) rows.firstElementChild.remove();
    const tr = document.createElement("tr");
    tr.innerHTML = `<th scope="row">Oct 12</th><td class="a-right">${mood.value}</td><td class="a-right">${stress.value}</td>`;
    rows.prepend(tr);
    badge.className = "ds-badge v-success";
    badge.textContent = "Checked in";
    checkin.querySelector("[data-checkin-submit]").lastChild.textContent = "Update check-in";
    say(saved
      ? `Check-in updated: mood ${mood.value}, stress ${stress.value}.`
      : `Checked in: mood ${mood.value}, stress ${stress.value}. Your trend now includes today.`);
    saved = true;
  });

  // ── Anonymous concern ──
  const concern = document.querySelector("[data-concern-form]");
  concern.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = concern.querySelector("[data-concern-text]");
    if (!text.value.trim()) {
      concern.querySelector("[data-concern-error]").hidden = false;
      text.focus();
      return;
    }
    const topic = concern.querySelector("[data-concern-topic]").selectedOptions[0];
    const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // no 0/O or 1/I to misread
    const code = Array.from(crypto.getRandomValues(new Uint8Array(8)), (n) => alphabet[n % alphabet.length])
      .join("").replace(/(.{4})/, "$1-");
    const done = document.querySelector("[data-concern-done]");
    done.querySelector("[data-concern-code]").textContent = code;
    done.querySelector("[data-concern-route]").textContent = `Your ${topic.value.toLowerCase()} concern went to ${"wellness" in topic.dataset ? "the wellness office" : "HR"}.`;
    done.hidden = false;
    concern.reset();
    concern.hidden = true;
  });

  // ── Consent: share check-ins with the wellness officer for 90 days ──
  const consent = document.querySelector("[data-consent]");
  const status = document.querySelector("[data-consent-status]");
  consent.addEventListener("change", () => {
    status.textContent = consent.checked
      ? "Shared with the wellness officer until Jan 10, 2027. Every view is logged, and you can stop any time."
      : "Not shared. Only you see your check-ins.";
    say(consent.checked ? "Your check-ins are now shared with the wellness officer for 90 days." : "Sharing stopped. The wellness officer can no longer see your check-ins.");
  });

  // ── Counselor request ──
  const counselor = document.getElementById("counselor-dialog");
  counselor.querySelector("[data-counselor-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const anon = counselor.querySelector("[data-counselor-anon]").checked;
    const mode = counselor.querySelector("[data-counselor-mode]").value.toLowerCase();
    counselor.close();
    say(`Request sent to the wellness office (${mode}${anon ? ", without your name" : ""}). They'll reply within 2 working days.`);
  });

  // ── Survey ──
  const survey = document.getElementById("take-survey-dialog");
  survey.querySelector("[data-take-survey-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    survey.close();
    const card = document.querySelector("[data-survey-card]");
    card.innerHTML = '<p class="fms-muted"><i class="ti ti-circle-check" aria-hidden="true"></i> Answered, thank you. Your answers are stored without your name.</p>';
    say("Survey answers sent anonymously.");
  });
})();
