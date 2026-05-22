<template>
  <section class="page-shell py-8">
    <div class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <p class="text-sm font-black text-river">시설</p>
        <h1 class="text-3xl font-black">야외 운동시설</h1>
      </div>
      <form class="flex gap-2" @submit.prevent="load">
        <input v-model="q" class="field" placeholder="시설명, 주소, 기구" />
        <button class="btn-primary" type="submit"><Search :size="18" />검색</button>
      </form>
    </div>
    <div class="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <FitnessSpotCard v-for="spot in spots" :key="spot.id" :spot="spot" />
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { Search } from "@lucide/vue";

import { api, unwrapList } from "../api/client";
import FitnessSpotCard from "../components/FitnessSpotCard.vue";

const q = ref("");
const spots = ref([]);

async function load() {
  const { data } = await api.get("/fitness-spots/", { params: { q: q.value } });
  spots.value = unwrapList(data);
}

onMounted(load);
</script>
