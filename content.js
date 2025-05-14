// Utility functions for human-like behavior
const randomDelay = (min, max) => {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  return new Promise(resolve => setTimeout(resolve, delay));
};

const simulateHumanScroll = async (element, distance) => {
  const steps = 10;
  const stepDistance = distance / steps;
  
  for (let i = 0; i < steps; i++) {
    element.scrollBy(0, stepDistance);
    await randomDelay(100, 300);
  }
};

// API communication functions
const API_BASE_URL = 'http://localhost:3000/api';

const callAPI = async (endpoint, method = 'GET', data = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : null,
    });
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// Connection automation
class ConnectionAutomation {
  constructor(settings) {
    this.settings = settings;
    this.isRunning = false;
  }

  async start() {
    this.isRunning = true;
    await callAPI('/automation/start', 'POST', { type: 'connections', settings: this.settings });
    
    while (this.isRunning) {
      try {
        const connectButtons = document.querySelectorAll('button[aria-label*="Connect"]');
        
        for (const button of connectButtons) {
          if (!this.isRunning) break;
          
          const profileCard = button.closest('.artdeco-card');
          if (!profileCard) continue;

          const name = profileCard.querySelector('.artdeco-entity-lockup__title')?.textContent.trim();
          const headline = profileCard.querySelector('.artdeco-entity-lockup__subtitle')?.textContent.trim();
          
          if (name && headline) {
            await this.sendConnectionRequest(button, name, headline);
          }
          
          await randomDelay(2000, 4000);
        }
        
        await simulateHumanScroll(document.documentElement, 800);
        await randomDelay(1000, 2000);
      } catch (error) {
        console.error('Connection automation error:', error);
        await randomDelay(5000, 10000);
      }
    }
  }

  async sendConnectionRequest(button, name, headline) {
    try {
      button.click();
      await randomDelay(1000, 2000);
      
      const addNoteButton = document.querySelector('button[aria-label="Add a note"]');
      if (addNoteButton) {
        addNoteButton.click();
        await randomDelay(1000, 2000);
        
        const messageInput = document.querySelector('textarea#custom-message');
        if (messageInput) {
          const personalizedMessage = this.settings.messageTemplate
            .replace('{name}', name)
            .replace('{headline}', headline);
          
          messageInput.value = personalizedMessage;
          messageInput.dispatchEvent(new Event('input', { bubbles: true }));
          
          await randomDelay(1000, 2000);
          
          const sendButton = document.querySelector('button[aria-label="Send now"]');
          if (sendButton) {
            sendButton.click();
            // Log the connection request to the backend
            await callAPI('/connections', 'POST', {
              profile: { name, headline, message: personalizedMessage }
            });
          }
        }
      }
    } catch (error) {
      console.error('Error sending connection request:', error);
    }
  }

  async stop() {
    this.isRunning = false;
    await callAPI('/automation/stop', 'POST', { type: 'connections' });
  }
}

// Post creation automation
class PostAutomation {
  constructor(settings) {
    this.settings = settings;
    this.isRunning = false;
  }

  async start() {
    this.isRunning = true;
    await callAPI('/automation/start', 'POST', { type: 'posts', settings: this.settings });
    
    while (this.isRunning) {
      try {
        const startPostButton = document.querySelector('button[aria-label="Start a post"]');
        if (startPostButton) {
          await this.createPost();
        }
        await randomDelay(300000, 600000); // Wait 5-10 minutes between posts
      } catch (error) {
        console.error('Post automation error:', error);
        await randomDelay(5000, 10000);
      }
    }
  }

  async createPost() {
    try {
      const startPostButton = document.querySelector('button[aria-label="Start a post"]');
      startPostButton.click();
      await randomDelay(1000, 2000);

      const postInput = document.querySelector('.ql-editor');
      if (postInput) {
        let content = '';
        if (this.settings.useAI) {
          // TODO: Implement AI content generation
          content = 'AI-generated post content';
        } else {
          content = 'Your post content here';
        }

        postInput.innerHTML = content;
        postInput.dispatchEvent(new Event('input', { bubbles: true }));

        await randomDelay(1000, 2000);

        const postButton = document.querySelector('button[aria-label="Post"]');
        if (postButton) {
          postButton.click();
          // Log the post to the backend
          await callAPI('/posts', 'POST', { content });
        }
      }
    } catch (error) {
      console.error('Error creating post:', error);
    }
  }

  async stop() {
    this.isRunning = false;
    await callAPI('/automation/stop', 'POST', { type: 'posts' });
  }
}

// Feed scrolling automation
class FeedAutomation {
  constructor(settings) {
    this.settings = settings;
    this.isRunning = false;
  }

  async start() {
    this.isRunning = true;
    await callAPI('/automation/start', 'POST', { type: 'feed', settings: this.settings });
    
    while (this.isRunning) {
      try {
        await this.scrollAndEngage();
        await randomDelay(2000, 4000);
      } catch (error) {
        console.error('Feed automation error:', error);
        await randomDelay(5000, 10000);
      }
    }
  }

  async scrollAndEngage() {
    const feed = document.querySelector('.feed-shared-update-v2');
    if (feed) {
      await simulateHumanScroll(feed, 500);
      
      if (this.settings.autoEngage) {
        const posts = document.querySelectorAll('.feed-shared-update-v2');
        for (const post of posts) {
          if (!this.isRunning) break;
          
          const content = post.textContent.toLowerCase();
          if (this.settings.keywords.some(keyword => content.includes(keyword.toLowerCase()))) {
            await this.engageWithPost(post);
          }
        }
      }
    }
  }

  async engageWithPost(post) {
    try {
      const likeButton = post.querySelector('button[aria-label*="Like"]');
      if (likeButton) {
        likeButton.click();
        await randomDelay(1000, 2000);
      }
    } catch (error) {
      console.error('Error engaging with post:', error);
    }
  }

  async stop() {
    this.isRunning = false;
    await callAPI('/automation/stop', 'POST', { type: 'feed' });
  }
}

// Message automation
class MessageAutomation {
  constructor(settings) {
    this.settings = settings;
    this.isRunning = false;
  }

  async start() {
    this.isRunning = true;
    await callAPI('/automation/start', 'POST', { type: 'messages', settings: this.settings });
    
    while (this.isRunning) {
      try {
        await this.sendMessages();
        await randomDelay(300000, 600000); // Wait 5-10 minutes between message batches
      } catch (error) {
        console.error('Message automation error:', error);
        await randomDelay(5000, 10000);
      }
    }
  }

  async sendMessages() {
    // TODO: Implement message sending logic
    // When implemented, add API call to log messages
    await callAPI('/messages', 'POST', { message: 'Message content' });
  }

  async stop() {
    this.isRunning = false;
    await callAPI('/automation/stop', 'POST', { type: 'messages' });
  }
}

// Initialize automation instances
let connectionAutomation = null;
let postAutomation = null;
let feedAutomation = null;
let messageAutomation = null;

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'startAutomation') {
    const settings = request.settings;
    
    switch (request.type) {
      case 'connections':
        connectionAutomation = new ConnectionAutomation(settings);
        connectionAutomation.start();
        break;
      case 'posts':
        postAutomation = new PostAutomation(settings);
        postAutomation.start();
        break;
      case 'feed':
        feedAutomation = new FeedAutomation(settings);
        feedAutomation.start();
        break;
      case 'messages':
        messageAutomation = new MessageAutomation(settings);
        messageAutomation.start();
        break;
    }
  } else if (request.action === 'stopAutomation') {
    connectionAutomation?.stop();
    postAutomation?.stop();
    feedAutomation?.stop();
    messageAutomation?.stop();
  }
}); 