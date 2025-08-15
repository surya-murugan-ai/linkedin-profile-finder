document.addEventListener("DOMContentLoaded", function() {
    const searchForm = document.getElementById("searchForm");
    const searchBtn = document.getElementById("searchBtn");
    const resultsContainer = document.getElementById("results");
    const resultsList = document.getElementById("resultsList");
    const status = document.getElementById("status");
    const exportJsonBtn = document.getElementById("exportJson");
    const exportCsvBtn = document.getElementById("exportCsv");
    
    let searchResults = [];
    
    // Load saved form data
    loadFormData();
    
    searchForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        
        const formData = new FormData(searchForm);
        const searchData = {
            name: formData.get("name"),
            title: formData.get("title"),
            company: formData.get("company"),
            location: formData.get("location"),
            maxResults: parseInt(formData.get("maxResults"))
        };
        
        // Save form data
        saveFormData(searchData);
        
        // Show loading state
        setLoading(true);
        showStatus(" Searching for LinkedIn profiles...", "info");
        
        try {
            // Send message to background script
            const response = await chrome.runtime.sendMessage({
                action: "searchLinkedInProfiles",
                data: searchData
            });
            
            if (response.success) {
                searchResults = response.results;
                displayResults(searchResults);
                showStatus(` Found ${searchResults.length} profiles!`, "success");
            } else {
                showStatus(` ${response.error}`, "error");
            }
        } catch (error) {
            showStatus(` Error: ${error.message}`, "error");
        } finally {
            setLoading(false);
        }
    });
    
    function displayResults(results) {
        if (results.length === 0) {
            resultsList.innerHTML = "<p class=\"no-results\">No LinkedIn profiles found. Try different search terms.</p>";
        } else {
            resultsList.innerHTML = results.map((result, index) => `
                <div class="result-item">
                    <div class="result-header">
                        <span class="result-number">#${index + 1}</span>
                        <span class="result-score score-${getScoreClass(result.score)}">${result.score.toFixed(1)}</span>
                    </div>
                    <div class="result-content">
                        <h4 class="result-title">
                            <a href="${result.url}" target="_blank" rel="noopener">${result.title || "LinkedIn Profile"}</a>
                        </h4>
                        <p class="result-snippet">${result.snippet || "No description available"}</p>
                        <div class="result-meta">
                            <span class="result-url">${result.url}</span>
                        </div>
                    </div>
                </div>
            `).join("");
        }
        
        resultsContainer.style.display = "block";
    }
    
    function getScoreClass(score) {
        if (score >= 8.0) return "excellent";
        if (score >= 5.0) return "good";
        if (score >= 2.0) return "fair";
        return "poor";
    }
    
    function setLoading(loading) {
        const btnText = searchBtn.querySelector(".btn-text");
        const btnLoading = searchBtn.querySelector(".btn-loading");
        
        if (loading) {
            btnText.style.display = "none";
            btnLoading.style.display = "inline";
            searchBtn.disabled = true;
        } else {
            btnText.style.display = "inline";
            btnLoading.style.display = "none";
            searchBtn.disabled = false;
        }
    }
    
    function showStatus(message, type) {
        status.textContent = message;
        status.className = `status status-${type}`;
        status.style.display = "block";
        
        if (type !== "error") {
            setTimeout(() => {
                status.style.display = "none";
            }, 5000);
        }
    }
    
    function saveFormData(data) {
        chrome.storage.local.set({ "formData": data });
    }
    
    function loadFormData() {
        chrome.storage.local.get(["formData"], function(result) {
            if (result.formData) {
                const data = result.formData;
                document.getElementById("name").value = data.name || "";
                document.getElementById("title").value = data.title || "";
                document.getElementById("company").value = data.company || "";
                document.getElementById("location").value = data.location || "";
                document.getElementById("maxResults").value = data.maxResults || 10;
            }
        });
    }
    
    // Export functionality
    exportJsonBtn.addEventListener("click", function() {
        if (searchResults.length > 0) {
            const dataStr = JSON.stringify(searchResults, null, 2);
            downloadFile(dataStr, "linkedin_profiles.json", "application/json");
        }
    });
    
    exportCsvBtn.addEventListener("click", function() {
        if (searchResults.length > 0) {
            const csvContent = convertToCSV(searchResults);
            downloadFile(csvContent, "linkedin_profiles.csv", "text/csv");
        }
    });
    
    function convertToCSV(data) {
        const headers = ["name", "title", "company", "location", "url", "result_title", "snippet", "score"];
        const csvRows = [headers.join(",")];
        
        for (const row of data) {
            const values = headers.map(header => {
                const value = row[header] || "";
                return `"${value.replace(/"/g, "\"\"")}"`;
            });
            csvRows.push(values.join(","));
        }
        
        return csvRows.join("\n");
    }
    
    function downloadFile(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
});
