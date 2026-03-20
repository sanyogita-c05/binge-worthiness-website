// LOAD NAVBAR
fetch("components/navbar.html")
  .then(response => response.text())
  .then(data => {
    document.getElementById("navbar").innerHTML = data;

    // AFTER navbar loads → apply scroll effect
    handleNavbarScroll();
  });

// NAVBAR SCROLL EFFECT
function handleNavbarScroll() {
  window.addEventListener("scroll", function () {
    const nav = document.querySelector(".navbar");

    if (!nav) return;

    if (window.scrollY > 50) {
      nav.style.background = "rgba(0, 0, 0, 0.9)";
    } else {
      nav.style.background = "transparent";
    }
  });
}