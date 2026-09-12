/**
 * ReportViewer.js
 * Renders publication-grade markdown research report into beautiful styled HTML.
 */

export class ReportViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.currentMarkdown = '';
  }

  render(markdownText) {
    this.currentMarkdown = markdownText || '';
    if (!this.currentMarkdown.trim()) {
      this.container.innerHTML = `
        <div style="color: #64748b; text-align: center; padding: 40px 0;">
          Run a query above to generate an autonomous scientific discovery report.
        </div>
      `;
      return;
    }

    this.container.innerHTML = this._parseMarkdown(this.currentMarkdown);
  }

  getMarkdown() {
    return this.currentMarkdown;
  }

  _parseMarkdown(md) {
    // Lightweight, fast markdown parser tailored for research reports
    const lines = md.split('\n');
    let html = '';
    let inTable = false;
    let tableHeaderDone = false;

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();

      // Horizontal rules
      if (line === '---' || line === '***') {
        html += '<hr style="border:none; border-top:1px solid rgba(255,255,255,0.1); margin:16px 0;"/>';
        continue;
      }

      // Tables
      if (line.startsWith('|') && line.endsWith('|')) {
        if (!inTable) {
          inTable = true;
          tableHeaderDone = false;
          html += '<table>';
        }
        if (line.includes('---')) {
          tableHeaderDone = true;
          continue; // separator row
        }
        const cells = line.split('|').slice(1, -1).map(c => c.trim());
        const tag = tableHeaderDone ? 'td' : 'th';
        html += '<tr>' + cells.map(c => `<${tag}>${this._formatInline(c)}</${tag}>`).join('') + '</tr>';
        continue;
      } else if (inTable) {
        inTable = false;
        html += '</table>';
      }

      // Headers
      if (line.startsWith('# ')) {
        html += `<h1>${this._formatInline(line.slice(2))}</h1>`;
      } else if (line.startsWith('## ')) {
        html += `<h2>${this._formatInline(line.slice(3))}</h2>`;
      } else if (line.startsWith('### ')) {
        html += `<h3>${this._formatInline(line.slice(4))}</h3>`;
      }
      // Blockquotes
      else if (line.startsWith('> ')) {
        html += `<blockquote>${this._formatInline(line.slice(2))}</blockquote>`;
      }
      // Bullet points
      else if (line.startsWith('- ')) {
        html += `<ul><li>${this._formatInline(line.slice(2))}</li></ul>`;
      } else if (line.match(/^\d+\.\s/)) {
        const text = line.replace(/^\d+\.\s/, '');
        html += `<ol><li>${this._formatInline(text)}</li></ol>`;
      }
      // Paragraphs
      else if (line.length > 0) {
        html += `<p>${this._formatInline(line)}</p>`;
      }
    }

    if (inTable) {
      html += '</table>';
    }

    // Clean up consecutive <ul> and <ol> tags
    html = html.replace(/<\/ul>\s*<ul>/g, '');
    html = html.replace(/<\/ol>\s*<ol>/g, '');

    return html;
  }

  _formatInline(text) {
    let res = text;
    // Code blocks `code`
    res = res.replace(/`([^`]+)`/g, '<code style="background:rgba(0,240,255,0.1); color:#00f0ff; padding:2px 6px; border-radius:4px; font-family:var(--font-mono);">$1</code>');
    // Bold **bold**
    res = res.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Italic *italic*
    res = res.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    // Links [text](url)
    res = res.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    return res;
  }
}
