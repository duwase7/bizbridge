// Small progressive enhancements: scroll reveal and number count-up.
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var items = document.querySelectorAll(".reveal, .opportunity-card, .request-card, .notification-card, .stat-tile, .detail-card, .dashboard-card");

  function countUp(el) {
    var target = parseInt(el.getAttribute("data-count"), 10) || 0;
    if (reduce || target === 0) { el.textContent = target; return; }
    var start = null, duration = 1200;
    function tick(t) {
      if (!start) start = t;
      var p = Math.min((t - start) / duration, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(tick);
    }
    el.textContent = "0";
    requestAnimationFrame(tick);
  }

  if (reduce || !("IntersectionObserver" in window)) {
    items.forEach(function (el) { el.classList.add("is-visible"); });
    return;
  }
  document.documentElement.classList.add("js-anim");
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      entry.target.querySelectorAll("[data-count]").forEach(countUp);
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12 });
  items.forEach(function (el, i) {
    el.style.transitionDelay = Math.min(i % 4, 3) * 80 + "ms";
    observer.observe(el);
  });
})();
