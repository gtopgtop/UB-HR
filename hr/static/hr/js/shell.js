// Behaviour for the Portal Layout shell: the remembered rail, the mobile drawer and
// collapsible nav groups. Also wires the component demos on the UI kit page (tabs,
// segmented control, dismissible alert, dialog). No framework, no build step.
(() => {
  const RAIL_KEY = "fms.sidebar.rail";
  const wide = window.matchMedia("(min-width: 1024px)");
  const sidebar = document.getElementById("sidebar");
  const railToggle = document.querySelector("[data-rail-toggle]");
  const drawerOpen = document.querySelector("[data-drawer-open]");
  const backdrop = document.querySelector("[data-drawer-close]");

  const saved = () => { try { return localStorage.getItem(RAIL_KEY) === "1"; } catch { return false; } };
  const save = (on) => { try { localStorage.setItem(RAIL_KEY, on ? "1" : "0"); } catch { /* private mode */ } };

  // Rail: only at and above 1024px. Each link gets a title so the icon has a tooltip.
  function applyRail(on) {
    const rail = on && wide.matches;
    sidebar.classList.toggle("is-rail", rail);
    railToggle.setAttribute("aria-pressed", String(rail));
    railToggle.querySelector(".ti").className = `ti ti-chevron-${rail ? "right" : "left"}`;
    railToggle.querySelector("span").textContent = rail ? "Expand" : "Collapse";
    sidebar.querySelectorAll(".ds-nav-link").forEach((link) => {
      if (rail) link.title = link.textContent.trim();
      else link.removeAttribute("title");
    });
  }
  railToggle.addEventListener("click", () => {
    const on = !sidebar.classList.contains("is-rail");
    save(on);
    applyRail(on);
  });

  // Drawer: below 1024px. Closed, the off-screen sidebar is inert so Tab skips it.
  function setDrawer(open) {
    const drawer = !wide.matches;
    sidebar.classList.toggle("is-open", drawer && open);
    sidebar.inert = drawer && !open;
    backdrop.hidden = !(drawer && open);
    drawerOpen.setAttribute("aria-expanded", String(drawer && open));
    if (drawer && open) sidebar.querySelector(".ds-nav-link").focus();
  }
  drawerOpen.addEventListener("click", () => setDrawer(true));
  backdrop.addEventListener("click", () => { setDrawer(false); drawerOpen.focus(); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sidebar.classList.contains("is-open")) { setDrawer(false); drawerOpen.focus(); }
  });

  wide.addEventListener("change", () => { setDrawer(false); applyRail(saved()); });
  applyRail(saved());
  setDrawer(false);

  // "View as": switching role opens that role's landing page.
  document.querySelector("[data-view-as] select")?.addEventListener("change", (e) => e.target.form.submit());

  // Collapsible nav groups.
  document.querySelectorAll("button.ds-nav-label[aria-controls]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const open = btn.getAttribute("aria-expanded") !== "true";
      btn.setAttribute("aria-expanded", String(open));
      document.getElementById(btn.getAttribute("aria-controls")).hidden = !open;
    });
  });

  // Tabs: ARIA tabs pattern with a roving tabindex. A tab with data-hash is linkable
  // (records/#pay opens the Pay tab) and writes its hash to the address bar.
  document.querySelectorAll('[role="tablist"]').forEach((list) => {
    const tabs = [...list.querySelectorAll('[role="tab"]')];
    const panelOf = (tab) => document.getElementById(tab.getAttribute("aria-controls"));
    function select(tab, { focus = true } = {}) {
      const from = tabs.findIndex((t) => t.getAttribute("aria-selected") === "true");
      const to = tabs.indexOf(tab);
      tabs.forEach((t) => {
        t.setAttribute("aria-selected", String(t === tab));
        t.tabIndex = t === tab ? 0 : -1;
        panelOf(t).hidden = true;
      });
      const panel = panelOf(tab);
      panel.hidden = false;
      panel.setAttribute("aria-labelledby", tab.id);
      if (focus && to !== from) {
        panel.style.setProperty("--fms-dir", to > from ? 1 : -1);
        panel.classList.remove("is-entering");
        void panel.offsetWidth; // restart the animation
        panel.classList.add("is-entering");
      }
      if (tab.dataset.hash && focus) history.replaceState(null, "", `#${tab.dataset.hash}`);
      if (focus) tab.focus();
    }
    const linked = tabs.find((t) => t.dataset.hash && `#${t.dataset.hash}` === location.hash);
    if (linked) select(linked, { focus: false });
    list.addEventListener("click", (e) => {
      const tab = e.target.closest('[role="tab"]');
      if (tab) select(tab);
    });
    list.addEventListener("keydown", (e) => {
      const i = tabs.indexOf(document.activeElement);
      const next = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (i < 0 || next === undefined) return;
      e.preventDefault();
      select(tabs[(next + tabs.length) % tabs.length]);
    });
  });

  // Segmented control: exactly one option pressed.
  document.querySelectorAll(".ds-segmented").forEach((group) => {
    group.addEventListener("click", (e) => {
      const option = e.target.closest(".ds-seg");
      if (!option) return;
      group.querySelectorAll(".ds-seg").forEach((s) => s.setAttribute("aria-pressed", String(s === option)));
    });
  });

  // Masked values (government IDs): Show swaps in the full value; aria-pressed carries the state.
  document.querySelectorAll("[data-reveal]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const value = document.getElementById(btn.getAttribute("aria-controls"));
      const show = btn.getAttribute("aria-pressed") !== "true";
      btn.setAttribute("aria-pressed", String(show));
      value.textContent = show ? value.dataset.full : value.dataset.masked;
      btn.querySelector(".ti").className = `ti ti-${show ? "eye-off" : "eye"}`;
      btn.querySelector("span").textContent = show ? "Hide" : "Show";
    });
  });

  // Dismissible alerts.
  document.querySelectorAll("[data-dismiss]").forEach((btn) => {
    btn.addEventListener("click", () => btn.closest(".ds-alert").remove());
  });

  // Page flash: the success alert at the top of a page. A button with data-say shows its message
  // there (the prototype's stand-in for an action that would be saved), then disables itself.
  const flash = document.querySelector("[data-flash]");
  if (flash) {
    flash.querySelector("[data-flash-close]")?.addEventListener("click", () => { flash.hidden = true; });
    document.querySelectorAll("[data-say]").forEach((btn) => {
      btn.addEventListener("click", () => {
        flash.querySelector("[data-flash-text]").textContent = btn.dataset.say;
        flash.hidden = false;
        if (!("sayRepeat" in btn.dataset)) btn.disabled = true;
      });
    });
  }

  // Table export: a button with data-csv-table="<table selector>" downloads that table as CSV, as it
  // stands (rows hidden by a filter are left out). Columns with no visible heading, such as row actions,
  // are skipped. data-csv-name sets the file name.
  const cellText = (cell) => cell.textContent.replace(/\s+/g, " ").trim();
  const quoteCSV = (v) => (/[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v);
  document.querySelectorAll("[data-csv-table]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const table = document.querySelector(btn.dataset.csvTable);
      const heads = [...table.tHead.rows[0].cells];
      const hiddenOnly = (th) => th.querySelector(".ds-sr-only") && cellText(th) === cellText(th.querySelector(".ds-sr-only"));
      const keep = heads.map((th) => cellText(th) !== "" && !hiddenOnly(th));
      const pick = (row) => [...row.cells].filter((_, i) => keep[i]).map(cellText);
      const body = [...table.tBodies].flatMap((tb) => [...tb.rows]).filter((tr) => !tr.hidden);
      const foot = table.tFoot ? [...table.tFoot.rows] : [];
      const rows = [pick(table.tHead.rows[0]), ...body.map(pick), ...foot.map(pick)];
      const csv = rows.map((r) => r.map(quoteCSV).join(",")).join("\r\n");
      const url = URL.createObjectURL(new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8;" })); // BOM so Excel reads UTF-8
      const a = document.createElement("a");
      a.href = url;
      a.download = btn.dataset.csvName || "export.csv";
      a.click();
      URL.revokeObjectURL(url);
      if (flash) {
        flash.querySelector("[data-flash-text]").textContent = `Downloaded ${a.download}: ${body.length} row${body.length === 1 ? "" : "s"}.`;
        flash.hidden = false;
      }
    });
  });

  // Stat tiles export: data-csv-stats="<grid selector>" downloads each tile's label, value and hint.
  document.querySelectorAll("[data-csv-stats]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tiles = [...document.querySelectorAll(`${btn.dataset.csvStats} .ds-stat`)];
      const pick = (tile, cls) => cellText(tile.querySelector(cls) || document.createElement("i"));
      const rows = [["Figure", "Value", "Detail"],
        ...tiles.map((t) => [pick(t, ".ds-stat-label"), pick(t, ".ds-stat-value"), pick(t, ".ds-stat-hint")])];
      const csv = rows.map((r) => r.map(quoteCSV).join(",")).join("\r\n");
      const url = URL.createObjectURL(new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8;" })); // BOM so Excel reads UTF-8
      const a = document.createElement("a");
      a.href = url;
      a.download = btn.dataset.csvName || "figures.csv";
      a.click();
      URL.revokeObjectURL(url);
      if (flash) {
        flash.querySelector("[data-flash-text]").textContent = `Downloaded ${a.download}: ${tiles.length} figures as of now.`;
        flash.hidden = false;
      }
    });
  });

  // Print a part of the page: fmsPrint([elements], "Heading") copies them into the print portal, which is
  // the only thing the print layout shows (app.css), so "Save as PDF" in the print dialog gives just that.
  window.fmsPrint = (elements, heading) => {
    let portal = document.querySelector(".fms-print-portal");
    if (!portal) {
      portal = document.createElement("div");
      portal.className = "fms-print-portal";
      document.body.append(portal);
    }
    const head = document.createElement("h1");
    head.className = "ds-panel-title";
    head.textContent = heading;
    portal.replaceChildren(head, ...elements.map((el) => {
      const copy = el.cloneNode(true);
      copy.hidden = false;
      return copy;
    }));
    window.print();
  };

  // Dialogs: native <dialog>. A click on the scrim closes it; focus returns to the opener.
  document.querySelectorAll("[data-dialog-open]").forEach((btn) => {
    btn.addEventListener("click", () => document.getElementById(btn.dataset.dialogOpen).showModal());
  });
  document.querySelectorAll("dialog.ds-modal").forEach((dialog) => {
    dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
    dialog.querySelectorAll("[data-dialog-close]").forEach((btn) => btn.addEventListener("click", () => dialog.close()));
  });
})();
