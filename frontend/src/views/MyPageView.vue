<template>
  <section class="page-shell py-8">
    <div class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <p class="text-sm font-black text-moss">마이페이지</p>
        <h1 class="text-3xl font-black">{{ auth.user?.nickname || auth.user?.username }}</h1>
        <p class="mt-2 text-ink/65">{{ auth.user?.preferred_location || "선호 지역 없음" }} · {{ auth.user?.level }}</p>
      </div>
      <RouterLink class="btn-primary" to="/profile/edit"><Settings :size="18" />프로필 수정</RouterLink>
    </div>
    <section class="mt-8">
      <h2 class="text-2xl font-black">북마크</h2>
      <div class="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <CourseCard v-for="item in courseBookmarks" :key="`c-${item.id}`" :course="item.course_detail" />
        <FitnessSpotCard v-for="item in spotBookmarks" :key="`s-${item.id}`" :spot="item.fitness_spot_detail" />
      </div>
    </section>
    <section class="mt-8">
      <h2 class="text-2xl font-black">운동 기록</h2>
      <div class="mt-4 space-y-3">
        <div v-for="record in records" :key="record.id" class="panel p-4">
          <p class="font-black">{{ record.course_detail?.name }}</p>
          <p class="mt-1 text-sm text-ink/65">{{ record.distance_km }}km · {{ record.duration_min }}분 · {{ new Date(record.started_at).toLocaleDateString() }}</p>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { Settings } from "@lucide/vue";

import { api, unwrapList } from "../api/client";
import CourseCard from "../components/CourseCard.vue";
import FitnessSpotCard from "../components/FitnessSpotCard.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const bookmarks = ref([]);
const records = ref([]);
const courseBookmarks = computed(() => bookmarks.value.filter((item) => item.course_detail));
const spotBookmarks = computed(() => bookmarks.value.filter((item) => item.fitness_spot_detail));

async function load() {
  await auth.fetchMe();
  const [{ data: bookmarkData }, { data: recordData }] = await Promise.all([
    api.get("/bookmarks/"),
    api.get("/workout-records/"),
  ]);
  bookmarks.value = unwrapList(bookmarkData);
  records.value = unwrapList(recordData);
}

onMounted(load);
</script>
