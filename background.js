// Initialize extension when installed
chrome.runtime.onInstalled.addListener(() => {
  // Set default settings
  chrome.storage.sync.set({
    settings: {
      connectionRequests: {
        enabled: false,
        messageTemplate: 'Hi {name}, I noticed your work as {headline} and would love to connect!',
        maxRequests: 50
      },
      postCreation: {
        enabled: false,
        useAI: true,
        hashtags: []
      },
      feedScrolling: {
        enabled: false,
        autoEngage: false,
        keywords: []
      },
      messaging: {
        enabled: false,
        templates: []
      }
    }
  });
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getSettings') {
    chrome.storage.sync.get(['settings'], (result) => {
      sendResponse(result.settings);
    });
    return true; // Required for async sendResponse
  }
});

// Handle tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url.includes('linkedin.com')) {
    // Inject content script if needed
    chrome.scripting.executeScript({
      target: { tabId },
      files: ['content.js']
    });
  }
}); 