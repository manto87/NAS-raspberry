'use strict';

let weatherChart = null;

const fmtBytes = b => {
  const u = ['B','KB','MB','GB','TB'];
  let i = 0;
  while (b >= 1024 && i < u.length - 1) { b /= 1024; i++; }
  return `${b.toFixed(1)} ${u[i]}`;
};

const pctColor = p => p > 90 ? 'danger' : p > 70 ? 'warning' : 'success';

async function refreshNas() {
  try {
    const d = await fetch('/api/nas/status').then(r => r.json());

    document.getElementById('cpu-pct').textContent  = `${d.system.cpu_percent}%`;
    document.getElementById('mem-pct').textContent  = `${d.system.memory.percent}%`;
    document.getElementById('cpu-temp').textContent = d.system.temperature ? `${d.system.temperature}°C` : '—';

    const smb = document.getElementById('samba-badge');
    smb.textContent  = d.samba.running ? 'smbd running' : 'smbd stopped';
    smb.className    = 'badge ' + (d.samba.running ? 'bg-success' : 'bg-danger');

    const box = document.getElementById('nas-disks');
    if (!d.disks.length) {
      box.innerHTML = '<span class="text-secondary small">Share paths not found — check config.yaml.</span>';
      return;
    }
    box.innerHTML = d.disks.map(dk => `
      <div class="mb-3">
        <div class="d-flex justify-content-between small mb-1">
          <span>${dk.path}</span>
          <span class="text-secondary">${fmtBytes(dk.used)} / ${fmtBytes(dk.total)}</span>
        </div>
        <div class="progress">
          <div class="progress-bar bg-${pctColor(dk.percent)}" style="width:${dk.percent}%"></div>
        </div>
      </div>`).join('');
  } catch {
    document.getElementById('nas-disks').innerHTML = '<span class="text-danger small">Failed to load NAS status.</span>';
  }
}

async function refreshWeather() {
  try {
    const [cur, hist] = await Promise.all([
      fetch('/api/weather/current').then(r => r.json()),
      fetch('/api/weather/history?hours=6').then(r => r.json()),
    ]);

    if (cur && cur.temperature != null) {
      document.getElementById('wx-temp').textContent = `${cur.temperature}°C`;
      document.getElementById('wx-hum').textContent  = `${cur.humidity}%`;
      document.getElementById('wx-pres').textContent = cur.pressure ? `${cur.pressure} hPa` : '—';
    }

    if (hist.length > 1) {
      const labels = hist.map(r => {
        const d = new Date(r.timestamp);
        return `${d.getHours()}:${String(d.getMinutes()).padStart(2,'0')}`;
      });
      const temps = hist.map(r => r.temperature);
      const hums  = hist.map(r => r.humidity);

      const chartCfg = {
        type: 'line',
        data: {
          labels,
          datasets: [
            { label: 'Temp (°C)',    data: temps, borderColor: '#ffc107', backgroundColor: 'rgba(255,193,7,.08)',  tension: .4, pointRadius: 0, yAxisID: 'y'  },
            { label: 'Humidity (%)', data: hums,  borderColor: '#0dcaf0', backgroundColor: 'rgba(13,202,240,.08)', tension: .4, pointRadius: 0, yAxisID: 'y1' },
          ],
        },
        options: {
          animation: false,
          plugins: { legend: { labels: { color: '#adb5bd', font: { size: 11 } } } },
          scales: {
            x:  { ticks: { color: '#6c757d', maxTicksLimit: 8, font: { size: 10 } }, grid: { color: '#2c3138' } },
            y:  { ticks: { color: '#ffc107', font: { size: 10 } }, grid: { color: '#2c3138' }, position: 'left'  },
            y1: { ticks: { color: '#0dcaf0', font: { size: 10 } }, grid: { display: false },   position: 'right' },
          },
        },
      };

      if (!weatherChart) {
        weatherChart = new Chart(document.getElementById('weather-chart').getContext('2d'), chartCfg);
      } else {
        weatherChart.data.labels = labels;
        weatherChart.data.datasets[0].data = temps;
        weatherChart.data.datasets[1].data = hums;
        weatherChart.update('none');
      }
    }
  } catch (e) {
    console.error('Weather fetch failed:', e);
  }
}

async function refreshIrrigation() {
  try {
    const d = await fetch('/api/irrigation/status').then(r => r.json());
    const badge = document.getElementById('irrigation-badge');
    const box   = document.getElementById('irrigation-zones');

    if (!d.enabled) return;

    badge.textContent = 'enabled';
    badge.className   = 'badge bg-success';

    box.innerHTML = d.zones.map(z => `
      <div class="zone-row">
        <div>
          <span class="fw-semibold">${z.name}</span>
          <span class="ms-2 badge ${z.active ? 'bg-success' : 'bg-secondary'}">${z.active ? 'ON' : 'OFF'}</span>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-success" onclick="zoneOn(${z.id})"  ${z.active  ? 'disabled' : ''}>On</button>
          <button class="btn btn-sm btn-outline-danger"  onclick="zoneOff(${z.id})" ${!z.active ? 'disabled' : ''}>Off</button>
        </div>
      </div>`).join('');
  } catch (e) {
    console.error('Irrigation fetch failed:', e);
  }
}

async function zoneOn(id) {
  await fetch(`/api/irrigation/zone/${id}/on`, { method: 'POST' });
  refreshIrrigation();
}

async function zoneOff(id) {
  await fetch(`/api/irrigation/zone/${id}/off`, { method: 'POST' });
  refreshIrrigation();
}

function refreshAll() {
  refreshNas();
  refreshWeather();
  refreshIrrigation();
  document.getElementById('last-updated').textContent = 'Updated: ' + new Date().toLocaleTimeString();
}

document.addEventListener('DOMContentLoaded', () => {
  refreshAll();
  setInterval(refreshAll, 30_000);
});
