<template>
  <section v-if="spot" class="page-shell py-8">
    <div class="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div>
        <p class="text-sm font-black text-river">야외 운동시설</p>
        <h1 class="mt-1 text-4xl font-black">{{ spot.name }}</h1>
        <p class="mt-4 leading-7 text-ink/72">{{ spot.description }}</p>
        <div class="mt-5 flex flex-wrap gap-2">
          <span v-for="equipment in spot.equipment_types" :key="equipment" class="badge bg-river/10 text-river">{{ equipment }}</span>
        </div>
      </div>
      <div class="flex items-start justify-end gap-2">
        <button class="btn-secondary" type="button" @click="toggleBookmark"><Heart :size="18" />북마크</button>
        <RouterLink class="btn-primary" :to="{ path: '/reviews/new', query: { fitness_spot: spot.id } }"><PenLine :size="18" />후기</RouterLink>
      </div>
    </div>
    <div class="mt-8">
      <KakaoCourseMap :title="spot.name" :lat="spot.lat" :lng="spot.lng" marker-only />
    </div>
    <section class="mt-8">
      <h2 class="text-2xl font-black">후기</h2>
      <ReviewList class="mt-4" :reviews="reviews" />
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { Heart, PenLine } from "@lucide/vue";

import { api, unwrapList } from "../api/client";
import ReviewList from "../components/ReviewList.vue";
import KakaoCourseMap from "../components/maps/KakaoCourseMap.vue";

const props = defineProps({ id: { type: String, required: true } });
const spot = ref(null);
const reviews = ref([]);

async function load() {
  const [{ data: detail }, { data: reviewData }] = await Promise.all([
    api.get(`/fitness-spots/${props.id}/`),
    api.get("/reviews/", { params: { fitness_spot: props.id } }),
  ]);
  spot.value = detail;
  reviews.value = unwrapList(reviewData);
}

async function toggleBookmark() {
  if (!spot.value) return;
  if (spot.value.is_bookmarked) {
    await api.delete("/bookmarks/", { data: { fitness_spot: spot.value.id } });
    spot.value.is_bookmarked = false;
  } else {
    await api.post("/bookmarks/", { fitness_spot: spot.value.id });
    spot.value.is_bookmarked = true;
  }
}

onMounted(load);
</script>
