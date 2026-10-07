/*
Menampilkan tabel/grafik frekuensi, IC, dan estimasi brute force dari Python.
Grafik dibuat dengan elemen HTML/CSS; tidak memakai library grafik atau kriptografi.
*/


const $ = id => document.getElementById(id);
let current = null, revision = 0, mainBusy = false, estimating = false;

function lock() {
  for (const element of $('estimate-form').querySelectorAll('input, button')) {
    element.disabled = mainBusy || estimating || !current;
  }
}
export function setAnalysisBusy(value) { mainBusy = value; lock(); }

export function clearAnalysis() {
  current = null; revision++; estimating = false;
  $('frequency-body').replaceChildren(); $('frequency-table').hidden = true;
  $('frequency-info').textContent = 'Analisis muncul setelah catatan dienkripsi atau dibuka kembali.';
  $('analysis-content').hidden = true; $('frequency-chart').replaceChildren();
  $('estimate-form').reset(); $('estimate-result').hidden = true;
  $('estimate-error').hidden = true; $('estimate-error').textContent = '';
  for (const id of ['ic-before', 'ic-after', 'ic-before-count', 'ic-after-count',
                    'estimate-length', 'estimate-space', 'estimate-attempts',
                    'estimate-probability', 'estimate-average', 'estimate-full']) $(id).textContent = '';
  lock();
}

function table() {
  if (!current) return;
  const selected = $('frequency-stage').value;
  const data = current[selected];
  $('frequency-body').replaceChildren();
  for (const item of data.rows) {
    const row = document.createElement('tr'); row.className = 'border-b border-zinc-100';
    for (const value of [item.letter, item.count, item.percent.toFixed(2) + '%']) {
      const cell = document.createElement('td'); cell.className = 'py-2'; cell.textContent = value; row.append(cell);
    }
    $('frequency-body').append(row);
  }
  const label = selected === 'after' ? 'sesudah encode' : 'sebelum encode';
  $('frequency-info').textContent = 'Total huruf A–Z (' + label + '): ' + data.total;
  $('frequency-table').hidden = false;
}

function chart() {
  const byLetter = data => Object.fromEntries(data.rows.map(row => [row.letter, row]));
  const before = byLetter(current.before), after = byLetter(current.after);
  $('frequency-chart').replaceChildren();
  for (const letter of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') {
    const row = document.createElement('div'); row.className = 'frequency-chart-row';
    const label = document.createElement('span'); label.textContent = letter; row.append(label);
    const tracks = document.createElement('div'); tracks.className = 'frequency-chart-tracks';
    for (const [stage, data] of [['before', before[letter]], ['after', after[letter]]]) {
      const track = document.createElement('div'); track.className = 'frequency-chart-track';
      const bar = document.createElement('div'); bar.className = 'frequency-chart-bar ' + stage;
      bar.style.width = data.percent + '%';
      track.append(bar); tracks.append(track);
    }
    row.append(tracks);
    const values = document.createElement('span'); values.className = 'frequency-chart-values';
    values.textContent = before[letter].percent.toFixed(2) + '% / ' + after[letter].percent.toFixed(2) + '%';
    row.append(values);
    row.title = letter + ': sebelum ' + before[letter].count + ' huruf; sesudah ' + after[letter].count + ' huruf';
    row.setAttribute('aria-label', letter + ': sebelum ' + before[letter].percent + '%, sesudah ' + after[letter].percent + '%');
    $('frequency-chart').append(row);
  }
}

function countLabel(value, exact = true) {
  return exact ? BigInt(value).toLocaleString('id-ID') : '≈ ' + value;
}
function showEstimate(data) {
  $('estimate-space').textContent = countLabel(data.key_space, data.key_space_exact);
  $('estimate-attempts').textContent = countLabel(data.attempts);
  $('estimate-probability').textContent = data.probability;
  $('estimate-average').textContent = data.average_time;
  $('estimate-full').textContent = data.full_time;
  $('estimate-result').hidden = false;
}

export function renderAnalysis(data) {
  current = data; revision++; estimating = false;
  $('analysis-content').hidden = false; $('frequency-stage').value = 'after';
  $('estimate-form').reset(); $('estimate-error').hidden = true;
  for (const stage of ['before', 'after']) {
    const item = data[stage];
    $('ic-' + stage).textContent = item.ic === null ? 'Data belum cukup' : item.ic.toFixed(4);
    $('ic-' + stage + '-count').textContent = item.total + ' huruf A–Z';
  }
  $('estimate-length').textContent = data.vigenere_length + ' huruf';
  table(); chart(); showEstimate(data.estimate); lock();
}

export function initAnalysis(request) {
  $('frequency-stage').addEventListener('change', table);
  $('estimate-form').addEventListener('submit', async event => {
    event.preventDefault(); if (!current || mainBusy || estimating) return;
    const snapshot = revision;
    const rate = Number($('estimate-rate').value), seconds = Number($('estimate-seconds').value);
    $('estimate-error').hidden = true; $('estimate-result').hidden = true;
    if (!Number.isInteger(rate) || !Number.isInteger(seconds) || rate < 1 || seconds < 1 || rate > 1e12 || seconds > 1e12) {
      $('estimate-error').textContent = 'Kecepatan dan durasi harus bilangan bulat 1 sampai 1.000.000.000.000.';
      $('estimate-error').hidden = false; return;
    }
    estimating = true; lock();
    try {
      const result = await request('analysis', {length: current.vigenere_length, rate, seconds});
      if (snapshot === revision) showEstimate(result);
    } catch (error) {
      if (snapshot === revision) { $('estimate-error').textContent = error.message; $('estimate-error').hidden = false; }
    } finally { if (snapshot === revision) { estimating = false; lock(); } }
  });
}
