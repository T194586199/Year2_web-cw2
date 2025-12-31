// Search functionality

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchSuggestions = document.getElementById('search-suggestions');
    
    if (!searchInput || !searchSuggestions) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        
        // Clear previous timer
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            searchSuggestions.classList.remove('show');
            return;
        }
        
        // Delay 300ms before sending request
        searchTimeout = setTimeout(() => {
            fetch(`/api/search/suggest?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    showSuggestions(data.suggestions);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }, 300);
    });
    
    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
            searchSuggestions.classList.remove('show');
        }
    });
    
    // Keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        const items = searchSuggestions.querySelectorAll('.suggestion-item');
        const currentFocus = searchSuggestions.querySelector('.suggestion-item:focus');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (currentFocus) {
                const next = currentFocus.nextElementSibling;
                if (next) {
                    currentFocus.blur();
                    next.focus();
                }
            } else if (items.length > 0) {
                items[0].focus();
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (currentFocus) {
                const prev = currentFocus.previousElementSibling;
                if (prev) {
                    currentFocus.blur();
                    prev.focus();
                } else {
                    currentFocus.blur();
                    searchInput.focus();
                }
            }
        } else if (e.key === 'Enter' && currentFocus) {
            e.preventDefault();
            currentFocus.click();
        } else if (e.key === 'Escape') {
            searchSuggestions.classList.remove('show');
            searchInput.focus();
        }
    });
});

function showSuggestions(suggestions) {
    const searchSuggestions = document.getElementById('search-suggestions');
    if (!searchSuggestions) return;
    
    if (suggestions.length === 0) {
        searchSuggestions.classList.remove('show');
        return;
    }
    
    searchSuggestions.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('a');
        item.href = suggestion.url;
        item.className = 'suggestion-item';
        item.setAttribute('role', 'option');
        item.tabIndex = 0;
        
        const type = document.createElement('span');
        type.className = 'suggestion-type';
        type.textContent = suggestion.type === 'tag' ? 'Tag' : 'Post';
        
        const text = document.createElement('span');
        text.className = 'suggestion-text';
        text.textContent = suggestion.text;
        
        item.appendChild(type);
        item.appendChild(text);
        searchSuggestions.appendChild(item);
    });
    
    searchSuggestions.classList.add('show');
}


