<template>
  <div
    class="p-4 rounded-lg shadow text-white font-bold text-center"
    :class="bgColor"
  >
    <h2 class="text-lg">{{ title }}</h2>
    <p class="text-4xl mt-2">{{ value }}</p>
  </div>
</template>

<script setup>
const props = defineProps({
  title: String,
  value: Number,
  color: String
});

const bgColor = {
  blue: "bg-blue-600",
  green: "bg-green-600",
  orange: "bg-orange-500",
  purple: "bg-purple-600"
}[props.color];
</script>
