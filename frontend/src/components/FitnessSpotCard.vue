<template>
  <RouterLink :to="`/fitness-spots/${spot.id}`" class="panel block h-full p-5 transition hover:-translate-y-1 hover:shadow-soft">
    <p class="text-sm font-bold text-river">야외 운동시설</p>
    <h3 class="mt-1 text-lg font-black leading-snug">{{ spot.name }}</h3>
    <p class="mt-3 min-h-10 text-sm text-ink/65">{{ spot.address || "주소 정보 없음" }}</p>
    <div class="mt-4 flex flex-wrap gap-2">
      <span v-for="equipment in spot.equipment_types" :key="equipment" class="badge bg-river/10 text-river">{{ equipment }}</span>
    </div>
    <p class="mt-4 text-sm font-bold">★ {{ spot.avg_rating || "0.0" }} · 후기 {{ spot.review_count || 0 }}</p>
  </RouterLink>
</template>

<script setup>
defineProps({
  spot: { type: Object, required: true },
});
</script>
