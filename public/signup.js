const signupForm = document.querySelector("#signupForm");
const signupMessage = document.querySelector("#signupMessage");

signupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  signupMessage.textContent = "";

  const response = await fetch("/api/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: document.querySelector("#name").value,
      email: document.querySelector("#email").value,
      password: document.querySelector("#password").value
    })
  });

  const data = await response.json();
  if (!response.ok) {
    signupMessage.textContent = data.error || "가입에 실패했습니다.";
    return;
  }

  window.location.href = "/";
});
