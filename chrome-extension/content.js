// Content script for extracting LinkedIn profiles from Google search results
function extractLinkedInProfiles(searchData) {
    const results = [];
    
    // Method 1: Direct LinkedIn URL search
    const allLinks = document.querySelectorAll('a[href*="linkedin.com/in/"]');
    for (const link of allLinks) {
        try {
            const href = link.getAttribute('href');
            if (href && href.includes('linkedin.com/in/')) {
                // Extract clean URL
                let url = href;
                if (url.startsWith('/url?q=')) {
                    url = url.split('/url?q=')[1].split('&')[0];
                }
                url = decodeURIComponent(url);
                
                if (isLinkedInProfileUrl(url)) {
                    const title = extractTitleFromElement(link);
                    const snippet = extractSnippetFromElement(link);
                    
                    results.push({
                        url: url,
                        title: title,
                        snippet: snippet
                    });
                }
            }
        } catch (e) {
            continue;
        }
    }
    
    // Method 2: Search through all result containers
    const resultContainers = document.querySelectorAll('div[data-sokoban-container], div.g, div[jscontroller]');
    for (const container of resultContainers) {
        try {
            const links = container.querySelectorAll('a[href*="linkedin.com/in/"]');
            for (const link of links) {
                const href = link.getAttribute('href');
                if (href && href.includes('linkedin.com/in/')) {
                    let url = href;
                    if (url.startsWith('/url?q=')) {
                        url = url.split('/url?q=')[1].split('&')[0];
                    }
                    url = decodeURIComponent(url);
                    
                    if (isLinkedInProfileUrl(url)) {
                        const title = extractTitleFromElement(link);
                        const snippet = extractSnippetFromElement(link);
                        
                        results.push({
                            url: url,
                            title: title,
                            snippet: snippet
                        });
                    }
                }
            }
        } catch (e) {
            continue;
        }
    }
    
    return results;
}

function isLinkedInProfileUrl(url) {
    return /^https?:\/\/([a-z]+\.)?linkedin\.com\/in\/[^\/?#]+\/?$/i.test(url);
}

function extractTitleFromElement(element) {
    try {
        // Look for title in the link itself
        if (element.textContent.trim()) {
            return element.textContent.trim();
        }
        
        // Look for title in parent elements
        const titleElement = element.closest('div').querySelector('h3, .title, [role="heading"]');
        if (titleElement) {
            return titleElement.textContent.trim();
        }
        
        return null;
    } catch (e) {
        return null;
    }
}

function extractSnippetFromElement(element) {
    try {
        const container = element.closest('div');
        const snippetElement = container.querySelector('[data-snf="nke7rc"], .VwiC3b, .snippet, [class*="VwiC3b"]');
        if (snippetElement) {
            return snippetElement.textContent.trim();
        }
        return null;
    } catch (e) {
        return null;
    }
}
