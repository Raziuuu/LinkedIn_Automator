import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';

const Popup = () => {
  const [activeTab, setActiveTab] = useState('connections');
  const [isRunning, setIsRunning] = useState(false);
  const [settings, setSettings] = useState({
    connectionRequests: {
      enabled: false,
      messageTemplate: '',
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
  });

  useEffect(() => {
    // Load saved settings from Chrome storage
    chrome.storage.sync.get(['settings'], (result) => {
      if (result.settings) {
        setSettings(result.settings);
      }
    });
  }, []);

  const saveSettings = () => {
    chrome.storage.sync.set({ settings });
  };

  const startAutomation = async () => {
    setIsRunning(true);
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (tab.url.includes('linkedin.com')) {
      chrome.tabs.sendMessage(tab.id, {
        action: 'startAutomation',
        settings: settings[activeTab]
      });
    }
  };

  const stopAutomation = async () => {
    setIsRunning(false);
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (tab.url.includes('linkedin.com')) {
      chrome.tabs.sendMessage(tab.id, { action: 'stopAutomation' });
    }
  };

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">LinkedIn Automation</h1>
        <button
          onClick={isRunning ? stopAutomation : startAutomation}
          className={`px-4 py-2 rounded ${
            isRunning ? 'bg-red-500' : 'bg-blue-500'
          } text-white`}
        >
          {isRunning ? 'Stop' : 'Start'}
        </button>
      </div>

      <div className="flex space-x-2 mb-4">
        <button
          onClick={() => setActiveTab('connections')}
          className={`px-3 py-1 rounded ${
            activeTab === 'connections' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Connections
        </button>
        <button
          onClick={() => setActiveTab('posts')}
          className={`px-3 py-1 rounded ${
            activeTab === 'posts' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Posts
        </button>
        <button
          onClick={() => setActiveTab('feed')}
          className={`px-3 py-1 rounded ${
            activeTab === 'feed' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Feed
        </button>
        <button
          onClick={() => setActiveTab('messages')}
          className={`px-3 py-1 rounded ${
            activeTab === 'messages' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Messages
        </button>
      </div>

      <div className="space-y-4">
        {activeTab === 'connections' && (
          <div>
            <h2 className="text-lg font-semibold mb-2">Connection Automation</h2>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.connectionRequests.enabled}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      connectionRequests: {
                        ...settings.connectionRequests,
                        enabled: e.target.checked
                      }
                    })
                  }
                  className="mr-2"
                />
                Enable Connection Requests
              </label>
              <textarea
                placeholder="Connection request message template"
                value={settings.connectionRequests.messageTemplate}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    connectionRequests: {
                      ...settings.connectionRequests,
                      messageTemplate: e.target.value
                    }
                  })
                }
                className="w-full p-2 border rounded"
                rows="3"
              />
              <input
                type="number"
                placeholder="Max requests per day"
                value={settings.connectionRequests.maxRequests}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    connectionRequests: {
                      ...settings.connectionRequests,
                      maxRequests: parseInt(e.target.value)
                    }
                  })
                }
                className="w-full p-2 border rounded"
              />
            </div>
          </div>
        )}

        {activeTab === 'posts' && (
          <div>
            <h2 className="text-lg font-semibold mb-2">Post Creation</h2>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.postCreation.enabled}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      postCreation: {
                        ...settings.postCreation,
                        enabled: e.target.checked
                      }
                    })
                  }
                  className="mr-2"
                />
                Enable Post Creation
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.postCreation.useAI}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      postCreation: {
                        ...settings.postCreation,
                        useAI: e.target.checked
                      }
                    })
                  }
                  className="mr-2"
                />
                Use AI for Content Generation
              </label>
            </div>
          </div>
        )}

        {activeTab === 'feed' && (
          <div>
            <h2 className="text-lg font-semibold mb-2">Feed Scrolling</h2>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.feedScrolling.enabled}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      feedScrolling: {
                        ...settings.feedScrolling,
                        enabled: e.target.checked
                      }
                    })
                  }
                  className="mr-2"
                />
                Enable Feed Scrolling
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.feedScrolling.autoEngage}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      feedScrolling: {
                        ...settings.feedScrolling,
                        autoEngage: e.target.checked
                      }
                    })
                  }
                  className="mr-2"
                />
                Auto-engage with Posts
              </label>
            </div>
          </div>
        )}

        {activeTab === 'messages' && (
          <div>
            <h2 className="text-lg font-semibold mb-2">Message Automation</h2>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.messaging.enabled}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      messaging: {
                        ...settings.messaging,
                        enabled: e.target.checked
                      }
                    })
                  }
                  className="mr-2"
                />
                Enable Message Automation
              </label>
            </div>
          </div>
        )}
      </div>

      <button
        onClick={saveSettings}
        className="mt-4 px-4 py-2 bg-green-500 text-white rounded w-full"
      >
        Save Settings
      </button>
    </div>
  );
};

ReactDOM.render(<Popup />, document.getElementById('root')); 