document.addEventListener('DOMContentLoaded', function() {

    // --- INTERACTIVE ELEMENTS ---

    // Character search functionality
    const characterSearchInput = document.querySelector('.character-search');
    const searchIcon = document.querySelector('.search-icon');

    const performCharacterSearch = () => {
        const characterName = characterSearchInput.value.trim();
        if (characterName) {
            // In a real app, you might show a loading spinner here
            window.location.href = `/character_info/?character_name=${encodeURIComponent(characterName)}`;
        } else {
            characterSearchInput.focus();
        }
    };

    if (characterSearchInput) {
        characterSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                performCharacterSearch();
            }
        });
    }

    if (searchIcon) {
        searchIcon.addEventListener('click', performCharacterSearch);
    }

    // Main chat input click redirects to chatbot page
    const chatInputContainer = document.querySelector('.chat-input-container');
    if (chatInputContainer) {
        chatInputContainer.addEventListener('click', () => {
            // The CSS handles the click animation, JS handles the redirect
            window.location.href = '/chatbot/';
        });
    }

    // Suggested questions click redirects to chatbot page with the question
    const questionBubbles = document.querySelectorAll('.question-bubble');
    questionBubbles.forEach(bubble => {
        bubble.addEventListener('click', function() {
            const questionText = this.innerText.trim();
            if (questionText) {
                window.location.href = `/chatbot/?q=${encodeURIComponent(questionText)}`;
            }
        });
    });


    // --- DYNAMIC CONTENT & ANIMATIONS ---

    // Smooth scroll for anchor links (if any are added in the future)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Page load animations for a smoother entry
    const animateOnLoad = () => {
        const elementsToAnimate = [
            '.main-headline',
            '.main-center',
            '.main-chat-section',
            '.suggested-questions',
            '.content-grid'
        ];

        elementsToAnimate.forEach((selector, index) => {
            const element = document.querySelector(selector);
            if (element) {
                element.style.opacity = '0';
                element.style.transform = 'translateY(20px)';
                element.style.transition = `opacity 0.5s ease-out ${index * 0.1}s, transform 0.5s ease-out ${index * 0.1}s`;
                
                setTimeout(() => {
                    element.style.opacity = '1';
                    element.style.transform = 'translateY(0)';
                }, 100); // Small delay to ensure styles are applied before transition starts
            }
        });
    };

    animateOnLoad();


    // --- KEYBOARD & ACCESSIBILITY ---

    // Keyboard shortcut: Ctrl + K to focus on search
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            if (characterSearchInput) {
                characterSearchInput.focus();
            }
        }
    });

    // Make interactive elements focusable and clickable with keyboard
    const improveAccessibility = () => {
        const interactiveSelectors = [
            '.question-bubble',
            '.event-banner',
            '.cash-banner',
            '.ranking-item',
            '.maple-logo',
            '.user-status .status-text'
        ];
        
        document.querySelectorAll(interactiveSelectors.join(', ')).forEach(element => {
            if (element.tagName !== 'A' && element.tagName !== 'BUTTON' && element.tagName !== 'INPUT') {
                element.setAttribute('role', 'button');
                element.setAttribute('tabindex', '0');
                
                element.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.click();
                    }
                });
            }
        });
    };

    improveAccessibility();

    console.log('MAI Main Page UI Initialized 🍁');
});
