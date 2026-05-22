<template>
  <section class="page-shell py-8">
    <form class="panel flex flex-col gap-3 p-4 md:flex-row" @submit.prevent="search">
      <input v-model="q" class="field" placeholder="코스명, 지역명, 시설명" />
      <button class="btn-primary" type="submit"><Search :size="18" />검색</button>
    </form>
    <div class="mt-8">
      <h1 class="text-3xl font-black">검색 결과</h1>
      <h2 class="mt-6 text-xl font-black">코스</h2>
      <div class="mt-3 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <CourseCard v-for="course in courses" :key="course.id" :course="course" />
      </div>
      <h2 class="mt-8 text-xl font-black">시설</h2>
      <div class="mt-3 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <FitnessSpotCard v-for="spot in spots" :key="spot.id" :spot="spot" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Search } from "@lucide/vue";

import { api, unwrapList } from "../api/client";
import CourseCard from "../components/CourseCard.vue";
import FitnessSpotCard from "../components/FitnessSpotCard.vue";

const route = useRoute();
const router = useRouter();
const q = ref(route.query.q || "");
const courses = ref([]);
const spots = ref([]);

async function search() {
  router.replace({ path: "/search", query: { q: q.value } });
  const [{ data: courseData }, { data: spotData }] = await Promise.all([
    api.get("/courses/", { params: { q: q.value } }),
    api.get("/fitness-spots/", { params: { q: q.value } }),
  ]);
  courses.value = unwrapList(courseData);
  spots.value = unwrapList(spotData);
}

onMounted(search);
</script>
