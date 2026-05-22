<template>
  <RouterLink :to="`/courses/${course.id}`" class="panel block h-full p-5 transition hover:-translate-y-1 hover:shadow-soft">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-sm font-bold text-moss">{{ course.category?.display_name }}</p>
        <h3 class="mt-1 text-lg font-black leading-snug">{{ course.name }}</h3>
      </div>
      <span class="badge bg-leaf/15 text-moss">{{ difficultyLabel }}</span>
    </div>
    <div class="mt-5 grid grid-cols-3 gap-2 text-sm">
      <div>
        <p class="text-ink/50">거리</p>
        <p class="font-black">{{ course.distance_km }}km</p>
      </div>
      <div>
        <p class="text-ink/50">시간</p>
        <p class="font-black">{{ course.duration_min }}분</p>
      </div>
      <div>
        <p class="text-ink/50">평점</p>
        <p class="font-black">★ {{ course.avg_rating || "0.0" }}</p>
      </div>
    </div>
    <p class="mt-4 flex items-center gap-1 text-sm text-ink/65"><MapPin :size="16" />{{ course.region }}</p>
  </RouterLink>
</template>

<script setup>
import { computed } from "vue";
import { MapPin } from "@lucide/vue";

const props = defineProps({
  course: { type: Object, required: true },
});

const difficultyLabel = computed(() => ({
  EASY: "쉬움",
  MEDIUM: "보통",
  HARD: "어려움",
}[props.course.difficulty] || props.course.difficulty));
</script>
