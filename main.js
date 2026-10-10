(() => {
  const styles = window.MOTION_STYLES;
  const grid = document.getElementById("grid");
  const count = document.getElementById("count");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Build the cards.
  grid.innerHTML = styles.map((s, i) => `
    <li class="card" data-tags="${s.tags.join(" ")}" style="transition-delay:${(i % 2) * 80}ms">
      <button type="button" class="card-button" data-index="${i}" aria-label="Open ${s.name} full size">
        <div class="media">
          <video data-src="videos/web/${s.id}.mp4" poster="posters/${s.id}.jpg" muted loop playsinline preload="none" aria-hidden="true"></video>
          <span class="num">${String(i + 1).padStart(2, "0")}</span>
        </div>
        <div class="body">
          <div class="title-row"><h3>${s.name}</h3><span class="tool">${s.tool}</span></div>
          <div class="tags">${s.tags.map(t => `<span class="tag">${t === "3d" ? "3D" : t}</span>`).join("")}</div>
          <p>${s.text}</p>
        </div>
      </button>
    </li>`).join("");

  // Load videos only when near the viewport; play while visible, pause when not.
  const videos = document.querySelectorAll("video[data-src]");
  const playIfAllowed = v => { if (!reduceMotion) v.play().catch(() => {}); };
  const io = new IntersectionObserver(entries => {
    for (const { target: v, isIntersecting } of entries) {
      if (isIntersecting) {
        if (!v.src) v.src = v.dataset.src;
        playIfAllowed(v);
      } else {
        v.pause();
      }
    }
  }, { rootMargin: "200px 0px", threshold: 0.15 });
  videos.forEach(v => io.observe(v));

  // With reduced motion, play a card's loop only on hover or keyboard focus.
  if (reduceMotion) {
    grid.querySelectorAll(".card-button").forEach(btn => {
      const v = btn.querySelector("video");
      const start = () => { if (!v.src) v.src = v.dataset.src; v.play().catch(() => {}); };
      const stop = () => v.pause();
      btn.addEventListener("mouseenter", start); btn.addEventListener("focus", start);
      btn.addEventListener("mouseleave", stop); btn.addEventListener("blur", stop);
    });
  }

  // Reveal cards as they scroll in (staggered, overlapping).
  const revealer = new IntersectionObserver(entries => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add("is-in"); revealer.unobserve(e.target); }
  }, { threshold: 0.1 });
  grid.querySelectorAll(".card").forEach(c => revealer.observe(c));

  // Filters.
  const chips = document.querySelectorAll(".chip");
  const applyFilter = f => {
    let shown = 0;
    grid.querySelectorAll(".card").forEach(c => {
      const match = f === "all" || c.dataset.tags.split(" ").includes(f);
      c.hidden = !match;
      if (match) shown++;
    });
    chips.forEach(ch => ch.setAttribute("aria-pressed", String(ch.dataset.filter === f)));
    count.textContent = `(${shown})`;
  };
  chips.forEach(ch => ch.addEventListener("click", () => applyFilter(ch.dataset.filter)));
  applyFilter("all");

  // Full-size viewer.
  const dialog = document.getElementById("viewer");
  const dv = document.getElementById("viewer-video");
  grid.addEventListener("click", e => {
    const btn = e.target.closest(".card-button");
    if (!btn) return;
    const s = styles[Number(btn.dataset.index)];
    dv.src = `videos/web/${s.id}.mp4`;
    dv.poster = `posters/${s.id}.jpg`;
    document.getElementById("viewer-title").textContent = s.name;
    document.getElementById("viewer-text").textContent = s.text;
    document.getElementById("viewer-meta").textContent = `${s.tool} · ${s.tags.map(t => t === "3d" ? "3D" : t).join(" · ")}`;
    dialog.showModal();
    playIfAllowed(dv);
  });
  dialog.addEventListener("close", () => { dv.pause(); dv.removeAttribute("src"); dv.load(); });
  dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); });
})();
