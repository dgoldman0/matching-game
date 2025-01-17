document.getElementById("language-pair-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const L1_language = document.getElementById("L1_language").value;
    const L2_language = document.getElementById("L2_language").value;
    const n = document.getElementById("n").value;
    const reading_level = document.getElementById("reading_level").value;

    try {
        const result = await fetchLanguagePairs(L1_language, L2_language, n, reading_level);
        if (result) initializeGame(result.pairs, L1_language, L2_language);
    } catch (err) {
        console.error("Error fetching language pairs:", err);
        displayError("Failed to load language pairs. Please try again.");
    }
});

/**
 * Fetch language pairs from the backend.
 */
async function fetchLanguagePairs(L1, L2, n, level) {
    const response = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ L1_language: L1, L2_language: L2, n, reading_level: level }),
    });

    if (!response.ok) {
        throw new Error("Error fetching language pairs");
    }

    return await response.json();
}

/**
 * Initialize the game board with buttons and timer.
 */
function initializeGame(pairs, L1_language, L2_language) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = ""; // Clear previous results

    const autoRefresh = document.getElementById("auto-refresh").checked; // Get auto-refresh setting

    // Shuffle words independently for L1 and L2
    const L1_words = pairs.map(pair => pair.L1);
    const L2_words = pairs.map(pair => pair.L2);
    const shuffledL1 = shuffleArray([...L1_words]);
    const shuffledL2 = shuffleArray([...L2_words]);

    const L1Buttons = createButtons(shuffledL1, "L1");
    const L2Buttons = createButtons(shuffledL2, "L2");

    resultsDiv.innerHTML = `
        <div class="columns">
            <div class="column">
                <h3>${L1_language}</h3>
                <div class="button-group">${L1Buttons}</div>
            </div>
            <div class="column">
                <h3>${L2_language}</h3>
                <div class="button-group">${L2Buttons}</div>
            </div>
        </div>
        <p id="status-message"></p>
        <p id="timer">Time: 0:00</p>
    `;

    let timerInterval = startTimer();


    attachButtonHandlers(pairs, () => {
        clearInterval(timerInterval); // Stop timer
        displaySuccess(`All pairs matched in ${formatTime(secondsElapsed)}.`);

        // Auto-refresh logic
        if (autoRefresh) {
            setTimeout(() => {
                document.getElementById("language-pair-form").dispatchEvent(new Event("submit"));
            }, 1000); // Delay before fetching new words
        }
    });
}

/**
 * Initilize local storage if not already initialized as mathing-game, and add new game to it
 */
function addGame(L1, L2, n, reading_level) {
    if (!localStorage.getItem("matching-game")) {
        localStorage.setItem("matching-game", JSON.stringify([]));
    }

    const games = JSON.parse(localStorage.getItem("matching-game"));
    games.push({ L1, L2, n, reading_level });
    localStorage.setItem("matching-game", JSON.stringify(games));

    return games;
}

/**
 * Create buttons for a shuffled array of words.
 */
function createButtons(words, side) {
    return words
        .map(word => `<button class="word-btn" data-side="${side}" data-word="${word}">${word}</button>`)
        .join(" ");
}

/**
 * Attach handlers to buttons for game logic.
 */
function attachButtonHandlers(pairs, onGameComplete) {
    const buttons = document.querySelectorAll(".word-btn");
    const statusMessage = document.getElementById("status-message");
    let activeWord = null;
    let correctMatches = 0;

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const side = button.dataset.side;
            const word = button.dataset.word;

            if (!activeWord) {
                setActiveWord(button, side, word);
            } else if (activeWord.side === side) {
                switchActiveWord(button, side, word);
            } else {
                if (checkMatch(pairs, activeWord.word, word)) {
                    markAsMatched(activeWord.element, button);
                    activeWord = null;
                    correctMatches++;

                    if (correctMatches === pairs.length) {
                        onGameComplete();
                    } else {
                        displayMessage("Correct! Keep going.", "green");
                    }
                } else {
                    resetActiveWord(activeWord.element);
                    activeWord = null;
                    displayMessage("Incorrect match. Try again.", "red");
                }
            }
        });
    });

    function setActiveWord(button, side, word) {
        activeWord = { side, word, element: button };
        button.classList.add("active");
    }

    function switchActiveWord(button, side, word) {
        activeWord.element.classList.remove("active");
        activeWord = { side, word, element: button };
        button.classList.add("active");
    }
}

/**
 * Check if two words form a valid pair.
 */
function checkMatch(pairs, word1, word2) {
    return pairs.some(pair => (pair.L1 === word1 && pair.L2 === word2) || (pair.L2 === word1 && pair.L1 === word2));
}

/**
 * Mark two buttons as matched.
 */
function markAsMatched(button1, button2) {
    button1.disabled = true;
    button2.disabled = true;
    button1.classList.add("matched");
    button2.classList.add("matched");
}

/**
 * Reset the active word button.
 */
function resetActiveWord(button) {
    button.classList.remove("active");
}

/**
 * Display a success message.
 */
function displaySuccess(message) {
    displayMessage(message, "green");
}

/**
 * Display an error message.
 */
function displayError(message) {
    displayMessage(message, "red");
}

/**
 * Display a status message.
 */
function displayMessage(message, color) {
    const statusMessage = document.getElementById("status-message");
    statusMessage.textContent = message;
    statusMessage.style.color = color;
}

/**
 * Start a timer and return the interval reference.
 */
// Same as above, but instead use timestamp and subtraction to avoid drift
function startTimer() {
    const startTime = Date.now();
    const timerElement = document.getElementById("timer");

    if (!timerElement) {
        console.error("Timer element not found in the DOM.");
        return null;
    }

    return setInterval(() => {
        const elapsed = Date.now() - startTime;
        timerElement.textContent = `Time: ${formatTime(Math.floor(elapsed / 1000))}`;
    }, 1000);
}

/**
 * Format time as MM:SS.
 */
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, "0")}`;
}

/**
 * Shuffle an array using Fisher-Yates algorithm.
 */
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}


