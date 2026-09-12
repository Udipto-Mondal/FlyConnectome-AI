/**
 * CircuitCanvas.js
 * Interactive 3D/2.5D Canvas visualizer for Drosophila Connectome neural pathways.
 * Supports 3D orbit, zoom, pan, particle pulse animations, and node tooltips.
 */

export class CircuitCanvas {
  constructor(canvasId, tooltipId) {
    this.canvas = document.getElementById(canvasId);
    this.tooltip = document.getElementById(tooltipId);
    this.ctx = this.canvas.getContext('2d');

    this.nodes = [];
    this.edges = [];
    this.highlightedNode = null;
    this.hoveredNode = null;
    this.silencedNodeIds = new Set();

    // Camera & 3D projection parameters
    this.rotX = 0.35;
    this.rotY = 0.55;
    this.zoom = 1.3;
    this.autoRotate = true;
    this.isDragging = false;
    this.lastMouseX = 0;
    this.lastMouseY = 0;

    // Signal pulse particles
    this.particles = [];
    this.lastFrameTime = performance.now();

    this._initEvents();
    this._resize();
    this._animate();
  }

  setData(subgraph, activePathNodes = []) {
    this.nodes = subgraph.nodes || [];
    this.edges = subgraph.edges || [];
    this.activePathNodes = new Set(activePathNodes);

    // Initialize pulse particles along edges
    this.particles = [];
    this.edges.forEach((edge, idx) => {
      // Spawn 2-3 particles per edge
      for (let i = 0; i < 2; i++) {
        this.particles.push({
          sourceId: edge.source,
          targetId: edge.target,
          progress: Math.random(),
          speed: 0.006 + Math.random() * 0.008,
          synapses: edge.synapses || 100
        });
      }
    });
  }

  setSilencedNodes(silencedIds) {
    this.silencedNodeIds = new Set(silencedIds);
  }

  _resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.width = rect.width;
    this.height = rect.height;
  }

  _initEvents() {
    window.addEventListener('resize', () => this._resize());

    // Mouse Drag for 3D Orbit
    this.canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        const dx = e.clientX - this.lastMouseX;
        const dy = e.clientY - this.lastMouseY;
        this.rotY += dx * 0.008;
        this.rotX += dy * 0.008;
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
      } else {
        this._handleHover(e);
      }
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    // Zoom on wheel
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
      this.zoom = Math.max(0.4, Math.min(3.5, this.zoom * zoomFactor));
    }, { passive: false });

    // Touch support
    let touchStartX = 0;
    let touchStartY = 0;
    this.canvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        this.isDragging = true;
      }
    });

    this.canvas.addEventListener('touchmove', (e) => {
      if (this.isDragging && e.touches.length === 1) {
        const dx = e.touches[0].clientX - touchStartX;
        const dy = e.touches[0].clientY - touchStartY;
        this.rotY += dx * 0.01;
        this.rotX += dy * 0.01;
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      }
    });

    this.canvas.addEventListener('touchend', () => {
      this.isDragging = false;
    });
  }

  _handleHover(e) {
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    let closest = null;
    let minDist = 22; // detection radius

    for (const node of this.projectedNodes || []) {
      const dist = Math.hypot(node.screenX - mouseX, node.screenY - mouseY);
      if (dist < minDist) {
        closest = node;
        minDist = dist;
      }
    }

    this.hoveredNode = closest ? closest.raw : null;

    if (this.hoveredNode) {
      const n = this.hoveredNode;
      const isSilenced = this.silencedNodeIds.has(String(n.id));
      this.tooltip.classList.remove('hidden');
      this.tooltip.style.left = `${mouseX + 15}px`;
      this.tooltip.style.top = `${mouseY - 20}px`;
      this.tooltip.innerHTML = `
        <div style="font-weight:700; color:${isSilenced ? '#ff0055' : '#00f0ff'}; margin-bottom:4px;">
          ${n.name} ${isSilenced ? '(SILENCED)' : ''}
        </div>
        <div style="font-size:0.72rem; color:#94a3b8;">
          Type: <strong>${n.type}</strong><br/>
          Region: <strong>${n.neuropil}</strong><br/>
          NT: <strong>${n.neurotransmitter}</strong><br/>
          Subsystem: <strong>${n.subsystem}</strong>
        </div>
      `;
    } else {
      this.tooltip.classList.add('hidden');
    }
  }

  _project3D(coords) {
    const [x, y, z] = coords;
    // Rotation around Y axis
    const cosY = Math.cos(this.rotY);
    const sinY = Math.sin(this.rotY);
    const x1 = x * cosY + z * sinY;
    const z1 = -x * sinY + z * cosY;

    // Rotation around X axis
    const cosX = Math.cos(this.rotX);
    const sinX = Math.sin(this.rotX);
    const y2 = y * cosX - z1 * sinX;
    const z2 = y * sinX + z1 * cosX;

    // Perspective projection
    const distance = 400;
    const scale = (distance / (distance + z2)) * this.zoom;
    const screenX = this.width / 2 + x1 * scale * 1.5;
    const screenY = this.height / 2 - y2 * scale * 1.5;

    return { screenX, screenY, scale, depth: z2 };
  }

  _getNodeColor(node) {
    if (this.silencedNodeIds.has(String(node.id))) {
      return '#ff0055'; // Red for silenced
    }
    const sub = (node.subsystem || '').toLowerCase();
    if (sub.includes('visual')) return '#00f0ff';       // Cyan
    if (sub.includes('escape') || sub.includes('descending')) return '#a855f7'; // Purple / Relay
    if (sub.includes('compass') || sub.includes('navigation')) return '#ffb703'; // Amber
    if (sub.includes('motor')) return '#ff0055';         // Crimson
    if (sub.includes('dimorphic') || sub.includes('courtship')) return '#ff7b00'; // Orange
    if (sub.includes('olfact') || sub.includes('learning')) return '#06d6a0';  // Emerald
    return '#38bdf8';
  }

  _animate() {
    requestAnimationFrame(() => this._animate());

    const now = performance.now();
    const dt = (now - this.lastFrameTime) / 1000;
    this.lastFrameTime = now;

    if (this.autoRotate && !this.isDragging) {
      this.rotY += 0.003;
    }

    this._render();
  }

  _render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    if (!this.nodes.length) {
      ctx.fillStyle = '#64748b';
      ctx.font = '14px Outfit';
      ctx.textAlign = 'center';
      ctx.fillText('No circuit loaded. Enter a query or select a preset above.', this.width / 2, this.height / 2);
      return;
    }

    // 1. Project all nodes to screen coordinates
    const nodeMap = new Map();
    this.projectedNodes = [];

    for (const node of this.nodes) {
      const proj = this._project3D(node.coords || [0, 0, 0]);
      const item = {
        raw: node,
        screenX: proj.screenX,
        screenY: proj.screenY,
        scale: proj.scale,
        depth: proj.depth
      };
      this.projectedNodes.push(item);
      nodeMap.set(String(node.id), item);
    }

    // Sort nodes by depth for painter's algorithm
    this.projectedNodes.sort((a, b) => b.depth - a.depth);

    // 2. Draw Synaptic Edges
    for (const edge of this.edges) {
      const src = nodeMap.get(String(edge.source));
      const tgt = nodeMap.get(String(edge.target));
      if (!src || !tgt) continue;

      const isSrcSilenced = this.silencedNodeIds.has(String(edge.source));
      const isTgtSilenced = this.silencedNodeIds.has(String(edge.target));
      const isSevered = isSrcSilenced || isTgtSilenced;

      ctx.beginPath();
      ctx.moveTo(src.screenX, src.screenY);
      ctx.lineTo(tgt.screenX, tgt.screenY);

      if (isSevered) {
        ctx.strokeStyle = 'rgba(255, 0, 85, 0.35)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4, 4]);
      } else {
        const synCount = edge.synapses || 100;
        const alpha = Math.min(0.85, 0.2 + (synCount / 700));
        ctx.strokeStyle = `rgba(0, 240, 255, ${alpha})`;
        ctx.lineWidth = Math.max(1.2, Math.min(3.5, (synCount / 200)));
        ctx.setLineDash([]);
      }
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // 3. Draw Signal Pulse Particles
    for (const p of this.particles) {
      const isSevered = this.silencedNodeIds.has(String(p.sourceId)) || this.silencedNodeIds.has(String(p.targetId));
      if (isSevered) continue; // Don't animate through severed pathways

      const src = nodeMap.get(String(p.sourceId));
      const tgt = nodeMap.get(String(p.targetId));
      if (!src || !tgt) continue;

      p.progress += p.speed;
      if (p.progress > 1) p.progress = 0;

      const px = src.screenX + (tgt.screenX - src.screenX) * p.progress;
      const py = src.screenY + (tgt.screenY - src.screenY) * p.progress;

      ctx.beginPath();
      ctx.arc(px, py, 2.5 * src.scale, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = '#00f0ff';
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0; // reset
    }

    // 4. Draw Neurons (Nodes)
    for (const item of this.projectedNodes) {
      const n = item.raw;
      const isSilenced = this.silencedNodeIds.has(String(n.id));
      const isHovered = this.hoveredNode && String(this.hoveredNode.id) === String(n.id);
      const baseRadius = Math.max(5, 9 * item.scale);
      const radius = isHovered ? baseRadius * 1.35 : baseRadius;
      const color = this._getNodeColor(n);

      // Outer glow
      ctx.beginPath();
      ctx.arc(item.screenX, item.screenY, radius * 1.8, 0, Math.PI * 2);
      ctx.fillStyle = isSilenced ? 'rgba(255, 0, 85, 0.15)' : `${color}22`;
      ctx.fill();

      // Main sphere
      ctx.beginPath();
      ctx.arc(item.screenX, item.screenY, radius, 0, Math.PI * 2);
      const grad = ctx.createRadialGradient(
        item.screenX - radius * 0.3,
        item.screenY - radius * 0.3,
        radius * 0.1,
        item.screenX,
        item.screenY,
        radius
      );
      grad.addColorStop(0, '#ffffff');
      grad.addColorStop(0.4, color);
      grad.addColorStop(1, isSilenced ? '#500' : '#04101e');
      ctx.fillStyle = grad;
      ctx.shadowColor = color;
      ctx.shadowBlur = isHovered ? 18 : 8;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Label text
      ctx.font = `${Math.max(10, 11 * item.scale)}px Outfit, sans-serif`;
      ctx.fillStyle = isSilenced ? '#ff0055' : (isHovered ? '#ffffff' : '#cbd5e1');
      ctx.textAlign = 'center';
      ctx.fillText(n.name, item.screenX, item.screenY + radius + 12);
    }
  }

  toggleAutoRotate() {
    this.autoRotate = !this.autoRotate;
    return this.autoRotate;
  }

  resetView() {
    this.rotX = 0.35;
    this.rotY = 0.55;
    this.zoom = 1.3;
  }
}
