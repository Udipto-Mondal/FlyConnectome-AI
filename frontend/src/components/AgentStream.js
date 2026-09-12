/**
 * AgentStream.js
 * Visualizes real-time multi-agent reasoning steps, thought logs, and execution duration.
 */

export class AgentStream {
  constructor(containerId, timerBadgeId) {
    this.container = document.getElementById(containerId);
    this.timerBadge = document.getElementById(timerBadgeId);
  }

  setLoading(query) {
    this.timerBadge.textContent = 'Running Agents...';
    this.timerBadge.className = 'card-badge pulse-badge';

    this.container.innerHTML = `
      <div class="agent-step-card active">
        <div class="agent-step-header">
          <div class="agent-title-info">
            <div class="agent-number">1</div>
            <div>
              <div class="agent-name">Planner Agent</div>
              <div class="agent-role">Decomposing research query into circuit hypotheses...</div>
            </div>
          </div>
          <div class="spinner"></div>
        </div>
      </div>
      <div class="agent-step-card" style="opacity: 0.5;">
        <div class="agent-step-header">
          <div class="agent-title-info">
            <div class="agent-number">2</div>
            <div>
              <div class="agent-name">Connectome Graph-RAG Agent</div>
              <div class="agent-role">Pending execution...</div>
            </div>
          </div>
        </div>
      </div>
      <div class="agent-step-card" style="opacity: 0.4;">
        <div class="agent-step-header">
          <div class="agent-title-info">
            <div class="agent-number">3</div>
            <div>
              <div class="agent-name">Literature Validation Agent</div>
              <div class="agent-role">Pending execution...</div>
            </div>
          </div>
        </div>
      </div>
      <div class="agent-step-card" style="opacity: 0.3;">
        <div class="agent-step-header">
          <div class="agent-title-info">
            <div class="agent-number">4</div>
            <div>
              <div class="agent-name">Synthesis & Discovery Agent</div>
              <div class="agent-role">Pending execution...</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderTimeline(timeline, totalTimeMs) {
    this.timerBadge.textContent = `${totalTimeMs} ms`;
    this.timerBadge.className = 'card-badge info-badge';

    this.container.innerHTML = '';

    timeline.forEach((step, index) => {
      const card = document.createElement('div');
      card.className = 'agent-step-card';

      const logsHtml = (step.logs || []).map(log => `<div class="agent-log-item">${escapeHtml(log)}</div>`).join('');

      card.innerHTML = `
        <div class="agent-step-header">
          <div class="agent-title-info">
            <div class="agent-number">${index + 1}</div>
            <div>
              <div class="agent-name">${step.agent_name}</div>
              <div class="agent-role">${step.role}</div>
            </div>
          </div>
          <div class="agent-duration">${step.duration_ms} ms</div>
        </div>
        <div class="agent-logs-list">
          ${logsHtml}
        </div>
      `;

      this.container.appendChild(card);
    });
  }
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}
