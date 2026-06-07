const loginForm = document.querySelector("#loginForm");
const loginMessage = document.querySelector("#loginMessage");

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginMessage.textContent = "";

  const response = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: document.querySelector("#email").value,
      password: document.querySelector("#password").value
    })
  });

  const data = await response.json();
  if (!response.ok) {
    loginMessage.textContent = data.error || "로그인에 실패했습니다.";
    return;
  }

  window.location.href = data.user.role === "admin" ? "/admin.html" : "/";
});
