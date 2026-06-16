chrome.action.onClicked.addListener(() => {
  chrome.windows.create({
    url: 'popup.html',
    type: 'popup',
    width: 380,
    height: 500,
    focused: true
  }, (window) => {
    chrome.windows.update(window.id, { focused: true });
  });
});
