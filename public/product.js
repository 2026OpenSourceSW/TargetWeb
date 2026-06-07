const productId = new URLSearchParams(window.location.search).get("id") || "101";
const productMoney = new Intl.NumberFormat("ko-KR", {
  style: "currency",
  currency: "KRW",
  maximumFractionDigits: 0
});

async function productApi(path) {
  const response = await fetch(path);
  return response.json();
}

function saveCartItem(product) {
  const cart = JSON.parse(localStorage.getItem("marketnestCart") || "[]");
  cart.push(product);
  localStorage.setItem("marketnestCart", JSON.stringify(cart));
}

async function loadProductDetail() {
  const data = await productApi(`/api/product?id=${encodeURIComponent(productId)}`);
  const product = data.product;
  document.title = `${product.name} | MarketNest`;
  document.querySelector("#productDetail").innerHTML = `
    <div class="detail-media">
      <img src="${product.image}" alt="${product.name}">
    </div>
    <div class="detail-copy">
      <p class="eyebrow">${product.category}</p>
      <h1>${product.name}</h1>
      <p class="muted">${product.description}</p>
      <div class="detail-price">${productMoney.format(product.price)}</div>
      <div class="hero-actions">
        <button id="addDetailCart">장바구니 담기</button>
        <a class="secondary-action" href="/checkout.html">체크아웃으로 이동</a>
      </div>
    </div>
  `;
  document.querySelector("#addDetailCart").addEventListener("click", () => saveCartItem(product));

  const reviews = await productApi(`/api/reviews?productId=${encodeURIComponent(productId)}`);
  document.querySelector("#detailReviews").innerHTML =
    reviews.reviews.map((review) => `<div class="review"><strong>${review.author}</strong><p>${review.body}</p></div>`).join("") ||
    `<p class="muted">등록된 리뷰가 없습니다.</p>`;
}

loadProductDetail();
