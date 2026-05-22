<template>
  <section class="page-shell py-8">
    <div class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="text-sm font-black text-moss">코스</p>
        <h1 class="text-3xl font-black">야외 운동 코스 탐색</h1>
      </div>
      <form class="grid gap-2 sm:grid-cols-4" @submit.prevent="load">
        <input v-model="filters.q" class="field" placeholder="지역명, 코스명" />
        <select v-model="filters.category" class="field">
          <option value="">전체</option>
          <option value="WALKING">러닝/걷기</option>
          <option value="HIKING">등산</option>
          <option value="CYCLING">자전거</option>
        </select>
        <select v-model="filters.difficulty" class="field">
          <option value="">난이도</option>
          <option value="EASY">쉬움</option>
          <option value="MEDIUM">보통</option>
          <option value="HARD">어려움</option>
        </select>
        <button class="btn-primary" type="submit"><Search :size="18" />검색</button>
      </form>
    </div>
    <div class="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <CourseCard v-for="course in courses" :key="course.id" :course="course" />
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { Search } from "@lucide/vue";

import { api, unwrapList } from "../api/client";
import CourseCard from "../components/CourseCard.vue";

const courses = ref([]);
const filters = reactive({ q: "", category: "", difficulty: "" });

async function load() {
  const { data } = await api.get("/courses/", { params: filters });
  courses.value = unwrapList(data);
}

onMounted(load);
</script>
