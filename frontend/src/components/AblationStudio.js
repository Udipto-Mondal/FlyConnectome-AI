/**
 * AblationStudio.js
 * Interactive In-Silico Neuronal Knockout & Circuit Resilience Testing Studio.
 */

export class AblationStudio {
  constructor(containerId, onAblationChange) {
    this.container = document.getElementById(containerId);
    this.onAblationChange = onAblationChange;
    this.silencedNodeIds = new Set();
    this.currentSubsystem = 'Visual Escape';
    this.currentNodes = [];
    this.lastAblationResult = null;
  }

  setCircuitContext(subsystem, nodes, ablationResult = null) {
    this.currentSubsystem = subsystem;
    this.currentNodes = nodes;
    this.lastAblationResult = ablationResult;

    // If backend provided an ablation result, initialize silenced nodes
    if (ablationResult && ablationResult.silenced_neurons) {
      this.silencedNodeIds = new Set(ablationResult.silenced_neurons.map(n => String(n.id)));
    } else {
      this.silencedNodeIds.clear();
    }

    this.render();
  }

  render() {
    // Select top 4-5 key candidate neurons from current nodes for toggle switches
    const candidateNodes = this.currentNodes.filter(n => {
      const type = (n.type || '').toLowerCase();
      return type.includes('giant') || type.includes('command') || type.includes('compass') || 
             type.includes('kenyon') || type.includes('looming') || type.includes('motor') ||
             type.includes('lobula') || type.includes('relay');
    }).slice(0, 5);

    // If candidates empty, take first 4 nodes
    const displayNodes = candidateNodes.length ? candidateNodes : this.currentNodes.slice(0, 4);

    const togglesHtml = displayNodes.map(node => {
      const nId = String(node.id);
      const isSilenced = this.silencedNodeIds.has(nId);
      return `
        <div class="ablation-toggle-card ${isSilenced ? 'silenced' : ''}">
          <div class="toggle-info">
            <h4>${node.name}</h4>
            <p>${node.type} • ${node.neuropil}</p>
          </div>
          <label class="switch">
            <input type="checkbox" data-neuron-id="${nId}" ${isSilenced ? 'checked' : ''}>
            <span class="slider"></span>
          </label>
        </div>
      `;
    }).join('');

    const res = this.lastAblationResult || {
      severance_percentage: 0,
      throughput_loss_percentage: 0,
      vulnerability_score: 0,
      explanation: "All neuronal pathways intact. Toggle a neuron above to simulate physical lesion or optogenetic silencing."
    };

    const isSevere = res.severance_percentage > 50;

    this.container.innerHTML = `
      <div class="ablation-toggles-grid">
        ${togglesHtml}
      </div>

      <div class="ablation-metrics-bar">
        <div class="metric-stat">
          <span class="metric-title">Circuit Severance</span>
          <span class="metric-value ${isSevere ? 'severe' : ''}">${res.severance_percentage}%</span>
        </div>
        <div class="metric-stat">
          <span class="metric-title">Throughput Loss</span>
          <span class="metric-value ${isSevere ? 'severe' : ''}">${res.throughput_loss_percentage}%</span>
        </div>
        <div class="metric-stat">
          <span class="metric-title">Vulnerability Index</span>
          <span class="metric-value ${isSevere ? 'severe' : ''}">${res.vulnerability_score} / 10</span>
        </div>
      </div>

      <div class="ablation-explanation-text">
        ${res.explanation}
      </div>
    `;

    // Attach toggle event listeners
    this.container.querySelectorAll('input[type="checkbox"]').forEach(input => {
      input.addEventListener('change', (e) => {
        const nid = e.target.dataset.neuronId;
        if (e.target.checked) {
          this.silencedNodeIds.add(nid);
        } else {
          this.silencedNodeIds.delete(nid);
        }
        if (this.onAblationChange) {
          this.onAblationChange(Array.from(this.silencedNodeIds));
        }
      });
    });
  }

  updateMetrics(ablationResult) {
    this.lastAblationResult = ablationResult;
    this.render();
  }
}
