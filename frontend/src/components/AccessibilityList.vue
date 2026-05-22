<template>
  <div class="grid gap-3 sm:grid-cols-2">
    <div v-for="item in items" :key="item.key" class="rounded-lg border border-ink/10 bg-white p-4">
      <div class="flex items-center justify-between gap-2">
        <p class="font-black">{{ item.label }}</p>
        <span v-if="item.source" class="badge bg-clay/12 text-clay">{{ item.source }}</span>
      </div>
      <p class="mt-2 text-sm leading-6 text-ink/70">{{ item.display_value || item.value || "정보 없음" }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
});
</script>
