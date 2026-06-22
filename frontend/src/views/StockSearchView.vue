<template>
  <section class="page-shell py-8">
    <div class="mb-6">
      <p class="text-sm font-bold uppercase tracking-[0.18em] text-emerald-600">Stock Universe</p>
      <h1 class="mt-2 text-4xl font-bold text-slate-950">종목 검색과 스코어 필터</h1>
      <p class="mt-3 max-w-3xl leading-7 text-slate-600">
        포트폴리오에는 회사 가치와 진입 타이밍이 모두 70점 이상인 종목만 편입되지만, 전체 종목의 리포트와 관찰 후보도 함께 확인할 수 있습니다.
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

    <div v-if="!loading" class="mb-4 flex flex-wrap items-center justify-between gap-3 text-sm font-bold text-slate-500">
      <span>전체 {{ totalCount }}개 중 {{ stocks.length }}개 표시</span>
      <span v-if="nextPage">스크롤하면 다음 종목을 계속 불러옵니다.</span>
      <span v-else>모든 조건의 종목을 불러왔습니다.</span>
    </div>

    <div v-if="loading" class="panel p-8 text-center font-bold text-slate-500">종목을 불러오는 중입니다.</div>
    <div v-else-if="error" class="panel border-red-200 bg-red-50 p-8 font-bold text-red-700">{{ error }}</div>
    <div v-else-if="!stocks.length" class="panel p-8 text-center font-bold text-slate-500">조건에 맞는 종목이 없습니다.</div>
    <template v-else>
      <div class="grid gap-4 md:grid-cols-2">
        <RouterLink
          v-for="stock in stocks"
          :key="stock.ticker"
          :to="{ name: 'stock-report', params: { ticker: stock.ticker } }"
          class="panel p-5 transition hover:-translate-y-0.5 hover:shadow-soft"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <h2 class="text-2xl font-bold text-slate-950">{{ stock.name }}</h2>
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
              <p class="text-3xl font-bold" :class="stock.latest_score >= 70 ? 'text-rose-500' : 'text-slate-700'">
                {{ stock.latest_score }}
              </p>
            </div>
          </div>
        </RouterLink>
      </div>

      <div ref="loadMoreSentinel" class="py-8 text-center">
        <p v-if="loadingMore" class="font-bold text-slate-500">다음 종목을 불러오는 중입니다.</p>
        <button v-else-if="nextPage" class="btn-secondary" type="button" @click="loadMore">더 불러오기</button>
        <p v-else class="font-bold text-slate-400">마지막 종목까지 모두 표시했습니다.</p>
      </div>
    </template>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, reactive, ref } from "vue";

import { api } from "../api/client";

const filters = reactive({
  q: "",
  min_score: "",
});
const stocks = ref([]);
const loading = ref(true);
const loadingMore = ref(false);
const error = ref("");
const nextPage = ref(null);
const totalCount = ref(0);
const loadMoreSentinel = ref(null);
let observer = null;

function requestParams(page) {
  const params = { page };
  if (filters.q) params.q = filters.q;
  if (filters.min_score) params.min_score = filters.min_score;
  return params;
}

function updatePagination(payload, page) {
  if (Array.isArray(payload)) {
    totalCount.value = payload.length;
    nextPage.value = null;
    return payload;
  }

  totalCount.value = payload?.count ?? 0;
  nextPage.value = payload?.next ? page + 1 : null;
  return payload?.results ?? [];
}

function setupInfiniteScroll() {
  observer?.disconnect();
  if (!loadMoreSentinel.value || !nextPage.value) return;

  observer = new IntersectionObserver(
    (entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        loadMore();
      }
    },
    { rootMargin: "500px 0px" },
  );
  observer.observe(loadMoreSentinel.value);
}

async function fetchStocksPage(page, append = false) {
  const response = await api.get("/stocks/", { params: requestParams(page) });
  const rows = updatePagination(response.data, page);
  stocks.value = append ? [...stocks.value, ...rows] : rows;
  await nextTick();
  setupInfiniteScroll();
}

async function loadStocks() {
  loading.value = true;
  error.value = "";
  stocks.value = [];
  nextPage.value = null;
  try {
    await fetchStocksPage(1);
  } catch {
    error.value = "종목 데이터를 불러오지 못했습니다. 백엔드 서버 상태를 확인해 주세요.";
  } finally {
    loading.value = false;
    await nextTick();
    setupInfiniteScroll();
  }
}

async function loadMore() {
  if (!nextPage.value || loadingMore.value || loading.value) return;
  loadingMore.value = true;
  const page = nextPage.value;
  try {
    await fetchStocksPage(page, true);
  } catch {
    error.value = "다음 종목을 불러오지 못했습니다.";
  } finally {
    loadingMore.value = false;
  }
}

onMounted(loadStocks);
onBeforeUnmount(() => observer?.disconnect());
</script>
