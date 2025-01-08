chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('contentScript.js received message:', message);

    if (message.type === 'HIGHLIGHT_CHUNKS') {
        const { chunks } = message;

        const instance = new Mark(document.body);
        instance.unmark();

        let mostSimilarElement = null;

        chunks.forEach(({ text, similarity }, index) => {
            if (text && similarity >= 0.1) {
                highlightTextOnPage(text);
                if (index === 1) { // Check if it's the most similar item (index 1)
                    // Find the first highlighted element for this chunk
                    mostSimilarElement = document.querySelector('mark[data-markjs="true"]');
                    console.log("Found most similar element:", mostSimilarElement);
                }
            }
        });

        if (mostSimilarElement) {
            mostSimilarElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start' // or 'center' or 'end'
            });
        }

        sendResponse({ status: "ok" });
    }

    if (message.type === 'CLEAR_HIGHLIGHTS') {
        const instance = new Mark(document.body);
        instance.unmark();
        sendResponse({ status: "ok" });
    }
});

function highlightTextOnPage(searchText) {
    const instance = new Mark(document.body);

    instance.mark(searchText, {
        accuracy: "exactly",
        separateWordSearch: false,
        acrossElements: true
    });
    console.log("Marked: " + searchText);
}
