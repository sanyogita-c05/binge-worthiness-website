const faqItems = document.querySelectorAll(".faq-item");

faqItems.forEach(item => {
    item.querySelector(".faq-question").addEventListener("click", () => {

        // close others
        faqItems.forEach(i => {
            if(i !== item) {
                i.classList.remove("active");
                i.querySelector(".icon").textContent = "+";
            }
        });

        // toggle current
        item.classList.toggle("active");

        const icon = item.querySelector(".icon");
        icon.textContent = item.classList.contains("active") ? "✖" : "+";
    });
});