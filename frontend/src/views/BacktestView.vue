<template>
  <section class="page-shell py-8">
    <div class="mb-6">
      <p class="text-sm font-black uppercase tracking-[0.18em] text-emerald-600">Backtest</p>
      <h1 class="mt-2 text-4xl font-black text-slate-950">추천 포트폴리오 vs 지수 수익률</h1>
      <p class="mt-3 max-w-3xl leading-7 text-slate-600">
        매일 70점 이상 추천 후보만 편입하고 70점 초과분 비례로 리밸런싱한다고 가정한 MVP 검증 화면입니다.
      </p>
    </div>

    <div v-if="loading" class="panel p-8 text-center font-bold text-slate-500">백테스트를 불러오는 중입니다.</div>
    <div v-else class="grid gap-6">
      <div class="grid gap-4 md:grid-cols-4">
        <div class="panel p-5">
          <p class="text-sm font-bold text-slate-500">포트폴리오 수익률</p>
          <p class="mt-2 text-3xl font-black text-emerald-600">+{{ backtest.portfolioReturn }}%</p>
        </div>
        <div class="panel p-5">
          <p class="text-sm font-bold text-slate-500">{{ backtest.benchmark }} 수익률</p>
          <p class="mt-2 text-3xl font-black text-slate-700">+{{ backtest.benchmarkReturn }}%</p>
        </div>
        <div class="panel p-5">
          <p class="text-sm font-bold text-slate-500">승률</p>
          <p class="mt-2 text-3xl font-black text-slate-950">{{ backtest.winRate }}%</p>
        </div>
        <div class="panel p-5">
          <p class="text-sm font-bold text-slate-500">최대 낙폭</p>
          <p class="mt-2 text-3xl font-black text-rose-500">{{ backtest.maxDrawdown }}%</p>
        </div>
      </div>

      <div class="panel p-5">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-2xl font-black text-slate-950">누적 수익률 차트</h2>
          <p class="text-sm font-bold text-slate-500">{{ backtest.summary }}</p>
        </div>
        <svg class="h-[340px] w-full" viewBox="0 0 900 340" role="img" aria-label="backtest chart">
          <line x1="45" y1="285" x2="875" y2="285" stroke="#e2e8f0" />
          <line x1="45" y1="45" x2="45" y2="285" stroke="#e2e8f0" />
          <polyline :points="linePoints('portfolio')" fill="none" stroke="#10b981" stroke-width="5" />
          <polyline :points="linePoints('benchmark')" fill="none" stroke="#64748b" stroke-width="4" stroke-dasharray="8 6" />
        </svg>
        <div class="mt-4 flex gap-5 text-sm font-black">
          <span class="text-emerald-600">추천 포트폴리오</span>
          <span class="text-slate-500">{{ backtest.benchmark }}</span>
        </div>
      </div>

      <div class="panel overflow-hidden">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-100 text-slate-500">
            <tr>
              <th class="p-3">날짜</th>
              <th class="p-3">포트폴리오</th>
              <th class="p-3">지수</th>
              <th class="p-3">편입 종목</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="row in backtest.series" :key="row.date">
              <td class="p-3 font-bold">{{ row.date }}</td>
              <td class="p-3 text-emerald-600">{{ row.portfolio }}</td>
              <td class="p-3 text-slate-600">{{ row.benchmark }}</td>
              <td class="p-3">{{ row.itemCount }}개</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { api } from "../api/client";

const backtest = ref({ series: [] });
const loading = ref(true);

const bounds = computed(() => {
  const values = backtest.value.series.flatMap((row) => [row.portfolio, row.benchmark]);
  const min = Math.min(...values, 99);
  const max = Math.max(...values, 101);
  return { min, max: max === min ? max + 1 : max };
});

function linePoints(field) {
  const series = backtest.value.series || [];
  const { min, max } = bounds.value;
  return series
    .map((row, index) => {
      const x = 50 + (index / Math.max(series.length - 1, 1)) * 800;
      const y = 275 - ((row[field] - min) / (max - min)) * 215;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

onMounted(async () => {
  const response = await api.get("/portfolio/backtest/");
  backtest.value = response.data;
  loading.value = false;
});
</script>
