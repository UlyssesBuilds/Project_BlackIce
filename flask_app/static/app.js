# api/static/app.js
// You can add similar listeners for "Place Bet" and "My Dashboard" actions
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
        localStorage.setItem("token", data.access_token);  // Save token
        alert("Login successful!");
        document.getElementById("login-section").style.display = "none";
        document.getElementById("markets-section").style.display = "block";
        fetchMarkets();
    } else {
        alert("Login failed: " + data.error);
    }
}

async function fetchMarkets() {
    const token = localStorage.getItem("token");

    const response = await fetch("/api/market/markets", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await response.json();

    if (response.ok) {
        const marketsList = document.getElementById("markets-list");
        marketsList.innerHTML = "";
        data.markets.forEach(market => {
            let listItem = document.createElement("li");
            listItem.textContent = market.name + " - " + market.odds;
            marketsList.appendChild(listItem);
        });
    } else {
        alert("Failed to load markets.");
    }
}


document.getElementById("view-markets").addEventListener("click", function(e) {
    e.preventDefault();
    fetch("/api/markets/markets")
        .then(response => response.json())
        .then(data => {
            let content = "<h2>Available Markets</h2><ul>";
            data.forEach(market => {
                content += `<li><strong>${market.name}</strong>: ${market.description} - Status: ${market.is_resolved ? "Closed" : "Open"}</li>`;
            });
            content += "</ul>";
            document.getElementById("content").innerHTML = content;
        })
        .catch(error => console.error("Error fetching markets:", error));
});