/**
 * MEOK AI Labs - JavaScript/TypeScript SDK
 * Constitutional AI Governance Platform
 */

class MEOKClient {
  /**
   * Create a MEOK API client
   * @param {Object} config - Configuration options
   * @param {string} config.apiKey - Your API key
   * @param {string} [config.baseUrl='https://meok.ai/api/v1'] - Base API URL
   * @param {number} [config.timeout=60000] - Request timeout in ms
   */
  constructor({ apiKey, baseUrl = 'https://meok.ai/api/v1', timeout = 60000 }) {
    this.apiKey = apiKey || process.env.MEOK_API_KEY;
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.timeout = timeout;

    if (!this.apiKey) {
      throw new Error('API key required. Set MEOK_API_KEY env var or pass apiKey.');
    }
  }

  /**
   * Make an API request
   */
  async _request(method, endpoint, { data, params } = {}) {
    const url = `${this.baseUrl}/${endpoint.replace(/^\//, '')}`;
    
    const headers = {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
    };

    const options = {
      method,
      headers,
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    options.signal = controller.signal;

    try {
      const response = await fetch(url, options);
      
      if (response.status === 429) {
        // Rate limited - wait and retry
        await new Promise(r => setTimeout(r, 2000));
        return this._request(method, endpoint, { data, params });
      }

      const json = await response.json();
      
      if (!response.ok) {
        throw new MEOKError(json.message || 'Request failed', response.status, json);
      }

      return json;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Get current rate limit status
   */
  async getRateLimitInfo() {
    return this._request('GET', '/auth/rate-limit');
  }
}

/**
 * Governance Client
 */
class GovernanceClient {
  constructor(client) {
    this._client = client;
  }

  /**
   * Analyze content against Constitutional AI principles
   * @param {string} content - Content to analyze
   * @param {Object} [options]
   * @param {string} [options.type='text'] - Content type
   * @param {string} [options.framework='constitutional'] - Governance framework
   */
  async analyze(content, { type = 'text', framework = 'constitutional' } = {}) {
    return this._client._request('POST', '/governance/analyze', {
      data: { content, type, framework }
    });
  }

  /**
   * Check compliance against standards
   * @param {string} content - Content to check
   * @param {string[]} standards - Standards to check against
   */
  async checkCompliance(content, standards) {
    return this._client._request('POST', '/governance/compliance', {
      data: { content, standards }
    });
  }
}

/**
 * Memory Client
 */
class MemoryClient {
  constructor(client) {
    this._client = client;
  }

  /**
   * Store a memory
   * @param {string} content - Memory content
   * @param {Object} [options]
   * @param {string} [options.type='episodic'] - Memory type
   * @param {string[]} [options.tags] - Tags
   * @param {number} [options.importance=0.5] - Importance score
   */
  async store(content, { type = 'episodic', tags = [], importance = 0.5 } = {}) {
    return this._client._request('POST', '/memory', {
      data: { content, type, tags, importance }
    });
  }

  /**
   * Query memories
   * @param {string} query - Search query
   * @param {number} [limit=10] - Max results
   */
  async query(query, limit = 10) {
    return this._client._request('GET', '/memory', {
      params: { q: query, limit }
    });
  }
}

/**
 * Agent Client
 */
class AgentClient {
  constructor(client) {
    this._client = client;
  }

  /**
   * Create an agent task
   * @param {string} agentId - Agent identifier
   * @param {string} instruction - Task instruction
   * @param {string} [priority='normal'] - Priority level
   */
  async createTask(agentId, instruction, priority = 'normal') {
    return this._client._request('POST', `/agents/${agentId}/tasks`, {
      data: { instruction, priority }
    });
  }

  /**
   * Get task status
   * @param {string} taskId - Task identifier
   */
  async getTask(taskId) {
    return this._client._request('GET', `/agents/tasks/${taskId}`);
  }
}

/**
 * Consciousness Client
 */
class ConsciousnessClient {
  constructor(client) {
    this._client = client;
  }

  /**
   * Get consciousness state
   */
  async getState() {
    return this._client._request('GET', '/consciousness/state');
  }

  /**
   * Enter dream mode
   */
  async enterDreamMode() {
    return this._client._request('POST', '/consciousness/dream');
  }
}

// Add sub-clients to main client
MEOKClient.prototype.governance = null;
MEOKClient.prototype.memory = null;
MEOKClient.prototype.agents = null;
MEOKClient.prototype.consciousness = null;

const originalConstructor = MEOKClient;
function WrappedClient(config) {
  const client = new originalConstructor(config);
  client.governance = new GovernanceClient(client);
  client.memory = new MemoryClient(client);
  client.agents = new AgentClient(client);
  client.consciousness = new ConsciousnessClient(client);
  return client;
}

// Copy prototype
WrappedClient.prototype = originalConstructor.prototype;

/**
 * Custom error class
 */
class MEOKError extends Error {
  constructor(message, statusCode, response) {
    super(message);
    this.name = 'MEOKError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

// Export
export { WrappedClient as MEOKClient, MEOKError };
export default MEOKClient;

// Also support CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MEOKClient, MEOKError };
}
