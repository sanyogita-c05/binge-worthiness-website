document.addEventListener("DOMContentLoaded", function () {

    const faqItems = document.querySelectorAll(".faq-item");

    faqItems.forEach(item => {
        const question = item.querySelector(".faq-question");

        if (!question) return;

        question.addEventListener("click", () => {

            // Close other items
            faqItems.forEach(i => {
                if (i !== item) {
                    i.classList.remove("active");

                    const otherIcon = i.querySelector(".icon");
                    if (otherIcon) otherIcon.textContent = "+";
                }
            });

            // Toggle current item
            item.classList.toggle("active");

            const icon = item.querySelector(".icon");
            if (icon) {
                icon.textContent = item.classList.contains("active") ? "✖" : "+";
            }
        });
    });

});