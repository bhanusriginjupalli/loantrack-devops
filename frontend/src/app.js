const loanForm = document.getElementById("loan-form");
const loanList = document.getElementById("loan-list");
const message = document.getElementById("message");

async function loadLoans() {
    try {
        const response = await fetch("/api/loans");

        if (!response.ok) {
            throw new Error(`Failed to load loans: ${response.status}`);
        }

        const loans = await response.json();

        loanList.innerHTML = "";

        for (const loan of loans) {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${loan.id}</td>
                <td>${loan.borrower_name}</td>
                <td>${Number(loan.loan_amount).toFixed(2)}</td>
                <td>${loan.property_city ?? ""}</td>
                <td>${loan.status}</td>
                <td>${new Date(loan.created_at).toLocaleString()}</td>
            `;

            loanList.appendChild(row);
        }
    } catch (error) {
        message.textContent = error.message;
    }
}

loanForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
        borrower_name: document.getElementById("borrower-name").value,
        loan_amount: Number(document.getElementById("loan-amount").value),
        property_city: document.getElementById("property-city").value || null,
        status: document.getElementById("status").value,
    };

    try {
        const response = await fetch("/api/loans", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Failed to create loan");
        }

        loanForm.reset();
        message.textContent = "Loan added successfully.";

        await loadLoans();
    } catch (error) {
        message.textContent = error.message;
    }
});

loadLoans();