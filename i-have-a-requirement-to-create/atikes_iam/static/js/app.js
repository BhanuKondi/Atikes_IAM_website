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
