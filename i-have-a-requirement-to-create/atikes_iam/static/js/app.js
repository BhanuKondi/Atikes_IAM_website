const navButton = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");

if (navButton && nav) {
  navButton.addEventListener("click", () => {
    nav.classList.toggle("open");
  });
}

const tagSelect = document.querySelector("[data-tag-select]");
const otherTagWrap = document.querySelector("[data-other-tag-wrap]");
const otherTag = document.querySelector("[data-other-tag]");

if (tagSelect && otherTagWrap && otherTag) {
  const syncOtherTag = () => {
    const isOther = tagSelect.value === "Other";
    otherTagWrap.classList.toggle("hidden", !isOther);
    otherTag.required = isOther;
    if (!isOther) {
      otherTag.value = "";
    }
  };
  tagSelect.addEventListener("change", syncOtherTag);
  syncOtherTag();
}

const profileToggle = document.querySelector("[data-profile-toggle]");
const profileMenu = document.querySelector("[data-profile-menu]");
if (profileToggle && profileMenu) {
  profileToggle.addEventListener("click", () => {
    profileMenu.classList.toggle("open");
  });
  document.addEventListener("click", (event) => {
    if (!profileToggle.contains(event.target) && !profileMenu.contains(event.target)) {
      profileMenu.classList.remove("open");
    }
  });
}

const carousel = document.querySelector("[data-carousel]");
if (carousel) {
  const slides = [...carousel.querySelectorAll("[data-slide]")];
  const previous = carousel.querySelector("[data-slide-prev]");
  const next = carousel.querySelector("[data-slide-next]");
  let activeIndex = 0;

  const showSlide = (index) => {
    if (!slides.length) return;
    activeIndex = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      slide.classList.toggle("active", slideIndex === activeIndex);
    });
  };

  previous?.addEventListener("click", (event) => {
    event.preventDefault();
    showSlide(activeIndex - 1);
  });

  next?.addEventListener("click", (event) => {
    event.preventDefault();
    showSlide(activeIndex + 1);
  });

  window.setInterval(() => showSlide(activeIndex + 1), 7000);
}

document.querySelectorAll("[data-format]").forEach((button) => {
  button.addEventListener("click", () => {
    const editor = document.querySelector("[data-rich-editor]");
    if (!editor) return;
    const tag = button.dataset.format === "bold" ? "**" : "_";
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selected = editor.value.slice(start, end) || "text";
    editor.value = `${editor.value.slice(0, start)}${tag}${selected}${tag}${editor.value.slice(end)}`;
    editor.focus();
    editor.selectionStart = start + tag.length;
    editor.selectionEnd = start + tag.length + selected.length;
  });
});
