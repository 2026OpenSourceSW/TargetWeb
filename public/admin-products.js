async function loadAdminProducts() {
  const response = await fetch("/api/admin/products");
  const data = await response.json();
  document.querySelector("#adminProducts").innerHTML = `
    <table>
      <thead><tr><th>ID</th><th>상품</th><th>카테고리</th><th>가격</th></tr></thead>
      <tbody>
        ${data.products.map((product) => `
          <tr>
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>${product.category}</td>
            <td>${new Intl.NumberFormat("ko-KR").format(product.price)}원</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

loadAdminProducts();
