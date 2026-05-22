<template>
  <section class="page-shell py-8">
    <div class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <p class="text-sm font-black text-moss">추천</p>
        <h1 class="text-3xl font-black">오늘 밖에서 움직일 곳</h1>
      </div>
      <button class="btn-secondary" type="button" @click="loadNearby"><MapPin :size="18" />내 주변 추천</button>
    </div>

    <div class="mt-6 grid gap-4 md:grid-cols-3">
      <CourseCard v-for="course in courses" :key="course.id" :course="course" />
    </div>
    <p v-if="!loading && !courses.length" class="mt-6 rounded-lg border border-dashed border-ink/20 bg-white p-6 text-ink/60">추천할 코스가 없습니다. 데모 데이터를 먼저 적재해 주세요.</p>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { MapPin } from "@lucide/vue";

import { api, unwrapList } from "../api/client";
import CourseCard from "../components/CourseCard.vue";

const courses = ref([]);
const loading = ref(false);

async function loadPersonalized() {
  loading.value = true;
  const { data } = await api.get("/recommendations/personalized/");
  courses.value = unwrapList(data);
  loading.value = false;
}

async function loadNearby() {
  if (!navigator.geolocation) {
    await loadPersonalized();
    return;
  }
  loading.value = true;
  navigator.geolocation.getCurrentPosition(async ({ coords }) => {
    const { data } = await api.get("/recommendations/nearby/", {
      params: { lat: coords.latitude, lng: coords.longitude, radius_km: 10 },
    });
    courses.value = unwrapList(data);
    loading.value = false;
  }, async () => {
    await loadPersonalized();
  });
}

onMounted(loadPersonalized);
</script>
