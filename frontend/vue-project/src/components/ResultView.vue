<template>
  <div>
    <SectionCard title="Scores">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <ScoreCard label="SEO Score" :value="scores.seo_score" />
        <ScoreCard label="Technical Score" :value="scores.technical_score" />
        <ScoreCard label="Content Score" :value="scores.content_score" />
        <ScoreCard label="AEO Score" :value="scores.aeo_score" />
      </div>
    </SectionCard>

    <SectionCard title="On-Page SEO">
      <p><strong>Title:</strong> {{ onpage.title }}</p>
      <p><strong>Meta Description:</strong> {{ onpage.meta_description || 'Missing' }}</p>
      <p><strong>H1:</strong> {{ onpage.h1 }}</p>
      <p><strong>Schema Present:</strong> {{ onpage.schema_present }}</p>
    </SectionCard>

    <SectionCard title="Performance">
      <p><strong>Score:</strong> {{ performance.performance_score }}</p>

      <div v-if="performance.core_web_vitals">
        <p><strong>LCP:</strong> {{ performance.core_web_vitals.lcp }}</p>
        <p><strong>CLS:</strong> {{ performance.core_web_vitals.cls }}</p>
        <p><strong>FCP:</strong> {{ performance.core_web_vitals.fcp }}</p>
      </div>

      <p v-else>Core Web Vitals unavailable</p>
    </SectionCard>

    <SectionCard title="Content Insights (AI)">
      <p><strong>Intent Coverage:</strong> {{ content.intent_coverage }}</p>
      <p><strong>Readability Grade:</strong> {{ content.readability_grade }}</p>
      <p><strong>Expertise Score:</strong> {{ content.expertise_score }}</p>

      <p class="mt-3 font-semibold">Missing Sections:</p>
      <ul class="list-disc ml-5">
        <li v-for="m in content.missing_sections" :key="m">{{ m }}</li>
      </ul>
    </SectionCard>

    <SectionCard title="Recommendations">
      <ul class="list-disc ml-5">
        <li v-for="r in recommendations" :key="r">{{ r }}</li>
      </ul>
    </SectionCard>
  </div>
</template>

<script setup>
import SectionCard from "./SectionCard.vue";
import ScoreCard from "./ScoreCard.vue";

defineProps({
  onpage: Object,
  performance: Object,
  content: Object,
  scores: Object,
  recommendations: Array,
});
</script>
