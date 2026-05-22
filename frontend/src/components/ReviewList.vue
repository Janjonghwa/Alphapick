<template>
  <div class="space-y-3">
    <div v-for="review in reviews" :key="review.id" class="rounded-lg border border-ink/10 bg-white p-4">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <p class="font-black">{{ review.user_nickname }}</p>
        <p class="text-sm font-black text-clay">★ {{ review.rating }}</p>
      </div>
      <p class="mt-2 text-sm leading-6 text-ink/70">{{ review.content }}</p>
    </div>
    <p v-if="!reviews.length" class="rounded-lg border border-dashed border-ink/20 bg-white p-5 text-sm text-ink/60">아직 후기가 없습니다.</p>
  </div>
</template>

<script setup>
defineProps({
  reviews: { type: Array, default: () => [] },
});
</script>
