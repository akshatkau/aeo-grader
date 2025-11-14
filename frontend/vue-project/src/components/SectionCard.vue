<template>
  <div class="bg-white p-6 rounded-lg shadow">
    <h2 class="text-2xl font-semibold mb-3">{{ title }}</h2>
    <div><slot /></div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: String
});
</script>
