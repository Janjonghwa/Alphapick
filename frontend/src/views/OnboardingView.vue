<template>
  <section class="page-shell py-8">
    <form class="panel mx-auto max-w-3xl p-6" @submit.prevent="submit">
      <p class="text-sm font-black text-moss">온보딩</p>
      <h1 class="mt-1 text-3xl font-black">처음 추천 기준을 정해요</h1>
      <div class="mt-6 grid gap-5">
        <label class="block text-sm font-bold">운동 레벨
          <select v-model="form.level" class="field mt-2">
            <option value="EASY">쉬움</option>
            <option value="MEDIUM">보통</option>
            <option value="HARD">어려움</option>
          </select>
        </label>
        <label class="block text-sm font-bold">선호 지역
          <input v-model="form.preferred_location" class="field mt-2" placeholder="예: 서울, 성동구, 부산" />
        </label>
        <div>
          <p class="text-sm font-bold">관심 운동</p>
          <div class="mt-3 grid gap-2 sm:grid-cols-2">
            <label v-for="category in categories" :key="category.value" class="flex items-center gap-3 rounded-lg border border-ink/10 bg-white p-4 font-bold">
              <input v-model="form.preferred_categories" type="checkbox" :value="category.value" />
              {{ category.label }}
            </label>
          </div>
        </div>
      </div>
      <button class="btn-primary mt-6 w-full" type="submit">저장</button>
    </form>
  </section>
</template>

<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const categories = [
  { value: "WALKING", label: "러닝/걷기" },
  { value: "HIKING", label: "등산" },
  { value: "CYCLING", label: "자전거" },
  { value: "FITNESS_SPOT", label: "야외 운동시설" },
];
const form = reactive({
  level: auth.user?.level || "EASY",
  preferred_location: auth.user?.preferred_location || "",
  preferred_categories: auth.user?.preferred_categories || ["WALKING"],
  onboarding_completed: true,
});

async function submit() {
  await auth.updateMe(form);
  router.push("/dashboard");
}
</script>
