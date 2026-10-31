// Business WhatsApp number: country code + number, digits only.
const WHATSAPP = "919607227768";

document.documentElement.classList.add("js");

const waLink = (text) =>
  `https://wa.me/${WHATSAPP}${text ? `?text=${encodeURIComponent(text)}` : ""}`;

// Keep every WhatsApp link in sync with the number above.
document.querySelectorAll("[data-wa]").forEach((a) => {
  const preset = new URL(a.href).searchParams.get("text");
  a.href = waLink(preset);
  a.target = "_blank";
  a.rel = "noopener";
});

// Header shadow + floating button
const header = document.querySelector(".site-header");
const float = document.querySelector(".wa-float");
const onScroll = () => {
  const y = window.scrollY;
  header.classList.toggle("scrolled", y > 8);
  float.classList.toggle("show", y > 600);
};
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

// Mobile nav
const toggle = document.querySelector(".nav-toggle");
const nav = document.getElementById("nav");
const setNav = (open) => {
  nav.classList.toggle("open", open);
  toggle.setAttribute("aria-expanded", String(open));
  toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
};
toggle.addEventListener("click", () => setNav(!nav.classList.contains("open")));
nav.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setNav(false)));
document.addEventListener("keydown", (e) => e.key === "Escape" && setNav(false));

// Reveal on scroll
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver(
    (entries) => entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    }),
    { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
  );
  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
} else {
  document.querySelectorAll(".reveal").forEach((el) => el.classList.add("in"));
}

// Booking form → WhatsApp (home page only)
const form = document.getElementById("booking-form");
if (form) {
  const dateInput = document.getElementById("f-date");
  const today = new Date();
  // Weekends only, booked at least 3 days ahead.
  const MIN_DAYS_AHEAD = 3;
  const isoLocal = (dt) => new Date(dt.getTime() - dt.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  const earliest = new Date(today.getFullYear(), today.getMonth(), today.getDate() + MIN_DAYS_AHEAD);
  dateInput.min = isoLocal(earliest);
  const MSG_MISSING = "Please fill in all the fields above (notes are optional).";
  const MSG_DATE = `Sessions are on Saturdays and Sundays only, booked at least ${MIN_DAYS_AHEAD} days ahead. Please pick another date.`;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const error = form.querySelector(".form-error");
    let ok = true;
    form.querySelectorAll("[required]").forEach((el) => {
      const bad = !el.value.trim();
      el.classList.toggle("invalid", bad);
      el.setAttribute("aria-invalid", String(bad));
      if (bad) ok = false;
    });
    error.textContent = MSG_MISSING;
    if (ok) {
      const picked = new Date(`${dateInput.value}T00:00`);
      const day = picked.getDay();
      if (picked < earliest || (day !== 0 && day !== 6)) {
        ok = false;
        dateInput.classList.add("invalid");
        dateInput.setAttribute("aria-invalid", "true");
        error.textContent = MSG_DATE;
      }
    }
    error.hidden = ok;
    if (!ok) { form.querySelector(".invalid").focus(); return; }

    const d = Object.fromEntries(new FormData(form));
    const date = new Date(`${d.date}T00:00`).toLocaleDateString("en-IN", {
      weekday: "short", day: "numeric", month: "short",
    });
    const lines = [
      `Hi Sid, I'd like to book a session.`,
      ``,
      `Name: ${d.name.trim()}`,
      `Gender: ${d.gender}`,
      `Area: ${d.area}`,
      `Style: ${d.treatment}`,
      `When: ${date}, ${d.time}`,
    ];
    if (d.notes.trim()) lines.push(`Notes: ${d.notes.trim()}`);
    lines.push(``, `I understand a ₹500 advance confirms the booking.`);
    window.open(waLink(lines.join("\n")), "_blank", "noopener");
  });

  form.addEventListener("input", (e) => {
    if (e.target.classList.contains("invalid") && e.target.value.trim()) {
      e.target.classList.remove("invalid");
      e.target.removeAttribute("aria-invalid");
    }
  });
}

document.getElementById("year").textContent = new Date().getFullYear();
