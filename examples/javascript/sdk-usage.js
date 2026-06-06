/**
 * MEOK AI Labs - JavaScript SDK Examples
 * Browser and Node.js usage patterns
 */

// Import the SDK (works in both environments)
import { MEOKClient } from '@meokai/js';

// Initialize client
const meok = new MEOKClient({
  apiKey: process.env.MEOK_API_KEY || 'your-api-key'
});

// ============================================
// Constitutional AI Analysis
// ============================================

async function analyzeContent() {
  const content = document.getElementById('user-input')?.value || 
    'Help me with my coding project';

  const result = await meok.governance.analyze({
    content,
    framework: 'constitutional',
    contentType: 'text'
  });

  if (result.violations?.length > 0) {
    showWarning(`Violations found: ${result.violations.join(', ')}`);
    return false;
  }

  return true;
}

// ============================================
// Real-time Content Moderation
// ============================================

class ContentModerator {
  constructor() {
    this.queue = [];
    this.processing = false;
  }

  async moderate(content) {
    const result = await meok.governance.analyze({
      content,
      framework: 'constitutional'
    });

    return {
      safe: !result.violations?.length,
      score: result.score,
      violations: result.violations || [],
      recommendations: result.recommendations || []
    };
  }

  async moderateBatch(contents) {
    const results = await Promise.all(
      contents.map(content => this.moderate(content))
    );
    return results;
  }
}

// ============================================
// Memory System
// ============================================

async function memoryExamples() {
  // Store a memory
  const stored = await meok.memory.store({
    content: 'User prefers dark mode theme',
    type: 'semantic',
    tags: ['preference', 'ui'],
    importance: 0.8
  });
  console.log('Memory stored:', stored.id);

  // Query memories
  const results = await meok.memory.query({
    query: 'user interface preferences',
    limit: 10
  });

  results.memories.forEach(mem => {
    console.log(`- ${mem.content.substring(0, 50)}...`);
  });

  return results;
}

// ============================================
// Agent Task Management
// ============================================

async function agentExamples() {
  // Create a task
  const task = await meok.agents.createTask({
    agentId: 'researcher',
    instruction: 'Find latest AI governance news',
    priority: 'high'
  });

  console.log('Task created:', task.id);

  // Poll for completion
  let status;
  while (status !== 'completed' && status !== 'failed') {
    await sleep(1000);
    const taskStatus = await meok.agents.getTask(task.id);
    status = taskStatus.status;
    console.log('Status:', status);
  }

  return status;
}

// ============================================
// Webhook Integration (Browser)
// ============================================

class WebhookListener {
  constructor(endpoint) {
    this.endpoint = endpoint;
    this.handlers = new Map();
  }

  on(eventType, handler) {
    this.handlers.set(eventType, handler);
  }

  async listen() {
    // Register service worker for webhooks
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker registered');
    }
  }
}

// ============================================
// UI Helpers
// ============================================

function showWarning(message) {
  const toast = document.createElement('div');
  toast.className = 'meok-warning-toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

function showSuccess(message) {
  const toast = document.createElement('div');
  toast.className = 'meok-success-toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// ============================================
// React Hook Example
// ============================================

/*
import { useState, useEffect } from 'react';

function useMEOK(apiKey) {
  const [client, setClient] = useState(null);
  const [state, setState] = useState({ loading: true, error: null });

  useEffect(() => {
    const meok = new MEOKClient({ apiKey });
    setClient(meok);
    setState({ loading: false, error: null });
  }, [apiKey]);

  const analyze = async (content) => {
    if (!client) return;
    setState(s => ({ ...s, loading: true }));
    try {
      const result = await client.governance.analyze({ content });
      setState({ loading: false, error: null });
      return result;
    } catch (error) {
      setState({ loading: false, error: error.message });
      throw error;
    }
  };

  return { client, ...state, analyze };
}

// Usage:
// const { loading, error, analyze } = useMEOK('your-api-key');
*/

// ============================================
// Export for module usage
// ============================================

export {
  analyzeContent,
  ContentModerator,
  memoryExamples,
  agentExamples,
  WebhookListener
};
