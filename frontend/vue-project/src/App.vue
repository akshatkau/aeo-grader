<template>
  <div class="app-root">
    <header class="topbar">
      <div class="brand">
        <img v-if="logoExists" :src="logo" alt="logo" class="logo" />
        <div v-else class="logo-fallback">AEO</div>
        <div class="brand-text">
          <h1>AEO Grader</h1>
          <p class="tagline">AI-driven SEO · Technical · Content insights</p>
        </div>
      </div>

      <div class="top-actions">
        <div class="powered">LLM: <strong>{{ llmName }}</strong></div>
      </div>
    </header>

    <main class="main-grid">
      <!-- Left column: form -->
      <section class="panel form-panel">
        <div class="panel-inner">
          <h2 class="panel-title">Run AEO Scan</h2>

          <form @submit.prevent="runScan" class="scan-form">
            <div v-for="(val, key) in form" :key="key" class="field">
              <label class="label">{{ formatLabel(key) }}</label>
              <input
                v-model="form[key]"
                :placeholder="`Enter ${formatLabel(key).toLowerCase()}`"
                class="input"
                :type="key === 'url' ? 'url' : 'text'"
                required="url" 
              />
            </div>

            <div class="controls">
              <button type="submit" class="btn primary" :disabled="loading">
                  <span v-if="!loading">Run Scan</span>
                  <span v-else class="spin">Analyzing…</span>
              </button>
              <button type="button" @click="downloadPdf" class="btn primary">Download PDF</button> 

              <button type="button" class="btn ghost" @click="reset" :disabled="loading">
                  Reset
              </button>
          </div>

            <p class="hint">
              Tip: fill company / location / industry to get richer, contextual results.
            </p>
          </form>
        </div>
      </section>

      <!-- Right column: results -->
      <section class="panel results-panel" v-if="result">
        <transition name="fade">
          <div class="results-inner" key="results">
            <div class="results-header">
              <div>
                <h3 class="results-title">{{ result.input_echo.company_name || 'Website Scan' }}</h3>
                <p class="muted">{{ result.input_echo.url }}</p>
              </div>
              <div class="results-meta">
                <div class="meta-item">
                  <div class="meta-label">AEO</div>
                  <div class="meta-value">{{ result.scores.aeo_score }}</div>
                </div>
                <div class="meta-item small">
                  <div class="meta-label">LLM</div>
                  <div class="meta-value small-text">{{ llmName }}</div>
                </div>
              </div>
            </div>

            <!-- Scores row -->
            <div class="score-row">
              <div class="score-card" v-for="card in scoreCards" :key="card.key">
                <div class="card-top">
                  <div class="card-title">{{ card.label }}</div>
                  <div :class="['card-score', scoreColorClass(card.value)]">{{ card.value }}</div>
                </div>
                <div class="card-sub">{{ card.subtitle }}</div>
              </div>
            </div>

            <div class="details-grid">
              <div class="detail-card">
                <h4>On-Page SEO</h4>
                <dl>
                  <template v-if="result.onpage">
                    <div><dt>Title</dt><dd>{{ result.onpage.title || '—' }}</dd></div>
                    <div><dt>H1</dt><dd>{{ result.onpage.h1 || '—' }}</dd></div>
                    <div><dt>Meta</dt><dd>{{ result.onpage.meta_description || 'Missing' }}</dd></div>
                    <div><dt>Schema</dt><dd>{{ result.onpage.schema_present ? 'Yes' : 'No' }}</dd></div>
                    <div><dt>Alt ratio</dt><dd>{{ formatAlt(result.onpage.images_with_alt_ratio) }}</dd></div>
                  </template>
                </dl>
              </div>

              <div class="detail-card">
                <h4>Performance</h4>
                <dl>
                  <div><dt>Score</dt><dd>{{ result.performance.performance_score ?? '—' }}</dd></div>
                  <div><dt>LCP</dt><dd>{{ formatSeconds(result.performance.core_web_vitals?.lcp) }}</dd></div>
                  <div><dt>CLS</dt><dd>{{ result.performance.core_web_vitals?.cls ?? '—' }}</dd></div>
                  <div><dt>FCP</dt><dd>{{ formatSeconds(result.performance.core_web_vitals?.fcp) }}</dd></div>
                </dl>
              </div>

              <div class="detail-card">
                <h4>Content Insights</h4>
                <dl>
                  <div><dt>Intent coverage</dt><dd>{{ pct(result.content.intent_coverage) }}</dd></div>
                  <div><dt>Readability</dt><dd>{{ result.content.readability_grade }}</dd></div>
                  <div><dt>E-E-A-T</dt><dd>{{ pct(result.content.expertise_score) }}</dd></div>
                </dl>

                <div class="tags">
                  <span v-for="m in result.content.missing_sections" :key="m" class="tag">
                    {{ m }}
                  </span>
                </div>
              </div>

              <div class="detail-card">
                <h4>Recommendations</h4>
                <ul class="recs">
                  <li v-for="r in result.recommendations" :key="r">{{ r }}</li>
                </ul>
              </div>
            </div>

            
          </div>
        </transition>
      </section>

      <!-- Placeholder results when empty -->
      <section class="panel results-panel placeholder" v-else>
        <div class="panel-inner placeholder-inner">
          <h3 class="placeholder-title">Results will appear here</h3>
          <p class="muted">Run a scan to see AEO score, technical metrics and content insights.</p>
          <div class="illustration" aria-hidden="true">
            <svg width="220" height="120" viewBox="0 0 220 120" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="2" y="10" width="216" height="98" rx="10" fill="#0f1724" stroke="#1f2937"/>
              <rect x="16" y="28" width="80" height="18" rx="4" fill="#071024"/>
              <rect x="16" y="54" width="180" height="10" rx="3" fill="#071024"/>
              <rect x="16" y="70" width="140" height="10" rx="3" fill="#071024"/>
            </svg>
          </div>
        </div>
      </section>
      <!-- Rewrite Tool - Full Width Below Grid -->

    <!-- Rewrite Tool - Full Width Below Grid -->
    <section class="rewrite-section" v-if="result">
      <RewriteTool />
    </section>
      <!-- Rewrite Tool - Full Width Below Grid -->
    </main>

    


    <!-- Toast for errors -->
    <div v-if="error" class="toast">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { analyzeWebsite } from './api/aeo';

// logo
import logoImg from './assets/logo.png?url';

import RewriteTool from "./components/RewriteTool.vue";


const logo = logoImg;
const logoExists = Boolean(logo);

// state
const loading = ref(false);
const error = ref('');
const result = ref(null);

const form = ref({
  url: '',
  company_name: '',
  location: '',
  product: '',
  industry: ''
});

const llmName = computed(() => {
  // fallback: check debug notes or use default
  if (result.value?.debug?.notes) {
    const s = result.value.debug.notes.toString();
    // try to extract a provider name
    if (/gpt[\w-]*/i.test(s)) return (s.match(/gpt[\w-]*/i) || [s])[0];
    return s.slice(0, 30);
  }
  return 'gpt-4o-mini';
});

function formatLabel(key) {
  return key.split('_').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' ');
}

function formatAlt(v) {
  if (v === null || v === undefined) return 'N/A';
  return (v * 100).toFixed(0) + '%';
}
function formatSeconds(ms) {
  if (!ms && ms !== 0) return '—';
  const s = Number(ms) / 1000;
  if (Number.isNaN(s)) return '—';
  return s.toFixed(2) + 's';
}
function pct(val) {
  if (val === null || val === undefined) return '—';
  return val + '%';
}

const scoreCards = computed(() => {
  const s = result.value?.scores || { aeo_score: 0, seo_score: 0, technical_score: 0, content_score: 0 };
  return [
    { key: 'aeo', label: 'AEO Score', value: s.aeo_score ?? 0, subtitle: 'Overall' },
    { key: 'seo', label: 'SEO', value: s.seo_score ?? 0, subtitle: 'On-page & metadata' },
    { key: 'tech', label: 'Technical', value: s.technical_score ?? 0, subtitle: 'Performance & CWV' },
    { key: 'content', label: 'Content', value: s.content_score ?? 0, subtitle: 'Intent & E-E-A-T' },
  ];
});

function scoreColorClass(score) {
  if (score >= 85) return 'good';
  if (score >= 60) return 'warn';
  return 'bad';
}

async function runScan() {
  error.value = '';
  if (!form.value.url) {
    error.value = 'Please enter a URL.';
    return;
  }

  loading.value = true;
  result.value = null;

  try {
    const res = await analyzeWebsite(form.value);
    result.value = res;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (e) {
    console.error(e);
    error.value = e?.message || 'Failed to analyze. See console.';
  } finally {
    loading.value = false;
    // clear toast after 4s
    setTimeout(() => (error.value = ''), 4000);
  }
}

async function downloadPdf() {
  if (!result.value) {
    alert("Run analysis first");
    return;
  }

  const res = await fetch("http://127.0.0.1:8000/api/report/pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(result.value)   // ✅ send analyzed data, NOT the input
  });

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "AEO_Report.pdf";
  a.click();

  window.URL.revokeObjectURL(url);
}




function reset() {
  form.value = { url: '', company_name: '', location: '', product: '', industry: '' };
  result.value = null;
}
</script>

<style scoped>

:global(#app) {
  width: 100vw !important;
  max-width: 100vw !important;
  margin: 0 !important;
  padding: 0 !important;
}



/* Basic page */
.app-root {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(180deg, #071022 0%, #051021 100%);
  color: #e6eef6;
  overflow-x: hidden;
}


/* Topbar */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;

  width: 100%;
  padding: 20px 40px;

  /* REMOVE max-width 1200px (causing centered layout + black left strip) */
  max-width: 100%;
  margin: 0;
  box-sizing: border-box;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
}
.logo {
  width: 52px;
  height: 52px;
  object-fit: contain;
  border-radius: 10px;
  background: linear-gradient(135deg,#0ea5e9,#7c3aed);
  padding: 6px;
  box-shadow: 0 6px 30px rgba(124,58,237,0.12);
}
.logo-fallback {
  width: 52px;
  height: 52px;
  display:flex;
  align-items:center;
  justify-content:center;
  border-radius:10px;
  background:linear-gradient(90deg,#0ea5e9,#7c3aed);
  font-weight:700;
  color:white;
  box-shadow: 0 6px 30px rgba(124,58,237,0.12);
}
.brand-text h1 { margin: 0; font-size: 18px; letter-spacing: -0.2px;}
.tagline { margin: 0; font-size: 12px; color:#9fb2c9; }

/* Main layout: two columns */
.main-grid {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 32px;

  width: 100vw !important;
  max-width: 100vw !important;
  grid-auto-rows: min-content;   /* ⭐ FIX: rows shrink to fit content */


  padding: 20px 40px;
  box-sizing: border-box;
  overflow: visible;
  align-items: start;
}




.panel {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.04);
  box-shadow: 0 8px 30px rgba(2,6,23,0.6);
}

/* Form panel */
.form-panel .panel-inner { padding: 22px;
width: 100%;
min-width: 380px; }
.panel-title { margin: 0 0 12px 0; font-size: 20px; }
.scan-form .field { margin-bottom: 12px; }
.label { display:block; color:#9fb2c9; font-size:12px; margin-bottom:6px; }
.input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.03);
  color: #e6eef6;
  outline: none;
  transition: box-shadow .15s ease, transform .12s ease;
}
.input:focus { box-shadow: 0 6px 20px rgba(14,165,233,0.08); transform: translateY(-1px); }

/* Buttons */
.controls { display:flex; gap: 10px; margin-top: 8px; }
.btn {
  padding: 10px 12px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight:600;
}
.btn.primary {
  background: linear-gradient(90deg,#0ea5e9,#7c3aed);
  color: #fff;
  box-shadow: 0 8px 30px rgba(124,58,237,0.12);
}
.btn.ghost {
  background: transparent;
  color: #9fb2c9;
  border: 1px solid rgba(255,255,255,0.04);
}

/* Results panel */
.results-panel {
  width: 100%;
  min-width: 0;     /* FIX grid overflow cutting */
  overflow: visible;
  height: auto;
}

.results-inner { padding: 18px; }
.results-header {
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom: 14px;
}
.results-title { margin:0; font-size:18px; }
.muted { color: #93a7bf; font-size: 13px; margin:0; }

.results-meta { display:flex; gap: 12px; align-items:center; }
.meta-item { text-align:right; }
.meta-label { font-size:12px; color:#93a7bf; }
.meta-value { font-weight:700; font-size:18px; color:#e6eef6; }
.small-text { font-size:12px; color:#9fb2c9; }

/* Score row */
.score-row { display:flex; gap: 12px; margin-bottom: 16px; }
.score-card {
  flex:1;
  background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005));
  border-radius: 10px;
  padding: 12px;
  border: 1px solid rgba(255,255,255,0.03);
}
.card-top { display:flex; justify-content:space-between; align-items:center; }
.card-title { color:#9fb2c9; font-size:13px; }
.card-score { font-weight:800; font-size:22px; }
.card-sub { color:#8fa7bf; font-size:12px; margin-top:6px; }

/* color classes */
.good { color: #34d399; }
.warn { color: #f59e0b; }
.bad  { color: #fb7185; }

/* details grid */
.details-grid {
  display:grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 8px;
}
.detail-card { padding: 12px; border-radius: 10px; background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.03); }
.detail-card h4 { margin:0 0 8px 0; color:#e6eef6; }
.detail-card dl { margin:0; }
.detail-card dt { font-size:12px; color:#9fb2c9; float:left; width:120px; }
.detail-card dd { margin:0 0 8px 130px; color:#cfe3f2; }

/* tags */
.tags { margin-top: 10px; display:flex; gap:8px; flex-wrap:wrap; }
.tag { background: rgba(236,72,153,0.08); color:#ff9ec7; padding:6px 10px; border-radius:999px; font-size:12px; }

/* recs */
.recs { margin:0; padding-left: 18px; color:#d6e8f6; }
.recs li { margin-bottom:8px; }

/* placeholder */
.placeholder { display:flex; align-items:center; justify-content:center; min-height: 300px; }
.placeholder-inner { text-align:center; padding: 24px; }
.placeholder-title { margin:0; font-size:18px; color:#cfe3f2; }

/* small toast */
.toast { position: fixed; left: 50%; transform: translateX(-50%); bottom: 18px; background: #ff5d6c; color: white; padding: 8px 14px; border-radius: 8px; font-weight:600; box-shadow: 0 6px 22px rgba(0,0,0,0.6); }

/* transitions */
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease, transform .25s ease; }
.fade-enter-from { opacity: 0; transform: translateY(6px); }
.fade-enter-to { opacity: 1; transform: translateY(0); }
.fade-leave-to { opacity: 0; transform: translateY(6px); }

/* responsive */
@media (max-width: 980px) {
  .main-grid { grid-template-columns: 1fr; padding: 0 12px; }
  .score-row { flex-direction: column; }
  .details-grid { grid-template-columns: 1fr; }
}
/* Rewrite section - full width */
.rewrite-section {
  width: 100%;
  max-width: 100%;  /* Change from 100vw */
  padding: 0 40px 40px 40px;
  box-sizing: border-box;
  overflow: visible;  /* Add this */
}

@media (max-width: 980px) {
  .rewrite-section {
    padding: 0 12px 20px 12px;
  }
}
</style>


<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #071022 0%, #051021 100%);
  overflow-x: hidden;
  overflow-y: auto;
}

/* Fix layout cutting issue */
.main-grid {
  align-items: start !important;
}

.results-panel {
  height: auto !important;
  overflow: visible !important;
}

.panel {
  height: auto !important;
}

.rewrite-panel-full {
  grid-column: 1 / -1;  /* span both grid columns */
  width: 100%;
  margin-top: 0;
  padding: 0;
}


</style>
