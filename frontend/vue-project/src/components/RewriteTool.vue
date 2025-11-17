<script setup>
import { ref } from 'vue';

const content = ref("");
const tone = ref("friendly");
const keywords = ref("");
const variations = ref(2);
const result = ref(null);
const loading = ref(false);

async function runRewrite() {
  if (!content.value) return alert("Paste source content");
  loading.value = true;

  const payload = {
    content: content.value,
    target_keywords: keywords.value
      ? keywords.value.split(",").map(k => k.trim())
      : [],
    tone: tone.value,
    seo_focus: true,
    preserve_html: false,
    max_length: 800,
    variations: Number(variations.value)
  };

  const res = await fetch("http://127.0.0.1:8000/api/rewrite", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  result.value = await res.json();
  loading.value = false;
}
</script>

<template>
  <div class="rewrite-panel">
    <h2 class="panel-title">AI Rewrite Tool</h2>

    <textarea
      v-model="content"
      placeholder="Paste your paragraph / content..."
      class="rewrite-textarea"
    ></textarea>

    <input
      v-model="keywords"
      placeholder="comma separated keywords (optional)"
      class="rewrite-input"
    />

    <select v-model="tone" class="rewrite-select">
      <option>neutral</option>
      <option>friendly</option>
      <option>professional</option>
      <option>conversational</option>
    </select>

    <input
      type="number"
      v-model="variations"
      min="1"
      max="5"
      class="rewrite-input"
    />

    <button @click="runRewrite" class="rewrite-btn">
      {{ loading ? 'Rewriting…' : 'Rewrite' }}
    </button>

    <div v-if="result" class="rewrite-results">
      <h3>Results</h3>

      <div
        v-for="(v, i) in result.variants"
        :key="i"
        class="variant-card"
      >
        <h4>
          Variant {{ i + 1 }} —
          Coverage: {{ v.keywords_covered }} —
          Length: {{ v.length }}
        </h4>

        <div v-html="v.text" class="variant-text"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>


.rewrite-panel {
  margin-top: 20px;
  padding: 18px;
  border-radius: 12px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
}

.rewrite-textarea {
  width: 100%;
  max-width: 100%;  /* Add this */
  height: 140px;
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 10px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  color: #fff;
  box-sizing: border-box;  /* Add this */
}

.rewrite-input,
.rewrite-select {
  width: 100%;
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 10px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  color: #fff;
}

.rewrite-btn {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  background: linear-gradient(90deg,#0ea5e9,#7c3aed);
  border: none;
  font-weight: bold;
  color: white;
  margin-top: 10px;
}

.variant-card {
  padding: 14px;
  background: rgba(255,255,255,0.02);
  border-radius: 10px;
  margin-top: 14px;
}

.variant-text {
  margin-top: 6px;
  color: #dbeafe;
}
</style>
