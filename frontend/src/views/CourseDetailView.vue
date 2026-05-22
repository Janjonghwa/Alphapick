<template>
  <section v-if="course" class="page-shell py-8">
    <div class="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
      <div>
        <p class="text-sm font-black text-moss">{{ course.category?.display_name }} · {{ course.region }}</p>
        <h1 class="mt-1 text-4xl font-black leading-tight">{{ course.name }}</h1>
        <p class="mt-4 leading-7 text-ink/72">{{ course.description }}</p>
        <div class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="panel p-4"><p class="text-sm text-ink/55">거리</p><p class="text-xl font-black">{{ course.distance_km }}km</p></div>
          <div class="panel p-4"><p class="text-sm text-ink/55">시간</p><p class="text-xl font-black">{{ course.duration_min }}분</p></div>
          <div class="panel p-4"><p class="text-sm text-ink/55">난이도</p><p class="text-xl font-black">{{ difficultyLabel }}</p></div>
          <div class="panel p-4"><p class="text-sm text-ink/55">평점</p><p class="text-xl font-black">★ {{ course.avg_rating }}</p></div>
        </div>
      </div>
      <div class="flex items-start justify-end gap-2">
        <button class="btn-secondary" type="button" @click="toggleBookmark"><Heart :size="18" />북마크</button>
        <RouterLink class="btn-primary" :to="{ path: '/reviews/new', query: { course: course.id } }"><PenLine :size="18" />후기</RouterLink>
      </div>
    </div>

    <div class="mt-8">
      <KakaoCourseMap :title="course.name" :lat="course.start_lat" :lng="course.start_lng" :path="course.gpx_simplified" />
    </div>

    <section class="mt-8">
      <h2 class="text-2xl font-black">오시는 길</h2>
      <AccessibilityList class="mt-4" :items="course.accessibility_info" />
    </section>

    <section class="mt-8">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-2xl font-black">이 코스와 비슷한 코스</h2>
      </div>
      <div class="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <CourseCard v-for="item in similar" :key="item.id" :course="item" />
      </div>
    </section>

    <section class="mt-8">
      <h2 class="text-2xl font-black">후기</h2>
      <ReviewList class="mt-4" :reviews="reviews" />
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { Heart, PenLine } from "@lucide/vue";

import { api, unwrapList } from "../api/client";
import AccessibilityList from "../components/AccessibilityList.vue";
import CourseCard from "../components/CourseCard.vue";
import ReviewList from "../components/ReviewList.vue";
import KakaoCourseMap from "../components/maps/KakaoCourseMap.vue";

const props = defineProps({ id: { type: String, required: true } });
const course = ref(null);
const similar = ref([]);
const reviews = ref([]);

const difficultyLabel = computed(() => ({
  EASY: "쉬움",
  MEDIUM: "보통",
  HARD: "어려움",
}[course.value?.difficulty] || course.value?.difficulty));

async function load() {
  const [{ data: detail }, { data: similarData }, { data: reviewData }] = await Promise.all([
    api.get(`/courses/${props.id}/`),
    api.get(`/courses/${props.id}/similar/`),
    api.get("/reviews/", { params: { course: props.id } }),
  ]);
  course.value = detail;
  similar.value = unwrapList(similarData);
  reviews.value = unwrapList(reviewData);
}

async function toggleBookmark() {
  if (!course.value) return;
  if (course.value.is_bookmarked) {
    await api.delete("/bookmarks/", { data: { course: course.value.id } });
    course.value.is_bookmarked = false;
  } else {
    await api.post("/bookmarks/", { course: course.value.id });
    course.value.is_bookmarked = true;
  }
}

onMounted(load);
</script>
