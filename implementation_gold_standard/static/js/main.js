document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("searchForm");
    const airportCodeInput = document.getElementById("airportCode");
    const messageArea = document.getElementById("message");
    const resultsContainer = document.getElementById("results-container");
    const resultsTableBody = document.querySelector("#resultsTable tbody");
  
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearResults();
      setMessage("");
      resultsContainer.hidden = true;
  
      const airportCode = airportCodeInput.value.trim().toUpperCase();
  
      // Client-side validation
      if (!airportCode.match(/^[A-Za-z]{3}$/)) {
        setMessage("Please enter a valid 3-letter airport code (e.g., LAX).", "error");
        return;
      }
  
      setMessage("Loading results, please wait...", "info");
  
      try {
        const response = await fetch("/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ airport_code: airportCode }),
        });
  
        const data = await response.json();
  
        if (!response.ok) {
          // API returned an error
          setMessage(data.error || "Server error occurred.", "error");
          return;
        }
  
        // Handle empty results
        if (data.summary.length === 0) {
          setMessage("No arrivals found for this airport code.", "info");
          return;
        }
  
        // Populate the table
        data.summary.forEach(({ country, count }) => {
          const row = document.createElement("tr");
          const countryCell = document.createElement("td");
          const countCell = document.createElement("td");
  
          countryCell.textContent = country;
          countCell.textContent = count;
  
          row.appendChild(countryCell);
          row.appendChild(countCell);
          resultsTableBody.appendChild(row);
        });
  
        resultsContainer.hidden = false;
        setMessage("Arrivals summary loaded successfully.", "success");
  
      } catch (error) {
        // Network or unexpected error
        console.error(error);
        setMessage("Network error. Please try again later.", "error");
      }
    });
  
    function clearResults() {
      resultsTableBody.innerHTML = "";
    }
  
    function setMessage(msg, type = "info") {
      messageArea.textContent = msg;
      messageArea.className = "message-area " + (type === "error" ? "error" : type === "success" ? "success" : "");
      // Additional styling can be done in CSS if needed
    }
  });
  