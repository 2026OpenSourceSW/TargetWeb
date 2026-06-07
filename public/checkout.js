const checkoutMoney = new Intl.NumberFormat("ko-KR", {
  style: "currency",
  currency: "KRW",
  maximumFractionDigits: 0
});
const checkoutCart = JSON.parse(localStorage.getItem("marketnestCart") || "[]");

function renderCheckout() {
  const total = checkoutCart.reduce((sum, product) => sum + product.price, 0);
  document.querySelector("#checkoutTotal").value = total;
  document.querySelector("#checkoutItems").innerHTML =
    checkoutCart.map((product) => `<div class="cart-row"><strong>${product.name}</strong><span>${checkoutMoney.format(product.price)}</span></div>`).join("") ||
    `<p class="muted">장바구니가 비어 있습니다.</p>`;
}

document.querySelector("#checkoutPageForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const response = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      clientTotal: Number(document.querySelector("#checkoutTotal").value),
      discountPercent: Number(document.querySelector("#checkoutDiscount").value),
      items: checkoutCart.map((product) => product.name)
    })
  });
  const data = await response.json();
  localStorage.setItem("marketnestLastOrder", JSON.stringify(data.order));
  localStorage.removeItem("marketnestCart");
  window.location.href = `/confirmation.html?orderId=${data.order.id}`;
});

renderCheckout();
