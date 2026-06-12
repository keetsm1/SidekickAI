document.getElementById('askBtn').addEventListener("click", async () => {
    const question = document.getElementById("question").value;

    // get current tab
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});

    const pageText = await chrome.scripting.executeScript({
        target: {tabId: tab.id},
        func: () => document.body.innerText
    });

    const text = pageText[0].result

    const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: question,
            page_text: text
        })
    });

    const data = await response.json();

    document.getElementById("answer").innerText = data.answer;
});