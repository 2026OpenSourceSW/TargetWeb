document.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;

  const label = button.textContent.replace(/\s+/g, " ").trim().toLowerCase();
  if (label.includes("shopping_cart") || label.includes("cart") || label.includes("add_shopping_cart")) {
    window.location.href = "/cart";
  }
  if (label.includes("account_circle") || label.includes("person")) {
    window.location.href = "/account";
  }
});
