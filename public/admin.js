const adminOrders = document.querySelector("#adminOrders");
const adminGuard = document.querySelector("#adminGuard");
const adminGreeting = document.querySelector("#adminGreeting");
const refreshOrdersBtn = document.querySelector("#refreshOrdersBtn");

function formatMoney(value) {
  return new Intl.NumberFormat("ko-KR", {
    style: "currency",
    currency: "KRW",
    maximumFractionDigits: 0
  }).format(value);
}

function renderOrders(orders) {
  adminOrders.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>주문번호</th>
          <th>회원번호</th>
          <th>상품</th>
          <th>상태</th>
          <th>금액</th>
        </tr>
      </thead>
      <tbody>
        ${orders
          .map((order) => {
            return `
              <tr>
                <td>${order.id}</td>
                <td>${order.userId}</td>
                <td>${order.items.join(", ")}</td>
                <td>${order.status}</td>
                <td>${formatMoney(order.total)}</td>
              </tr>
            `;
          })
          .join("")}
      </tbody>
    </table>
  `;
}

async function loadAdminOrders() {
  const response = await fetch("/api/admin/orders");
  const data = await response.json();
  renderOrders(data.orders || []);
}

document.addEventListener("marketnest:session", async (event) => {
  await showAdminState(event.detail.user);
});

async function showAdminState(user) {
  const isAdmin = user && user.role === "admin";

  adminGuard.classList.toggle("hidden", isAdmin);
  adminOrders.classList.toggle("hidden", !isAdmin);
  refreshOrdersBtn.classList.toggle("hidden", !isAdmin);
  adminGreeting.textContent = isAdmin ? `${user.name}님, 전체 주문을 확인할 수 있습니다.` : "";

  if (isAdmin) await loadAdminOrders();
}

if (window.marketNestAuthReady) {
  window.marketNestAuthReady.then(showAdminState);
}

refreshOrdersBtn.addEventListener("click", loadAdminOrders);
