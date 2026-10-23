document.addEventListener("DOMContentLoaded", function () {
  const textarea = document.getElementById("prompt");
  const counter = document.getElementById("char-count");
  const form = document.getElementById("scan-form");
  const scanButton = document.getElementById("scan-button");
  const clearButton = document.getElementById("clear-prompt");

  if (textarea && counter) {
    const updateCount = () => {
      counter.textContent = textarea.value.length.toLocaleString() + " / 10,000";
      counter.classList.toggle("counter-near-limit", textarea.value.length >= 9000);
    };
    textarea.addEventListener("input", updateCount);
    updateCount();

    document.querySelectorAll("[data-sample]").forEach((button) => {
      button.addEventListener("click", () => {
        textarea.value = button.getAttribute("data-sample") || "";
        updateCount();
        textarea.focus();
      });
    });

    if (clearButton) {
      clearButton.addEventListener("click", () => {
        textarea.value = "";
        updateCount();
        textarea.focus();
      });
    }
  }

  if (form && scanButton) {
    form.addEventListener("submit", (event) => {
      if (!textarea || !textarea.value.trim()) {
        event.preventDefault();
        if (textarea) textarea.focus();
        return;
      }
      scanButton.disabled = true;
      scanButton.setAttribute("aria-busy", "true");
      scanButton.innerHTML = '<span aria-hidden="true">◌</span> Analyzing locally…';
    });
  }
});
