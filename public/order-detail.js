const orderId = new URLSearchParams(window.location.search).get("orderId") || "9001";

async function loadOrderDetail() {
  const response = await fetch(`/api/order?orderId=${encodeURIComponent(orderId)}`);
  const data = await response.json();
  const order = data.order;
  document.querySelector("#orderTitle").textContent = `#${order.id}`;
  document.querySelector("#orderDetail").innerHTML = `
    <div class="panel-title"><span>배송 진행</span><strong>${order.status}</strong></div>
    <p><strong>회원번호:</strong> ${order.userId}</p>
    <p><strong>상품:</strong> ${order.items.join(", ")}</p>
    <p><strong>금액:</strong> ${new Intl.NumberFormat("ko-KR").format(order.total)}원</p>
  `;
}

loadOrderDetail();
