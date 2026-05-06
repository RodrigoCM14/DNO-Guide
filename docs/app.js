const sections = window.GUIDE_SECTIONS || [];
const input = document.querySelector("#searchInput");
const results = document.querySelector("#searchResults");
const resultCount = document.querySelector("#resultCount");
const clearSearch = document.querySelector("#clearSearch");
const guideSections = [...document.querySelectorAll(".guide-section")];
const tocLinks = [...document.querySelectorAll(".toc a")];
const backToTop = document.querySelector("#backToTop");

const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

function snippet(text, query) {
  const lower = text.toLowerCase();
  const index = lower.indexOf(query.toLowerCase());
  const start = Math.max(0, index - 58);
  const end = Math.min(text.length, index + query.length + 110);
  const raw = (index === -1 ? text.slice(0, 160) : text.slice(start, end)).trim();
  const escaped = raw.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
  return query ? escaped.replace(new RegExp(escapeRegExp(query), "ig"), "<mark>$&</mark>") : escaped;
}

function applySearch() {
  const query = input.value.trim();
  const normalized = query.toLowerCase();

  if (!query) {
    guideSections.forEach((section) => section.classList.remove("hidden-by-search"));
    results.innerHTML = "";
    resultCount.textContent = "Ready";
    return;
  }

  const matches = sections.filter((section) => {
    const haystack = `${section.title} ${section.text}`.toLowerCase();
    return haystack.includes(normalized);
  });
  const ids = new Set(matches.map((match) => match.id));
  guideSections.forEach((section) => {
    section.classList.toggle("hidden-by-search", !ids.has(section.id));
  });

  resultCount.textContent = `${matches.length} result${matches.length === 1 ? "" : "s"}`;
  results.innerHTML = matches.slice(0, 18).map((match) => `
    <a href="#${match.id}">
      <strong>${match.title}</strong>
      <small>${snippet(match.text, query)}</small>
    </a>
  `).join("");
}

input.addEventListener("input", applySearch);
clearSearch.addEventListener("click", () => {
  input.value = "";
  applySearch();
  input.focus();
});

const checklistKey = "dno-guide-checklist";
let checklistState = {};
try {
  checklistState = JSON.parse(localStorage.getItem(checklistKey) || "{}");
} catch {
  checklistState = {};
}

document.querySelectorAll(".check-item input[type='checkbox']").forEach((checkbox) => {
  const id = checkbox.dataset.checkId;
  checkbox.checked = Boolean(checklistState[id]);
  checkbox.addEventListener("change", () => {
    checklistState[id] = checkbox.checked;
    localStorage.setItem(checklistKey, JSON.stringify(checklistState));
  });
});

document.querySelectorAll(".anchor-link").forEach((link) => {
  link.addEventListener("click", async () => {
    const url = `${location.origin}${location.pathname}${link.getAttribute("href")}`;
    if (navigator.clipboard && location.protocol !== "file:") {
      await navigator.clipboard.writeText(url);
    }
  });
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    tocLinks.forEach((link) => {
      link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`);
    });
  });
}, { rootMargin: "-20% 0px -70% 0px", threshold: 0.01 });

guideSections.forEach((section) => observer.observe(section));

window.addEventListener("scroll", () => {
  backToTop.classList.toggle("visible", window.scrollY > 700);
});

backToTop.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});
