function renderHistory(orders) {
  document.querySelector("#orderHistory").innerHTML = `
    <table>
      <thead><tr><th>주문번호</th><th>상품</th><th>상태</th><th>금액</th><th></th></tr></thead>
      <tbody>
        ${orders.map((order) => `
          <tr>
            <td>${order.id}</td>
            <td>${order.items.join(", ")}</td>
            <td>${order.status}</td>
            <td>${new Intl.NumberFormat("ko-KR").format(order.total)}원</td>
            <td><a class="secondary-mini" href="/order-detail.html?orderId=${order.id}">상세</a></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function loadHistory() {
  const userId = document.querySelector("#historyUserId").value || 1;
  const response = await fetch(`/api/orders?userId=${encodeURIComponent(userId)}`);
  const data = await response.json();
  renderHistory(data.orders || []);
}

document.addEventListener("marketnest:session", (event) => {
  if (event.detail.user) document.querySelector("#historyUserId").value = event.detail.user.id;
});
document.querySelector("#historyLoadBtn").addEventListener("click", loadHistory);
loadHistory();
