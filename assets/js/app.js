/* Blush and Blue storefront: theme, bag, quick add, shop filters, product page, WhatsApp checkout. */
(() => {
  const WA = "27615107109";
  const STORE = "bb-bag-v1";
  const FREE_OVER = 1500;
  const DELIVERY = {
    courier: { label: "Door-to-door courier", fee: 120 },
    postnet: { label: "PostNet to PostNet", fee: 109 },
  };

  const root = document.documentElement;
  const r = document.body.dataset.root || "";
  const products = window.BB_PRODUCTS || [];
  const bySlug = Object.fromEntries(products.map((p) => [p.slug, p]));
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const icon = (n) => `<svg class="icon" aria-hidden="true"><use href="#i-${n}"></use></svg>`;
  const money = (n) => "R " + Math.round(n).toLocaleString("en-ZA").replace(/[,.]/g, " ").replace(/ /g, " ");
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const safeStore = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch {} },
  };

  /* Theme */
  function applyTheme(theme) {
    root.dataset.theme = theme;
    safeStore.set("bb-theme", theme);
    const c = theme === "dark" ? "#0b1324" : "#fbf1ee";
    $$('meta[name="theme-color"]').forEach((m) => m.setAttribute("content", c));
    $$("[data-theme-toggle]").forEach((b) => {
      b.setAttribute("aria-pressed", String(theme === "dark"));
      b.setAttribute("aria-label", theme === "dark" ? "Switch to the Blush light theme" : "Switch to the Blue dark theme");
    });
  }
  function toggleTheme(e) {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    if (!document.startViewTransition || reduced()) return applyTheme(next);
    const box = e.currentTarget.getBoundingClientRect();
    const x = box.left + box.width / 2, y = box.top + box.height / 2;
    const end = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    const vt = document.startViewTransition(() => applyTheme(next));
    vt.ready.then(() => {
      root.animate(
        { clipPath: [`circle(0 at ${x}px ${y}px)`, `circle(${end}px at ${x}px ${y}px)`] },
        { duration: 620, easing: "cubic-bezier(.32,.72,0,1)", pseudoElement: "::view-transition-new(root)" }
      );
    });
  }
  applyTheme(root.dataset.theme === "dark" ? "dark" : "light");
  $$("[data-theme-toggle]").forEach((b) => b.addEventListener("click", toggleTheme));

  /* Header turns solid once the hero has passed */
  const head = $(".site-head");
  const hero = $(".hero");
  if (hero && head) {
    new IntersectionObserver(([en]) => head.classList.toggle("is-stuck", !en.isIntersecting), { rootMargin: "-90px 0px 0px 0px" }).observe(hero);
  }

  /* One-time image reveals on the landing page */
  const reveals = $$(".reveal");
  if (reveals.length) {
    const io = new IntersectionObserver((ents) => ents.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
    }), { rootMargin: "0px 0px -8% 0px" });
    reveals.forEach((el) => io.observe(el));
  }

  /* Dialog helpers: click on backdrop closes */
  $$("dialog").forEach((d) => d.addEventListener("click", (e) => { if (e.target === d) d.close(); }));
  $$("[data-close]").forEach((b) => b.addEventListener("click", () => b.closest("dialog").close()));
  $$("[data-open-menu]").forEach((b) => b.addEventListener("click", () => $("#menu").showModal()));

  /* Bag */
  let bag = [];
  try { bag = JSON.parse(safeStore.get(STORE) || "[]").filter((l) => bySlug[l.slug]); } catch { bag = []; }
  const count = () => bag.reduce((s, l) => s + l.qty, 0);
  const subtotal = () => bag.reduce((s, l) => s + bySlug[l.slug].price * l.qty, 0);
  const saveBag = () => { safeStore.set(STORE, JSON.stringify(bag)); renderBag(); };

  function addToBag(slug, size, colour, qty = 1) {
    const hit = bag.find((l) => l.slug === slug && l.size === size && l.colour === colour);
    if (hit) hit.qty = Math.min(20, hit.qty + qty);
    else bag.push({ slug, size, colour, qty });
    saveBag();
    $$(".bag-count").forEach((c) => {
      c.classList.add("bump");
      setTimeout(() => c.classList.remove("bump"), 240);
    });
  }

  function lineHTML(l, i, compact) {
    const p = bySlug[l.slug];
    const opts = [l.colour, p.sizes.length > 1 || p.sizes[0] !== "One size" ? "Size " + l.size : ""].filter(Boolean).join(", ");
    return `<li class="line">
      <a class="line__img" href="${r}product/${p.slug}.html" tabindex="-1" aria-hidden="true"><img src="${r}assets/img/products/${p.images[0]}.webp" alt="" width="92" height="92" loading="lazy"></a>
      <div>
        <a class="line__name" href="${r}product/${p.slug}.html">${esc(p.name)}</a>
        <div class="line__meta">${esc(opts)}${compact ? "<br>Qty " + l.qty : ""}</div>
        ${compact ? "" : `<div class="line__actions">
          <div class="stepper" role="group" aria-label="Quantity of ${esc(p.name)}">
            <button type="button" data-step="-1" data-i="${i}" aria-label="One less">${icon("minus")}</button>
            <output>${l.qty}</output>
            <button type="button" data-step="1" data-i="${i}" aria-label="One more">${icon("plus")}</button>
          </div>
          <button type="button" class="line__remove" data-remove="${i}">Remove</button>
        </div>`}
      </div>
      <div class="line__price">${money(p.price * l.qty)}</div>
    </li>`;
  }

  function renderBag() {
    const n = count();
    $$(".bag-count").forEach((c) => { c.textContent = n; c.hidden = n === 0; });
    const body = $("#bag-body");
    if (!body) return;
    if (!bag.length) {
      body.innerHTML = `<div class="empty"><h3>Your bag is empty</h3><p>Add something you like and it will wait for you here.</p>
        <div class="empty__links"><a class="btn btn--ghost" href="${r}shop.html?dept=ladies">Shop ladies</a><a class="btn btn--ghost" href="${r}shop.html?dept=mens">Shop mens</a></div></div>`;
      $("#bag-foot").hidden = true;
      return;
    }
    $("#bag-foot").hidden = false;
    body.innerHTML = `<ul>${bag.map((l, i) => lineHTML(l, i, false)).join("")}</ul>`;
    const sub = subtotal();
    $("#bag-total").textContent = money(sub);
    $("#bag-note").textContent = sub >= FREE_OVER
      ? "Your order qualifies for free delivery."
      : `Add ${money(FREE_OVER - sub)} more for free delivery. Delivery is worked out at checkout.`;
  }
  document.addEventListener("click", (e) => {
    const step = e.target.closest("[data-step]");
    if (step) {
      const l = bag[+step.dataset.i];
      l.qty = Math.min(20, l.qty + +step.dataset.step);
      if (l.qty < 1) bag.splice(+step.dataset.i, 1);
      saveBag();
      if (document.body.dataset.page === "checkout") renderCheckout();
      return;
    }
    const rm = e.target.closest("[data-remove]");
    if (rm) {
      bag.splice(+rm.dataset.remove, 1);
      saveBag();
      if (document.body.dataset.page === "checkout") renderCheckout();
    }
  });
  const openBag = () => { const d = $("#bag"); if (d && !d.open) d.showModal(); };
  $$("[data-open-bag]").forEach((b) => b.addEventListener("click", openBag));

  /* Quick add from a product card */
  const quick = $("#quick");
  let quickState = null;
  function openQuick(slug) {
    const p = bySlug[slug];
    const one = p.sizes.length === 1 && p.sizes[0] === "One size";
    if (one) { addToBag(slug, p.sizes[0], p.colours[0][0]); openBag(); return; }
    quickState = { slug, size: null };
    $("#quick-img").src = `${r}assets/img/products/${p.images[0]}.webp`;
    $("#quick-name").textContent = p.name;
    $("#quick-price").textContent = money(p.price);
    $("#quick-colour").textContent = p.colours[0][0];
    $("#quick-link").href = `${r}product/${p.slug}.html`;
    $("#quick-sizes").innerHTML = p.sizes.map((s) => `<button type="button" class="chip" aria-pressed="false" data-size="${esc(s)}">${esc(s)}</button>`).join("");
    $("#quick-error").hidden = true;
    quick.showModal();
  }
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-quick]");
    if (b) { e.preventDefault(); openQuick(b.dataset.quick); }
  });
  if (quick) {
    $("#quick-sizes").addEventListener("click", (e) => {
      const c = e.target.closest("[data-size]");
      if (!c) return;
      $$("#quick-sizes .chip").forEach((x) => x.setAttribute("aria-pressed", String(x === c)));
      quickState.size = c.dataset.size;
      $("#quick-error").hidden = true;
    });
    $("#quick-add").addEventListener("click", () => {
      if (!quickState.size) { $("#quick-error").hidden = false; return; }
      addToBag(quickState.slug, quickState.size, bySlug[quickState.slug].colours[0][0]);
      quick.close();
      openBag();
    });
  }

  /* Landing rail arrows */
  $$("[data-rail]").forEach((b) => b.addEventListener("click", () => {
    const rail = $("#" + b.dataset.target);
    rail.scrollBy({ left: +b.dataset.rail * rail.clientWidth * 0.75, behavior: reduced() ? "auto" : "smooth" });
  }));

  /* Shop filters. Every card is in the HTML already, so this only hides and sorts them. */
  const grid = $("#shop-grid");
  if (grid) {
    const cards = $$(".card", grid);
    const original = cards.slice();
    const q0 = new URLSearchParams(location.search);
    const state = { dept: q0.get("dept") || "all", cat: q0.get("cat") || "all", tag: q0.get("tag") || "", q: q0.get("q") || "", sort: q0.get("sort") || "featured" };
    const search = $("#shop-search");
    const sort = $("#shop-sort");
    search.value = state.q;
    sort.value = state.sort;
    const TITLES = {
      "all/all": "The full range", "ladies/all": "Ladies", "mens/all": "Mens", "all/shoes": "Shoes", "all/clothing": "Clothing", "all/accessories": "Accessories",
      "ladies/shoes": "Ladies shoes", "ladies/clothing": "Ladies clothing", "ladies/accessories": "Ladies accessories",
      "mens/shoes": "Mens shoes", "mens/clothing": "Mens clothing", "mens/accessories": "Mens accessories",
    };
    function apply(push) {
      const q = state.q.trim().toLowerCase();
      let shown = 0;
      cards.forEach((c) => {
        const ok = (state.dept === "all" || c.dataset.dept === state.dept)
          && (state.cat === "all" || c.dataset.cat === state.cat)
          && (!state.tag || c.dataset.tags.split(" ").includes(state.tag))
          && (!q || c.dataset.search.includes(q));
        c.hidden = !ok;
        if (ok) shown++;
      });
      const ordered = state.sort === "featured" ? original
        : cards.slice().sort((a, b) => (state.sort === "low" ? 1 : -1) * (+a.dataset.price - +b.dataset.price));
      ordered.forEach((c) => grid.appendChild(c));
      $$("[data-filter-dept]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.filterDept === state.dept)));
      $$("[data-filter-cat]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.filterCat === state.cat)));
      const tagged = state.tag === "summer" ? "Ready for summer" : state.tag === "new" ? "New in" : TITLES[`${state.dept}/${state.cat}`];
      $("#shop-title").textContent = tagged || "The full range";
      $("#shop-count").textContent = `${shown} ${shown === 1 ? "piece" : "pieces"}`;
      $("#shop-empty").hidden = shown > 0;
      if (push) {
        const u = new URLSearchParams();
        if (state.dept !== "all") u.set("dept", state.dept);
        if (state.cat !== "all") u.set("cat", state.cat);
        if (state.tag) u.set("tag", state.tag);
        if (state.q) u.set("q", state.q);
        if (state.sort !== "featured") u.set("sort", state.sort);
        const s = u.toString();
        history.replaceState(null, "", location.pathname + (s ? "?" + s : ""));
      }
    }
    $$("[data-filter-dept]").forEach((b) => b.addEventListener("click", () => { state.dept = b.dataset.filterDept; state.tag = ""; apply(true); }));
    $$("[data-filter-cat]").forEach((b) => b.addEventListener("click", () => { state.cat = b.dataset.filterCat; state.tag = ""; apply(true); }));
    search.addEventListener("input", () => { state.q = search.value; apply(true); });
    sort.addEventListener("change", () => { state.sort = sort.value; apply(true); });
    $("#shop-clear").addEventListener("click", () => {
      Object.assign(state, { dept: "all", cat: "all", tag: "", q: "" });
      search.value = "";
      apply(true);
    });
    apply(false);
  }

  /* Product page */
  const pdp = $("#pdp");
  if (pdp) {
    const p = bySlug[pdp.dataset.slug];
    const st = { size: p.sizes.length === 1 ? p.sizes[0] : null, qty: 1 };
    $$("[data-pick-size]").forEach((c) => c.addEventListener("click", () => {
      st.size = c.dataset.pickSize;
      $$("[data-pick-size]").forEach((x) => x.setAttribute("aria-pressed", String(x === c)));
      $("#size-picked").textContent = st.size;
      $("#size-error").hidden = true;
    }));
    const qtyOut = $("#qty");
    $$("[data-qty]").forEach((b) => b.addEventListener("click", () => {
      st.qty = Math.max(1, Math.min(20, st.qty + +b.dataset.qty));
      qtyOut.textContent = st.qty;
    }));
    const add = () => {
      if (!st.size) {
        $("#size-error").hidden = false;
        $("#size-block").scrollIntoView({ block: "center", behavior: reduced() ? "auto" : "smooth" });
        return;
      }
      addToBag(p.slug, st.size, p.colours[0][0], st.qty);
      openBag();
    };
    $$("[data-add]").forEach((b) => b.addEventListener("click", add));
    $$("[data-thumb]").forEach((t) => t.addEventListener("click", () => {
      const main = $("#pdp-main");
      main.src = t.dataset.thumb;
      main.classList.toggle("is-photo", t.dataset.photo === "1");
      $$("[data-thumb]").forEach((x) => x.setAttribute("aria-current", String(x === t)));
    }));
    const bar = $("#buybar");
    const inline = $("#add-inline");
    if (bar && inline) {
      new IntersectionObserver(([en]) => bar.classList.toggle("show", !en.isIntersecting && en.boundingClientRect.top < innerHeight)).observe(inline);
    }
  }

  /* Checkout */
  function deliveryFor(method, sub) {
    const d = DELIVERY[method];
    return sub >= FREE_OVER ? 0 : d.fee;
  }
  function renderCheckout() {
    const form = $("#checkout-form");
    if (!form) return;
    const hasItems = bag.length > 0;
    $("#checkout-empty").hidden = hasItems || !$("#checkout-done").hidden;
    $("#checkout-main").hidden = !hasItems;
    if (!hasItems) return;
    const method = form.elements.delivery.value;
    const sub = subtotal();
    const fee = deliveryFor(method, sub);
    $("#sum-lines").innerHTML = bag.map((l, i) => lineHTML(l, i, true)).join("");
    $("#sum-sub").textContent = money(sub);
    $("#sum-del").textContent = fee === 0 ? "Free" : money(fee);
    $("#sum-total").textContent = money(sub + fee);
    $("#fee-courier").textContent = sub >= FREE_OVER ? "Free" : money(DELIVERY.courier.fee);
    $("#fee-postnet").textContent = sub >= FREE_OVER ? "Free" : money(DELIVERY.postnet.fee);
    $("#addr-courier").hidden = method !== "courier";
    $("#addr-postnet").hidden = method !== "postnet";
  }
  function buildMessage(f, ref) {
    const sub = subtotal();
    const method = f.delivery.value;
    const fee = deliveryFor(method, sub);
    const v = (n) => (f[n] ? f[n].value.trim() : "");
    const out = [];
    out.push("*New order: Blush and Blue*", `Order ref: ${ref}`, "");
    out.push("*Customer*", v("name"), v("phone"));
    if (v("email")) out.push(v("email"));
    out.push("", "*Items*");
    bag.forEach((l, i) => {
      const p = bySlug[l.slug];
      out.push(`${i + 1}. ${p.name}`);
      const bits = [l.colour];
      if (l.size !== "One size") bits.push("Size " + l.size);
      out.push(`   ${bits.join(", ")}`);
      out.push(`   ${l.qty} x ${money(p.price)} = ${money(p.price * l.qty)}`);
    });
    out.push("", "*Delivery*", DELIVERY[method].label);
    if (method === "courier") {
      out.push([v("street"), v("suburb")].filter(Boolean).join(", "), [v("city"), v("province"), v("postcode")].filter(Boolean).join(", "));
    } else {
      out.push(`PostNet branch: ${v("branch")}`);
    }
    if (v("notes")) out.push("", "*Notes*", v("notes"));
    out.push("", `Subtotal: ${money(sub)}`, `Delivery: ${fee === 0 ? "Free" : money(fee)}`, `*Total: ${money(sub + fee)}*`, "");
    out.push("Please confirm stock and send me the invoice. Thank you.");
    return out.join("\n");
  }
  function setErr(input, msg) {
    const err = input.parentElement.querySelector(".err");
    if (err) err.textContent = msg;
    input.setAttribute("aria-invalid", msg ? "true" : "false");
  }
  function validate(form) {
    const method = form.elements.delivery.value;
    const need = ["name", "phone"].concat(method === "courier" ? ["street", "city", "province", "postcode"] : ["branch"]);
    const LABEL = { name: "your full name", phone: "your WhatsApp number", street: "your street address", city: "your town or city", province: "your province", postcode: "your postal code", branch: "your nearest PostNet branch" };
    let first = null;
    ["name", "phone", "street", "city", "province", "postcode", "branch"].forEach((n) => {
      const el = form.elements[n];
      let msg = need.includes(n) && !el.value.trim() ? `Enter ${LABEL[n]}.` : "";
      if (!msg && n === "phone" && el.value.replace(/\D/g, "").length < 9) msg = "Enter a full cellphone number, for example 082 123 4567.";
      setErr(el, msg);
      if (msg && !first) first = el;
    });
    if (first) first.focus();
    return !first;
  }
  const form = $("#checkout-form");
  if (form) {
    renderCheckout();
    form.addEventListener("change", (e) => {
      if (e.target.name === "delivery") renderCheckout();
    });
    form.addEventListener("input", (e) => { if (e.target.getAttribute("aria-invalid") === "true") setErr(e.target, ""); });
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!bag.length || !validate(form)) return;
      const d = new Date();
      const pad = (n) => String(n).padStart(2, "0");
      const ref = `BB-${String(d.getFullYear()).slice(2)}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${String(Date.now()).slice(-4)}`;
      const url = `https://wa.me/${WA}?text=${encodeURIComponent(buildMessage(form.elements, ref))}`;
      $("#done-ref").textContent = ref;
      $("#done-open").href = url;
      window.open(url, "_blank", "noopener");
      bag = [];
      saveBag();
      $("#checkout-main").hidden = true;
      $("#checkout-empty").hidden = true;
      $("#checkout-done").hidden = false;
      $("#checkout-title").textContent = "Press send in WhatsApp";
      scrollTo({ top: 0, behavior: reduced() ? "auto" : "smooth" });
    });
  }

  renderBag();
})();
