<template>
  <section class="page-shell py-8">
    <div class="mb-6">
      <p class="text-sm font-black uppercase tracking-[0.18em] text-emerald-600">Stock Universe</p>
      <h1 class="mt-2 text-4xl font-black text-slate-950">종목 검색과 스코어 필터</h1>
      <p class="mt-3 max-w-3xl leading-7 text-slate-600">
        포트폴리오에는 70점 이상 추천 후보만 편입되지만, 전체 종목의 리포트와 관찰 후보도 함께 확인할 수 있습니다.
      </p>
    </div>

    <div class="panel mb-6 grid gap-3 p-4 md:grid-cols-[1fr_180px_160px]">
      <input v-model="filters.q" class="field" placeholder="종목명 또는 티커 검색" @keyup.enter="loadStocks" />
      <select v-model="filters.min_score" class="field">
        <option value="">전체 점수</option>
        <option value="90">90점 이상</option>
        <option value="80">80점 이상</option>
        <option value="70">70점 이상</option>
        <option value="60">60점 이상</option>
      </select>
      <button class="btn-primary" type="button" @click="loadStocks">검색</button>
    </div>

    <div v-if="loading" class="panel p-8 text-center font-bold text-slate-500">종목을 불러오는 중입니다.</div>
    <div v-else class="grid gap-4 md:grid-cols-2">
      <RouterLink
        v-for="stock in stocks"
        :key="stock.ticker"
        :to="{ name: 'stock-report', params: { ticker: stock.ticker } }"
        class="panel p-5 transition hover:-translate-y-0.5 hover:shadow-soft"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="text-2xl font-black text-slate-950">{{ stock.name }}</h2>
              <span class="badge bg-slate-100 text-slate-600">{{ stock.ticker }}</span>
              <span class="badge bg-emerald-50 text-emerald-700">{{ stock.sector }}</span>
              <span class="badge bg-blue-50 text-blue-700">{{ stock.primary_theme }}</span>
            </div>
            <div class="mt-3 flex flex-wrap gap-2">
              <span v-if="stock.signal" class="badge bg-slate-950 text-white">{{ stock.signal }}</span>
              <span v-if="stock.low_liquidity_flag" class="badge bg-amber-100 text-amber-700">유동성 주의</span>
              <span v-if="stock.fail_safe_flag" class="badge bg-red-100 text-red-700">Fail-safe</span>
              <span v-if="stock.volume_surge_flag" class="badge bg-blue-100 text-blue-700">거래량 급증</span>
            </div>
            <p class="mt-3 text-sm leading-6 text-slate-600">{{ stock.key_reason || stock.reason }}</p>
          </div>
          <div class="text-right">
            <p class="text-sm font-bold text-slate-500">점수</p>
            <p class="text-3xl font-black" :class="stock.latest_score >= 70 ? 'text-rose-500' : 'text-slate-700'">
              {{ stock.latest_score }}
            </p>
          </div>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import { api, unwrapList } from "../api/client";

const filters = reactive({
  q: "",
  min_score: "",
});
const stocks = ref([]);
const loading = ref(true);

async function loadStocks() {
  loading.value = true;
  const params = {};
  if (filters.q) params.q = filters.q;
  if (filters.min_score) params.min_score = filters.min_score;
  const response = await api.get("/stocks/", { params });
  stocks.value = unwrapList(response.data);
  loading.value = false;
}

onMounted(loadStocks);
</script>
