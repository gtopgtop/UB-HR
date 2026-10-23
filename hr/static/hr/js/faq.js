// The HR assistant's matching rule (plan §3 Module 4), shared by the employee's assistant and HR's tester:
// a question needs 2 matching words for an answer; fewer is handed off to HR, with the closest FAQ noted
// (ties keep the earlier FAQ).
window.fmsFaq = (() => {
  const words = (text) => new Set(text.toLowerCase().match(/[a-z0-9]+/g) || []);
  function match(faqs, question) {
    const asked = words(question);
    let best = null;
    let hits = 0;
    faqs.forEach((faq) => {
      const n = faq.keywords.filter((k) => asked.has(k)).length;
      if (n > hits) { best = faq; hits = n; }
    });
    return { faq: best, hits, answered: hits >= 2 };
  }
  return { words, match };
})();
