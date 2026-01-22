// Markdown编辑器

document.addEventListener('DOMContentLoaded', function() {
    const contentEditor = document.getElementById('content-editor');
    const markdownPreview = document.getElementById('markdown-preview');
    const toolbar = document.querySelector('.editor-toolbar');
    const tagInput = document.getElementById('tag-input');
    const tagsHidden = document.getElementById('tags-hidden');
    const selectedTags = document.getElementById('selected-tags');
    const tagSuggestions = document.getElementById('tag-suggestions');
    
    // Markdown editor toolbar
    if (toolbar && contentEditor) {
        toolbar.addEventListener('click', function(e) {
            if (e.target.classList.contains('toolbar-btn')) {
                e.preventDefault();
                const action = e.target.dataset.action;
                applyMarkdownAction(action, contentEditor);
            }
        });
        
        // 实时预览（可选）
        contentEditor.addEventListener('input', function() {
            // 可以在这里添加实时预览功能
            // 但为了性能，我们只在需要时显示预览
        });
    }
    
    // Tag selector
    if (tagInput && typeof allTags !== 'undefined' && allTags) {
        let selectedTagList = [];
        
        // Initialize selected tags (read from hidden field, as it may already have a value)
        if (tagsHidden && tagsHidden.value) {
            selectedTagList = tagsHidden.value.split(',').map(t => t.trim()).filter(t => t);
            renderSelectedTags();
        } else if (tagInput.value) {
            // If no hidden field value, read from visible input
            selectedTagList = tagInput.value.split(',').map(t => t.trim()).filter(t => t);
            renderSelectedTags();
            updateHiddenInput();
        }
        
        tagInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            
            if (query.length === 0) {
                tagSuggestions.classList.remove('show');
                return;
            }
            
            // Filter tags
            const filtered = allTags.filter(tag => 
                tag.toLowerCase().includes(query.toLowerCase()) && 
                !selectedTagList.includes(tag)
            ).slice(0, 10);
            
            showTagSuggestions(filtered);
        });
        
        tagInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const value = e.target.value.trim();
                if (value && selectedTagList.length < 5 && !selectedTagList.includes(value)) {
                    addTag(value);
                    e.target.value = '';
                    tagSuggestions.classList.remove('show');
                }
            } else if (e.key === 'Backspace' && e.target.value === '') {
                if (selectedTagList.length > 0) {
                    removeTag(selectedTagList[selectedTagList.length - 1]);
                }
            }
        });
        
        function addTag(tagName) {
            if (selectedTagList.length >= 5) {
                alert('Maximum 5 tags allowed');
                return;
            }
            
            if (!selectedTagList.includes(tagName)) {
                selectedTagList.push(tagName);
                renderSelectedTags();
                updateHiddenInput();
            }
        }
        
        function removeTag(tagName) {
            selectedTagList = selectedTagList.filter(t => t !== tagName);
            renderSelectedTags();
            updateHiddenInput();
        }
        
        function renderSelectedTags() {
            selectedTags.innerHTML = '';
            selectedTagList.forEach(tag => {
                const tagEl = document.createElement('span');
                tagEl.className = 'selected-tag';
                tagEl.innerHTML = `
                    ${tag}
                    <button type="button" class="tag-remove" aria-label="Remove tag ${tag}">×</button>
                `;
                tagEl.querySelector('.tag-remove').addEventListener('click', () => {
                    removeTag(tag);
                });
                selectedTags.appendChild(tagEl);
            });
        }
        
        function updateHiddenInput() {
            if (tagsHidden) {
                tagsHidden.value = selectedTagList.join(',');
            }
        }
        
        function showTagSuggestions(tags) {
            if (tags.length === 0) {
                tagSuggestions.classList.remove('show');
                return;
            }
            
            tagSuggestions.innerHTML = '';
            tags.forEach(tag => {
                const item = document.createElement('div');
                item.className = 'tag-suggestion-item';
                item.textContent = tag;
                item.addEventListener('click', () => {
                    addTag(tag);
                    tagInput.value = '';
                    tagSuggestions.classList.remove('show');
                });
                tagSuggestions.appendChild(item);
            });
            
            tagSuggestions.classList.add('show');
        }
        
        // Click outside to close suggestions
        document.addEventListener('click', function(e) {
            if (!tagInput.contains(e.target) && !tagSuggestions.contains(e.target)) {
                tagSuggestions.classList.remove('show');
            }
        });
        
        // Sync tag values before form submission
        const postForm = document.querySelector('.post-form');
        if (postForm) {
            postForm.addEventListener('submit', function(e) {
                updateHiddenInput();
                
                const inputValue = tagInput.value.trim();
                if (inputValue && !inputValue.includes(',')) {
                    // Single tag, if not added yet, add it
                    if (!selectedTagList.includes(inputValue) && selectedTagList.length < 5) {
                        addTag(inputValue);
                    }
                } else if (inputValue && inputValue.includes(',')) {
                    // Multiple tags separated by commas
                    const tags = inputValue.split(',').map(t => t.trim()).filter(t => t);
                    tags.forEach(tag => {
                        if (!selectedTagList.includes(tag) && selectedTagList.length < 5) {
                            addTag(tag);
                        }
                    });
                    tagInput.value = '';
                }
                
                updateHiddenInput();
            });
        }
    }
});

function applyMarkdownAction(action, textarea) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    let replacement = '';
    let cursorPos = start;
    
    switch(action) {
        case 'bold':
            if (selectedText) {
                replacement = `**${selectedText}**`;
                cursorPos = start + replacement.length;
            } else {
                replacement = '**bold text**';
                cursorPos = start + 2; // Place cursor before "bold text"
            }
            break;
        case 'italic':
            if (selectedText) {
                replacement = `*${selectedText}*`;
                cursorPos = start + replacement.length;
            } else {
                replacement = '*italic text*';
                cursorPos = start + 1; 
            }
            break;
        case 'link':
            if (selectedText) {
                replacement = `[${selectedText}](URL)`;
                cursorPos = start + replacement.length - 4; 
            } else {
                replacement = '[link text](URL)';
                cursorPos = start + 1; 
            }
            break;
    }
    
    textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
    textarea.focus();
    textarea.setSelectionRange(cursorPos, cursorPos);
}


