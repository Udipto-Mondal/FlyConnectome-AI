/**
 * main.js
 * Application controller connecting UI components to FastAPI backend.
 */

import { CircuitCanvas } from './components/CircuitCanvas.js';
import { AgentStream } from './components/AgentStream.js';
import { AblationStudio } from './components/AblationStudio.js';
import { ReportViewer } from './components/ReportViewer.js';

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : '/api';

class App {
  constructor() {
    this.canvas = new CircuitCanvas('circuitCanvas', 'canvasTooltip');
    this.agentStream = new AgentStream('agentStreamList', 'pipelineTimerBadge');
    this.reportViewer = new ReportViewer('reportContainer');
    this.ablationStudio = new AblationStudio('ablationStudioContent', (silencedIds) => {
      this.handleAblationChange(silencedIds);
    });

    this.currentData = null;
    this.presets = [];

    this._initElements();
    this._initEventListeners();
    this.bootstrap();
  }

  _initElements() {
    this.queryInput = document.getElementById('queryInput');
    this.discoverBtn = document.getElementById('discoverBtn');
    this.btnSpinner = document.getElementById('btnSpinner');
    this.btnText = this.discoverBtn.querySelector('.btn-text');
    this.presetsList = document.getElementById('presetsList');
    this.circuitSubtitle = document.getElementById('circuitSubtitle');
    this.toggleAutoRotateBtn = document.getElementById('toggleAutoRotateBtn');
    this.resetCamBtn = document.getElementById('resetCamBtn');
    this.copyReportBtn = document.getElementById('copyReportBtn');
    this.printReportBtn = document.getElementById('printReportBtn');
    this.statsNeuronsCount = document.getElementById('statsNeuronsCount');
  }

  _initEventListeners() {
    this.discoverBtn.addEventListener('click', () => {
      const q = this.queryInput.value.trim();
      if (q) this.runDiscovery(q);
    });

    this.queryInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const q = this.queryInput.value.trim();
        if (q) this.runDiscovery(q);
      }
    });

    this.toggleAutoRotateBtn.addEventListener('click', () => {
      const isAuto = this.canvas.toggleAutoRotate();
      this.toggleAutoRotateBtn.querySelector('span').textContent = `Auto-Rotate: ${isAuto ? 'ON' : 'OFF'}`;
    });

    this.resetCamBtn.addEventListener('click', () => {
      this.canvas.resetView();
    });

    this.copyReportBtn.addEventListener('click', () => {
      const md = this.reportViewer.getMarkdown();
      if (md) {
        navigator.clipboard.writeText(md).then(() => {
          const original = this.copyReportBtn.querySelector('span').textContent;
          this.copyReportBtn.querySelector('span').textContent = 'Copied!';
          setTimeout(() => {
            this.copyReportBtn.querySelector('span').textContent = original;
          }, 1800);
        });
      }
    });

    this.printReportBtn.addEventListener('click', () => {
      window.print();
    });
  }

  async bootstrap() {
    try {
      // 1. Fetch presets
      const presResp = await fetch(`${API_BASE}/presets`);
      if (presResp.ok) {
        this.presets = await presResp.json();
        this.renderPresets();
      }

      // 2. Fetch stats
      const statsResp = await fetch(`${API_BASE}/stats`);
      if (statsResp.ok) {
        const stats = await statsResp.json();
        if (this.statsNeuronsCount) {
          this.statsNeuronsCount.textContent = `${stats.total_neurons} Nodes • ${stats.total_synapses} Synapses`;
        }
      }

      // 3. Automatically run primary showcase query on load
      const defaultQuery = "Trace the visual looming escape circuit to jump motor neurons. What happens if Giant Fiber is knocked out?";
      this.queryInput.value = defaultQuery;
      this.runDiscovery(defaultQuery);
    } catch (err) {
      console.warn('Backend not reachable yet; retrying or running with local fallback:', err);
    }
  }

  renderPresets() {
    this.presetsList.innerHTML = '';
    this.presets.forEach(preset => {
      const tag = document.createElement('div');
      tag.className = 'preset-tag';
      tag.textContent = preset.title;
      tag.addEventListener('click', () => {
        this.queryInput.value = preset.query;
        this.runDiscovery(preset.query);
      });
      this.presetsList.appendChild(tag);
    });
  }

  setLoading(isLoading) {
    if (isLoading) {
      this.discoverBtn.disabled = true;
      this.btnSpinner.classList.remove('hidden');
      this.btnText.textContent = 'Discovering...';
    } else {
      this.discoverBtn.disabled = false;
      this.btnSpinner.classList.add('hidden');
      this.btnText.textContent = 'Discover Circuit';
    }
  }

  async runDiscovery(query) {
    this.setLoading(true);
    this.agentStream.setLoading(query);

    try {
      const resp = await fetch(`${API_BASE}/discover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status}: ${await resp.text()}`);
      }

      const data = await resp.json();
      this.currentData = data;

      // Update 3D Canvas
      const subgraph = data.graph.subgraph;
      const primaryPathNodes = (data.graph.paths && data.graph.paths[0]) ? data.graph.paths[0].nodes.map(n => n.id) : [];
      this.canvas.setData(subgraph, primaryPathNodes);

      if (data.ablation && data.ablation.silenced_neurons) {
        this.canvas.setSilencedNodes(data.ablation.silenced_neurons.map(n => n.id));
      } else {
        this.canvas.setSilencedNodes([]);
      }

      // Update Subtitle
      this.circuitSubtitle.textContent = data.plan.subsystem || 'Active Circuit';

      // Update Agent Stream
      this.agentStream.renderTimeline(data.agent_timeline, data.execution_time_ms);

      // Update Ablation Studio
      this.ablationStudio.setCircuitContext(data.plan.subsystem, subgraph.nodes, data.ablation);

      // Update Scientific Report
      this.reportViewer.render(data.report.markdown_report);

    } catch (err) {
      console.error('Discovery error:', err);
      alert('Error communicating with backend: ' + err.message);
    } finally {
      this.setLoading(false);
    }
  }

  async handleAblationChange(silencedIds) {
    this.canvas.setSilencedNodes(silencedIds);

    if (!this.currentData) return;

    if (!silencedIds.length) {
      this.ablationStudio.updateMetrics({
        severance_percentage: 0,
        throughput_loss_percentage: 0,
        vulnerability_score: 0,
        explanation: "All neuronal pathways restored. Normal synaptic transmission operational."
      });
      return;
    }

    try {
      const resp = await fetch(`${API_BASE}/ablate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          silenced_ids: silencedIds,
          source_ids: this.currentData.plan.source_neuron_ids,
          target_ids: this.currentData.plan.target_neuron_ids
        })
      });

      if (resp.ok) {
        const ablationResult = await resp.json();
        this.ablationStudio.updateMetrics(ablationResult);
      }
    } catch (err) {
      console.error('Ablation simulation error:', err);
    }
  }
}

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', () => {
  new App();
});
