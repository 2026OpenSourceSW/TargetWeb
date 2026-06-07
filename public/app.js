const money = new Intl.NumberFormat("ko-KR", {
  style: "currency",
  currency: "KRW",
  maximumFractionDigits: 0
});

const state = {
  products: [],
  cart: [],
  user: null
};

const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json"
    },
    ...options
  });
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

function print(target, value) {
  $(target).textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

function updateSessionUi(user) {
  state.user = user;
  const sessionState = $("#sessionState");
  const orderUserId = $("#orderUserId");

  if (sessionState) {
    sessionState.textContent = user ? `${user.name}님, 좋은 쇼핑 되세요.` : "";
  }

  if (orderUserId && user) {
    orderUserId.value = user.id;
  }
}

function renderProducts(products) {
  $("#productGrid").innerHTML = products
    .map((product) => {
      return `
        <article class="product-card">
          <img src="${product.image}" alt="${product.name}">
          <div class="product-body">
            <div>
              <h3>${product.name}</h3>
              <p class="muted">${product.description}</p>
            </div>
            <div class="price">${money.format(product.price)}</div>
            <button data-add="${product.id}">담기</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderCart() {
  const total = state.cart.reduce((sum, product) => sum + product.price, 0);
  $("#clientTotal").value = total;
  $("#cartItems").innerHTML =
    state.cart
      .map((product) => {
        return `<div class="cart-row"><strong>${product.name}</strong><span>${money.format(product.price)}</span></div>`;
      })
      .join("") || `<p class="muted">장바구니가 비어 있습니다.</p>`;
}

async function loadProducts() {
  const data = await api("/api/products");
  state.products = data.products;
  renderProducts(state.products);
  await runSearch();
}

async function runSearch() {
  const q = encodeURIComponent($("#searchInput").value);
  const data = await api(`/api/search?q=${q}`);
  renderProducts(data.results || []);
}

async function loadReviews(productId = 101) {
  const data = await api(`/api/reviews?productId=${productId}`);
  $("#reviewList").innerHTML =
    data.reviews
      .map((review) => `<div class="review"><strong>${review.author}</strong><p>${review.body}</p></div>`)
      .join("") || `<p class="muted">등록된 리뷰가 없습니다.</p>`;
}

$("#searchBtn").addEventListener("click", runSearch);

$("#productGrid").addEventListener("click", (event) => {
  const productId = Number(event.target.dataset.add);
  if (!productId) return;
  const product = state.products.find((candidate) => candidate.id === productId);
  if (product) {
    state.cart.push(product);
    renderCart();
  }
});

$("#checkoutForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = await api("/api/checkout", {
    method: "POST",
    body: JSON.stringify({
      clientTotal: Number($("#clientTotal").value),
      discountPercent: Number($("#discountPercent").value),
      items: state.cart.map((product) => product.name)
    })
  });
  print("#checkoutResult", data);
});

$("#loadOrdersBtn").addEventListener("click", async () => {
  const userId = Number($("#orderUserId").value);
  print("#ordersResult", await api(`/api/orders?userId=${userId}`));
});

$("#reviewForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const productId = Number($("#reviewProductId").value);
  await api("/api/reviews", {
    method: "POST",
    body: JSON.stringify({
      productId,
      author: $("#reviewAuthor").value,
      body: $("#reviewBody").value
    })
  });
  await loadReviews(productId);
});

document.addEventListener("marketnest:session", (event) => {
  updateSessionUi(event.detail.user);
});

if (window.marketNestAuthReady) {
  window.marketNestAuthReady.then(updateSessionUi);
}

loadProducts();
renderCart();
loadReviews();
