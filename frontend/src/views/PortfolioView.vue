<template>
  <section class="min-h-screen bg-[radial-gradient(circle_at_top_left,#ffffff_0,#f6f8fb_36%,#eef3f7_100%)]">
    <div class="page-shell py-6">
      <div class="mb-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold text-[#172033] md:text-4xl">오늘의 포트폴리오 편입 종목</h1>
          <p class="mt-2 text-sm font-bold text-slate-500">기준일 {{ portfolio.baseDate || "-" }} · 편입 종목 전체 보기</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <div class="flex rounded-lg border border-slate-200 bg-white p-1 shadow-sm">
            <button
              v-for="option in riskOptions"
              :key="option.value"
              type="button"
              class="rounded-md px-3 py-2 text-sm font-bold transition"
              :class="riskType === option.value ? 'bg-[#12b8a6] text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'"
              @click="setRiskType(option.value)"
            >
              {{ option.label }}
            </button>
          </div>
          <button class="btn-secondary min-h-10 gap-2 text-sm" type="button" @click="loadPortfolio">
            <RefreshCw :size="16" />
            새로고침
          </button>
        </div>
      </div>

      <div v-if="loading" class="panel p-8 text-center font-bold text-slate-500">편입 종목을 불러오는 중입니다.</div>
      <div v-else-if="error" class="panel border-red-200 bg-red-50 p-8 text-red-700">{{ error }}</div>

      <template v-else>
        <div class="mb-4 grid gap-3 md:grid-cols-3">
          <article class="panel p-4">
            <p class="text-sm font-bold text-slate-500">편입 종목</p>
            <p class="mt-2 text-3xl font-bold text-[#172033]">{{ portfolioItems.length }} 종목</p>
          </article>
          <article class="panel p-4">
            <p class="text-sm font-bold text-slate-500">추천 비중 합계</p>
            <p class="mt-2 text-3xl font-bold text-[#009e8e]">{{ formatPercent(investedWeight) }}%</p>
          </article>
          <article class="panel p-4">
            <p class="text-sm font-bold text-slate-500">현금 비중</p>
            <p class="mt-2 text-3xl font-bold text-amber-500">{{ formatPercent(portfolio.cashWeight) }}%</p>
          </article>
        </div>

        <section class="panel overflow-hidden">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">
            <div>
              <h2 class="text-xl font-bold text-[#172033]">편입 종목 전체</h2>
              <p class="mt-1 text-sm font-bold text-slate-500">{{ selectedRiskDescription }}</p>
            </div>
            <span v-if="portfolio.hurdles" class="rounded-full bg-[#ddf7f2] px-3 py-1 text-xs font-bold text-[#009e8e]">
              회사 {{ portfolio.hurdles.company }} · 타이밍 {{ portfolio.hurdles.timing }} · 신뢰도 {{ portfolio.hurdles.reliability }}
            </span>
          </div>

          <div v-if="portfolioItems.length" class="overflow-x-auto">
            <table class="w-full min-w-[960px] text-left">
              <thead class="bg-gradient-to-b from-slate-50 to-white text-xs font-bold text-slate-500">
                <tr>
                  <th class="px-5 py-3">순위</th>
                  <th class="px-4 py-3">종목명</th>
                  <th class="px-4 py-3">종목코드</th>
                  <th class="px-4 py-3">섹터</th>
                  <th class="px-4 py-3">테마</th>
                  <th class="px-4 py-3">종합 점수</th>
                  <th class="px-4 py-3">추천 비중</th>
                  <th class="px-5 py-3">핵심 추천 사유</th>
                  <th class="px-5 py-3">리포트</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 text-sm">
                <tr v-for="(item, index) in portfolioItems" :key="item.ticker" class="transition hover:bg-[#f7fcfb]">
                  <td class="px-5 py-4 font-bold text-[#172033]">{{ index + 1 }}</td>
                  <td class="px-4 py-4">
                    <p class="font-bold text-[#172033]">{{ item.name }}</p>
                    <div class="mt-1 flex flex-wrap gap-1">
                      <span v-if="item.sector_cap_applied" class="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700">섹터 조정</span>
                      <span v-if="item.volume_surge_flag" class="rounded bg-blue-100 px-2 py-0.5 text-xs font-bold text-blue-700">거래량</span>
                      <span v-if="item.target_upside_clipped" class="rounded bg-rose-100 px-2 py-0.5 text-xs font-bold text-rose-700">목표가 클리핑</span>
                    </div>
                  </td>
                  <td class="px-4 py-4 font-bold text-slate-600">{{ item.ticker }}</td>
                  <td class="px-4 py-4 font-bold text-slate-600">{{ item.sector || "-" }}</td>
                  <td class="px-4 py-4 font-bold text-slate-600">{{ item.primary_theme || "-" }}</td>
                  <td class="px-4 py-4">
                    <span class="rounded-md bg-[#12b8a6] px-3 py-1 text-sm font-bold text-white">{{ formatScore(item.total_score) }}</span>
                  </td>
                  <td class="px-4 py-4">
                    <div class="flex min-w-36 items-center gap-3">
                      <div class="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                        <div class="h-full rounded-full bg-[#12b8a6]" :style="{ width: `${Math.min(Number(item.weight || 0), 100)}%` }"></div>
                      </div>
                      <span class="w-12 text-right font-bold text-[#172033]">{{ formatPercent(item.weight) }}%</span>
                    </div>
                  </td>
                  <td class="px-5 py-4 font-bold leading-6 text-slate-600">{{ item.key_reason || item.reason || "-" }}</td>
                  <td class="px-5 py-4">
                    <RouterLink class="inline-flex rounded-md border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-[#0b2454] transition hover:border-[#12b8a6] hover:text-[#009e8e]" :to="{ name: 'stock-report', params: { ticker: item.ticker } }">
                      보기
                    </RouterLink>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="p-7">
            <h3 class="text-2xl font-bold text-[#172033]">오늘은 편입 종목이 없습니다.</h3>
            <p class="mt-2 text-slate-600">현재 성향 기준으로 회사 가치·진입 타이밍 허들을 모두 통과한 종목이 없습니다.</p>
          </div>
        </section>
      </template>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RefreshCw } from "@lucide/vue";

import { api } from "../api/client";

const portfolio = ref({});
const loading = ref(true);
const error = ref("");
const riskType = ref("neutral");
const riskOptions = [
  { value: "neutral", label: "중립형", description: "회사 70점·타이밍 70점·신뢰도 70점 기준으로 균형 있게 편입합니다." },
  { value: "aggressive", label: "공격형", description: "회사 65점·타이밍 75점·신뢰도 65점 기준으로 주도주 타이밍을 더 중시합니다." },
  { value: "stable", label: "안정형", description: "회사 75점·타이밍 65점·신뢰도 75점 기준으로 우량성과 데이터 신뢰도를 더 중시합니다." },
];

const portfolioItems = computed(() => portfolio.value.items || []);
const selectedRiskDescription = computed(
  () => riskOptions.find((option) => option.value === riskType.value)?.description || riskOptions[0].description,
);
const investedWeight = computed(() => portfolioItems.value.reduce((sum, item) => sum + Number(item.weight || 0), 0));

async function loadPortfolio() {
  loading.value = true;
  error.value = "";
  try {
    const response = await api.get("/portfolio/today/", { params: { risk_type: riskType.value } });
    portfolio.value = response.data;
  } catch (err) {
    error.value = "편입 종목 데이터를 불러오지 못했습니다. 백엔드 서버와 DB 상태를 확인하세요.";
  } finally {
    loading.value = false;
  }
}

function setRiskType(value) {
  if (riskType.value === value) return;
  riskType.value = value;
  loadPortfolio();
}

function formatScore(value) {
  const numberValue = Number(value || 0);
  return numberValue.toFixed(1).replace(".0", "");
}

function formatPercent(value) {
  const numberValue = Number(value || 0);
  return Number.isInteger(numberValue) ? String(numberValue) : numberValue.toFixed(1);
}

onMounted(loadPortfolio);
</script>
