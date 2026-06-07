const lastOrder = JSON.parse(localStorage.getItem("marketnestLastOrder") || "null");
document.querySelector("#confirmationResult").textContent = lastOrder
  ? JSON.stringify(lastOrder, null, 2)
  : "최근 주문 정보가 없습니다.";
