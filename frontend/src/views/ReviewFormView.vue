<template>
  <section class="page-shell flex min-h-[calc(100vh-65px)] items-center justify-center py-8">
    <form class="panel w-full max-w-2xl p-6" @submit.prevent="submit">
      <h1 class="text-3xl font-black">후기 작성</h1>
      <label class="mt-6 block text-sm font-bold">별점
        <select v-model.number="form.rating" class="field mt-2">
          <option :value="5">5</option>
          <option :value="4">4</option>
          <option :value="3">3</option>
          <option :value="2">2</option>
          <option :value="1">1</option>
        </select>
      </label>
      <label class="mt-4 block text-sm font-bold">내용
        <textarea v-model="form.content" class="field mt-2 min-h-36" required />
      </label>
      <button class="btn-primary mt-6 w-full" type="submit">저장</button>
    </form>
  </section>
</template>

<script setup>
import { reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

import { api } from "../api/client";

const route = useRoute();
const router = useRouter();
const form = reactive({
  rating: 5,
  content: "",
});

async function submit() {
  const payload = { ...form };
  if (route.query.course) payload.course = Number(route.query.course);
  if (route.query.fitness_spot) payload.fitness_spot = Number(route.query.fitness_spot);
  await api.post("/reviews/", payload);
  router.push(route.query.course ? `/courses/${route.query.course}` : `/fitness-spots/${route.query.fitness_spot}`);
}
</script>
