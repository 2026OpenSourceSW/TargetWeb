async function currentUser() {
  const response = await fetch("/api/me");
  const data = await response.json();
  return data.user;
}

function setAuthNavigation(user) {
  const adminLink = document.querySelector("#adminLink");
  const loginLink = document.querySelector("#loginLink");
  const signupLink = document.querySelector("#signupLink");
  const logoutBtn = document.querySelector("#logoutBtn");

  if (adminLink) adminLink.classList.toggle("hidden", !user || user.role !== "admin");
  if (loginLink) loginLink.classList.toggle("hidden", Boolean(user));
  if (signupLink) signupLink.classList.toggle("hidden", Boolean(user));
  if (logoutBtn) logoutBtn.classList.toggle("hidden", !user);
}

async function logout() {
  await fetch("/api/logout", { method: "POST" });
  window.location.href = "/";
}

async function initializeAuth() {
  const user = await currentUser();
  window.marketNestUser = user;
  setAuthNavigation(user);
  document.dispatchEvent(new CustomEvent("marketnest:session", { detail: { user } }));

  const logoutBtn = document.querySelector("#logoutBtn");
  if (logoutBtn) logoutBtn.addEventListener("click", logout);

  return user;
}

window.marketNestAuthReady = initializeAuth();
