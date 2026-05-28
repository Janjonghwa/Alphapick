<template>
  <section class="bg-slate-950 text-white">
    <div class="page-shell grid gap-10 py-12 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
      <div>
        <p class="text-sm font-black uppercase tracking-[0.2em] text-emerald-300">Daily Alpha Portfolio</p>
        <h1 class="mt-4 max-w-3xl text-4xl font-black leading-tight md:text-6xl">
          좋은 회사와 좋은 타이밍을 모두 통과한 오늘의 알파 포트폴리오
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
          회사 가치와 진입 타이밍을 각각 70점 기준으로 따로 판단하고,
          두 조건을 모두 통과한 종목만 포트폴리오에 편입합니다.
        </p>
        <div class="mt-8 flex flex-wrap gap-3">
          <RouterLink class="btn-primary bg-emerald-500 text-slate-950" to="/stocks">전체 종목 보기</RouterLink>
          <RouterLink class="btn-secondary border-white/15 bg-white/10 text-white" to="/backtest">백테스트 확인</RouterLink>
        </div>
      </div>

      <div class="rounded-lg border border-white/10 bg-white/8 p-5">
        <p class="text-sm font-bold text-slate-300">포트폴리오 정책</p>
        <div class="mt-5 grid grid-cols-2 gap-3">
          <div class="rounded-lg bg-white/10 p-4">
            <p class="text-sm text-slate-400">편입 기준</p>
            <p class="mt-2 text-3xl font-black">가치+타이밍</p>
          </div>
          <div class="rounded-lg bg-white/10 p-4">
            <p class="text-sm text-slate-400">비중 산정</p>
            <p class="mt-2 text-3xl font-black">균형 점수</p>
          </div>
          <div class="rounded-lg bg-white/10 p-4">
            <p class="text-sm text-slate-400">갱신 주기</p>
            <p class="mt-2 text-3xl font-black">매일</p>
          </div>
          <div class="rounded-lg bg-white/10 p-4">
            <p class="text-sm text-slate-400">최소 신뢰도</p>
            <p class="mt-2 text-3xl font-black">70점+</p>
          </div>
        </div>
        <div class="mt-5 rounded-lg bg-white/10 p-4">
          <p class="text-sm font-bold text-slate-300">투자 성향</p>
          <div class="mt-3 grid grid-cols-3 gap-2">
            <button
              v-for="option in riskOptions"
              :key="option.value"
              type="button"
              class="rounded-lg border px-3 py-2 text-sm font-black transition"
              :class="riskType === option.value ? 'border-emerald-300 bg-emerald-300 text-slate-950' : 'border-white/15 bg-white/5 text-white hover:bg-white/10'"
              @click="setRiskType(option.value)"
            >
              {{ option.label }}
            </button>
          </div>
          <p class="mt-3 text-sm leading-6 text-slate-300">{{ selectedRiskDescription }}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="page-shell py-10">
    <div v-if="loading" class="panel p-8 text-center font-bold text-slate-500">포트폴리오를 불러오는 중입니다.</div>
    <div v-else-if="error" class="panel border-red-200 bg-red-50 p-8 text-red-700">{{ error }}</div>

    <template v-else>
      <div class="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
        <div class="panel p-6">
          <p class="text-sm font-black uppercase tracking-[0.18em] text-emerald-600">Today's Portfolio</p>
          <div class="mt-4 flex items-end justify-between gap-4">
            <div>
              <p class="text-sm font-bold text-slate-500">기준일 {{ portfolio.baseDate || "-" }}</p>
              <h2 class="mt-1 text-4xl font-black text-slate-950">{{ portfolio.portfolioScore || 0 }}점</h2>
              <p class="mt-2 text-sm font-black text-emerald-700">
                {{ portfolio.riskTypeLabel || "중립형" }} 포트폴리오 · 균형 {{ portfolio.eligibilityScore || 0 }}점
              </p>
            </div>
            <div class="rounded-lg bg-slate-100 px-4 py-3 text-right">
              <p class="text-sm text-slate-500">편입 종목</p>
              <p class="text-2xl font-black text-slate-950">{{ portfolio.items?.length || 0 }}개</p>
            </div>
          </div>
          <p class="mt-5 leading-7 text-slate-600">{{ portfolio.summary }}</p>
          <p v-if="portfolio.sectorWarning" class="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm font-bold text-amber-700">
            {{ portfolio.sectorWarning }}
          </p>

          <div class="mt-6">
            <p class="mb-3 text-sm font-black text-slate-700">회사·타이밍 70점 통과 강도 비례 예상 비중</p>
            <div v-for="item in portfolio.items" :key="item.ticker" class="mb-3">
              <div class="mb-1 flex justify-between text-sm font-bold">
                <span>{{ item.name }}</span>
                <span>{{ item.weight }}%</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                <div class="h-full rounded-full bg-emerald-500" :style="{ width: `${item.weight}%` }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid gap-4">
          <article
            v-for="item in portfolio.items"
            :key="item.ticker"
            class="panel grid gap-4 p-5 md:grid-cols-[1fr_auto]"
          >
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-2xl font-black text-slate-950">{{ item.name }}</h3>
                <span class="badge bg-slate-100 text-slate-600">{{ item.ticker }}</span>
                <span class="badge bg-emerald-50 text-emerald-700">{{ item.sector }}</span>
                <span class="badge bg-blue-50 text-blue-700">{{ item.primary_theme }}</span>
              </div>
              <div class="mt-3 flex flex-wrap gap-2">
                <span class="badge bg-slate-950 text-white">{{ item.signal }}</span>
                <span v-if="item.volume_surge_flag" class="badge bg-blue-100 text-blue-700">거래량 급증</span>
                <span v-if="item.target_upside_clipped" class="badge bg-amber-100 text-amber-700">목표가 200%+ 클리핑</span>
              </div>
              <p class="mt-3 font-bold text-slate-700">핵심 사유: {{ item.key_reason || item.reason }}</p>
              <p class="mt-2 text-sm text-rose-600">주의 사유: {{ item.warning || "특이 경고 없음" }}</p>
            </div>
            <div class="flex min-w-40 flex-col items-start gap-3 md:items-end">
              <div class="text-left md:text-right">
                <p class="text-sm text-slate-500">리스크 반영 점수</p>
                <p class="text-3xl font-black text-rose-500">{{ item.total_score.toFixed(1) }}점</p>
                <p class="text-sm font-bold text-emerald-700">회사 {{ item.company_score }} · 타이밍 {{ item.timing_score }}</p>
                <p class="text-sm font-bold text-slate-500">추천 비중 {{ item.weight }}%</p>
              </div>
              <RouterLink class="btn-primary" :to="{ name: 'stock-report', params: { ticker: item.ticker } }">리포트 보기</RouterLink>
            </div>
          </article>

          <div v-if="!portfolio.items?.length" class="panel p-7">
            <h3 class="text-2xl font-black text-slate-950">오늘은 추천 조건을 만족한 종목이 없습니다.</h3>
            <p class="mt-2 text-slate-600">회사 가치와 진입 타이밍이 모두 70점 이상인 종목이 없으므로 관찰 후보만 표시합니다.</p>
          </div>
        </div>
      </div>

      <div class="mt-8 grid gap-5 lg:grid-cols-2">
        <div class="panel p-6">
          <h2 class="text-2xl font-black text-slate-950">관찰 후보 TOP 5</h2>
          <div class="mt-4 divide-y divide-slate-100">
            <RouterLink
              v-for="candidate in portfolio.watchCandidates"
              :key="candidate.ticker"
              class="flex items-center justify-between gap-4 py-3"
              :to="{ name: 'stock-report', params: { ticker: candidate.ticker } }"
            >
              <span>
                <strong class="block text-slate-950">{{ candidate.name }}</strong>
                <span class="text-sm text-slate-500">{{ candidate.primary_theme || candidate.sector }} · {{ candidate.ticker }}</span>
                <span class="mt-1 flex flex-wrap gap-1 text-xs font-black">
                  <span v-if="candidate.low_liquidity_flag" class="rounded bg-amber-100 px-2 py-0.5 text-amber-700">유동성 주의</span>
                  <span v-if="candidate.fail_safe_flag" class="rounded bg-red-100 px-2 py-0.5 text-red-700">Fail-safe</span>
                  <span v-if="candidate.volume_surge_flag" class="rounded bg-blue-100 px-2 py-0.5 text-blue-700">거래량 급증</span>
                </span>
              </span>
              <span class="text-xl font-black text-slate-700">{{ candidate.latest_score }}점</span>
            </RouterLink>
          </div>
        </div>

        <div class="panel p-6">
          <h2 class="text-2xl font-black text-slate-950">백테스트 요약</h2>
          <p class="mt-2 text-slate-600">{{ backtest.summary }}</p>
          <div class="mt-5 grid grid-cols-3 gap-3">
            <div class="rounded-lg bg-emerald-50 p-4">
              <p class="text-sm text-emerald-700">포트폴리오</p>
              <p class="text-2xl font-black text-emerald-700">+{{ backtest.portfolioReturn }}%</p>
            </div>
            <div class="rounded-lg bg-slate-100 p-4">
              <p class="text-sm text-slate-500">{{ backtest.benchmark }}</p>
              <p class="text-2xl font-black text-slate-700">+{{ backtest.benchmarkReturn }}%</p>
            </div>
            <div class="rounded-lg bg-slate-100 p-4">
              <p class="text-sm text-slate-500">승률</p>
              <p class="text-2xl font-black text-slate-700">{{ backtest.winRate }}%</p>
            </div>
          </div>
          <RouterLink class="btn-secondary mt-5" to="/backtest">자세히 보기</RouterLink>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { api } from "../api/client";

const portfolio = ref({});
const backtest = ref({});
const loading = ref(true);
const error = ref("");
const riskType = ref("neutral");
const riskOptions = [
  { value: "neutral", label: "중립형", description: "기업 점수 45%, 타이밍 점수 55%를 반영합니다." },
  { value: "aggressive", label: "공격형", description: "주도주 모멘텀과 피벗 돌파 등 타이밍 점수를 더 강하게 반영합니다." },
  { value: "stable", label: "안정형", description: "가치/퀄리티, ROE, EPS 가속도 등 기업 점수를 더 강하게 반영합니다." },
];

const selectedRiskDescription = computed(
  () => riskOptions.find((option) => option.value === riskType.value)?.description || riskOptions[0].description,
);

async function loadDashboard() {
  loading.value = true;
  error.value = "";
  try {
    const [portfolioResponse, backtestResponse] = await Promise.all([
      api.get("/portfolio/today/", { params: { risk_type: riskType.value } }),
      api.get("/portfolio/backtest/", { params: { risk_type: riskType.value } }),
    ]);
    portfolio.value = portfolioResponse.data;
    backtest.value = backtestResponse.data;
  } catch (err) {
    error.value = "포트폴리오 데이터를 불러오지 못했습니다. 백엔드 서버와 seed_alphapick 실행 여부를 확인하세요.";
  } finally {
    loading.value = false;
  }
}

function setRiskType(value) {
  if (riskType.value === value) return;
  riskType.value = value;
  loadDashboard();
}

onMounted(loadDashboard);
</script>
