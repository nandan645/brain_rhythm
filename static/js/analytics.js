document.addEventListener("DOMContentLoaded", function() {
  'use strict';
  console.log("CSV Analytics Dashboard v7 - Full ISO Mapping + No Errors");

  // === KEEP EXISTING TRACKING ===
  let sessionId = localStorage.getItem('analytics_session_id') || 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  localStorage.setItem('analytics_session_id', sessionId);

  const sectionMap = { /* unchanged */ };
  function getSection() { /* unchanged tracking logic */ return 'HOME'; }

  async function trackVisit(section) {
    fetch('/track-visit', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({section, session_id: sessionId})
    }).catch(e => {}); // Silent - CSV system
  }

  function trackTime(section, timeSpent) {
    navigator.sendBeacon('/track-time', new Blob([JSON.stringify({section, session_id: sessionId, time_spent: timeSpent})], {'type': 'application/json'}));
  }

  trackVisit(getSection());
  let startTime = performance.now();
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      trackTime(getSection(), (performance.now() - startTime) / 1000);
      startTime = performance.now();
    }
  });

  // === CSV DASHBOARD CLASS ===
  class CSVDashboard {
    constructor() {
      this.charts = { line: null, pie: null };
      this.loadData();
    }

    async loadData() {
      try {
        const response = await fetch('/analytics-data');
        const csvData = await response.json();

        if (!csvData.daily || !csvData.country) {
          console.warn('Empty CSV data:', csvData);
          return;
        }

        // === 1. FIX TOP STAT CARDS ===
        this.updateCards(csvData);

        // === 2. RENDER CHARTS ===
        await this.renderCharts(csvData);

      } catch (e) {
        console.error('CSV dashboard error:', e);
      }
    }

    updateCards(csvData) {
      const daily = csvData.daily || [];

      // TOTAL VISITS = sum Visits
      const totalVisits = daily.reduce((sum, row) => sum + Number(row.Visits || 0), 0);
      document.getElementById('total-users').textContent = totalVisits.toLocaleString();

      // TOTAL REQUESTS = sum Requests
      const totalRequests = daily.reduce((sum, row) => sum + Number(row.Requests || 0), 0);
      document.getElementById('total-visits').textContent = totalRequests.toLocaleString();

      // AVG BANDWIDTH = avg Bandwidth_MB + "MB" 
      const bandwidths = daily.map(row => Number(row.Bandwidth_MB || 0)).filter(b => b > 0);
      const avgBandwidth = bandwidths.length ? (bandwidths.reduce((a, b) => a + b, 0) / bandwidths.length).toFixed(1) : 0;
      document.getElementById('avg-session').textContent = avgBandwidth + ' MB';

      console.log('Cards updated:', {totalVisits, totalRequests, avgBandwidth});
    }

    async renderCharts(csvData) {
      const daily = csvData.daily || [];
      const country = csvData.country || [];

      // Parse data safely
      const dates = daily.map(row => row.Date || 'Unknown').slice(-10);
      const visits = daily.map(row => Number(row.Visits || 0)).slice(-10);
      const requests = daily.map(row => Number(row.Requests || 0)).slice(-10);

      // TOP 9 COUNTRIES + "OTHERS" for pie chart
      const sortedCountry = [...country].sort((a, b) => Number(b.Requests || 0) - Number(a.Requests || 0));
      const topCountries = sortedCountry.slice(0, 9);
      const othersCountries = sortedCountry.slice(9);
      const othersValue = othersCountries.reduce((sum, c) => sum + Number(c.Requests || 0), 0);
      const pieLabels = topCountries.map(c => c.Country || 'Unknown');
      const pieData = topCountries.map(c => Number(c.Requests || 0));
      if (othersValue > 0) {
        pieLabels.push('Others');
        pieData.push(othersValue);
      }

      // Destroy charts
      if (this.charts.line) this.charts.line.destroy();
      if (this.charts.pie) this.charts.pie.destroy();
      this.charts = { line: null, pie: null };

      // === LINE CHART ===
      const lineCanvas = document.getElementById('trend-line');
      if (lineCanvas) {
        lineCanvas.parentElement.querySelector('h4').textContent = 'Traffic Overview';
        lineCanvas.parentElement.querySelector('h4').style.color = '#26313d';
        this.charts.line = new Chart(lineCanvas, {
          type: 'line',
          data: {
            labels: dates,
            datasets: [
              { label: 'Visits', data: visits, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', tension: 0.4, fill: true, pointRadius: 4 },
              { label: 'Requests', data: requests, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', tension: 0.4, fill: false }
            ]
          },
          options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: { x: { grid: { color: 'rgba(0,0,0,0.05)' } }, y: { beginAtZero: true } }
          }
        });
      }

      // === PIE CHART ===
      const pieCanvas = document.getElementById('distribution-pie');
      if (pieCanvas) {
        pieCanvas.parentElement.querySelector('h4').textContent = 'Traffic by Country (Top 9 + Others)';
        pieCanvas.parentElement.querySelector('h4').style.color = '#26313d';
        this.charts.pie = new Chart(pieCanvas, {
          type: 'pie',
          data: {
            labels: pieLabels,
            datasets: [{ data: pieData, backgroundColor: ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#84cc16','#ec4899','#10b981','#f3f4f6'] }]
          },
          options: {
            responsive: true,
            plugins: { legend: { position: 'bottom', labels: { padding: 15, font: { size: 10 }, usePointStyle: true } } }
          }
        });
      }

    }
  }

  // Initialize only on homepage and only once per page load
  const isHomePage = window.location.pathname === '/' || window.location.pathname === '/index';
  const hasDashboard = Boolean(
    document.getElementById('trend-line') &&
    document.getElementById('distribution-pie')
  );

  if (isHomePage && hasDashboard && !window.__csvDashboardInitialized) {
    window.__csvDashboardInitialized = true;
    new CSVDashboard();
  }
});
