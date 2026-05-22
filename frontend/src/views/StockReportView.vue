<template>
  <section class="page-shell py-8">
    <div v-if="loading" class="panel p-8 text-center font-bold text-slate-500">스코어 리포트를 불러오는 중입니다.</div>
    <div v-else-if="error" class="panel border-red-200 bg-red-50 p-8 text-red-700">{{ error }}</div>

    <template v-else>
      <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <h1 class="text-3xl font-black text-slate-950">{{ report.stock.name }}</h1>
            <span class="badge bg-slate-100 text-slate-600">{{ report.stock.ticker }}</span>
            <span class="badge bg-blue-50 text-blue-700">{{ report.stock.sector }}</span>
            <span class="badge bg-emerald-50 text-emerald-700">{{ report.stock.primary_theme }}</span>
          </div>
          <div class="mt-2 flex flex-wrap gap-2">
            <span class="badge bg-slate-950 text-white">{{ report.score.signal }}</span>
            <span v-if="report.stock.low_liquidity_flag" class="badge bg-amber-100 text-amber-700">유동성 주의</span>
            <span v-if="report.score.fail_safe_flag" class="badge bg-red-100 text-red-700">Fail-safe</span>
            <span v-if="report.score.volume_surge_flag" class="badge bg-blue-100 text-blue-700">거래량 급증</span>
            <span v-if="report.score.target_upside_clipped" class="badge bg-amber-100 text-amber-700">목표가 200%+ 클리핑</span>
          </div>
          <p class="mt-2 text-sm font-bold text-slate-500">데이터 기준일 {{ report.score.base_date }}</p>
        </div>
        <button class="btn-primary" type="button" @click="captureHint = true">캡처</button>
      </div>

      <p v-if="captureHint" class="mb-4 rounded-lg bg-emerald-50 p-3 text-sm font-bold text-emerald-700">
        브라우저 캡처 기능으로 현재 리포트를 저장할 수 있습니다.
      </p>

      <section class="rounded-lg border border-slate-800 bg-slate-300 p-7 text-center text-slate-950">
        <h2 class="text-4xl font-black leading-tight md:text-5xl">{{ report.score.headline }}</h2>
        <p class="mt-4 text-xl font-black text-slate-900">{{ report.score.key_reason }}</p>
        <p class="mt-4 text-lg font-black text-slate-700">{{ report.score.summary_metrics.join(" · ") }}</p>
      </section>

      <div class="mt-6 grid gap-4 md:grid-cols-4">
        <div v-for="card in report.score.timing_cards" :key="card.label" class="panel p-4">
          <p class="text-sm font-black text-slate-500">{{ card.label }}</p>
          <p class="mt-2 text-3xl font-black text-slate-950">{{ card.score }}/{{ card.max }}</p>
          <p class="mt-2 text-sm leading-6 text-slate-500">{{ card.description }}</p>
        </div>
      </div>

      <div class="mt-6 panel p-5">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
          <h2 class="text-2xl font-black text-slate-950">{{ report.stock.name }} 가격 차트</h2>
          <div class="flex flex-wrap gap-3 text-sm font-bold text-slate-500">
            <span>Close</span>
            <span class="text-blue-500">EMA20</span>
            <span class="text-orange-500">EMA50</span>
            <span class="text-violet-500">EMA200</span>
          </div>
        </div>
        <svg class="h-[320px] w-full overflow-visible" viewBox="0 0 900 320" role="img" aria-label="stock price chart">
          <line x1="40" y1="270" x2="880" y2="270" stroke="#e2e8f0" />
          <line x1="40" y1="35" x2="40" y2="270" stroke="#e2e8f0" />
          <polyline :points="linePoints('bb_upper')" fill="none" stroke="#cbd5e1" stroke-dasharray="5 5" stroke-width="2" />
          <polyline :points="linePoints('bb_lower')" fill="none" stroke="#cbd5e1" stroke-dasharray="5 5" stroke-width="2" />
          <polyline :points="linePoints('ema200')" fill="none" stroke="#8b5cf6" stroke-dasharray="8 6" stroke-width="3" />
          <polyline :points="linePoints('ema50')" fill="none" stroke="#f97316" stroke-width="3" />
          <polyline :points="linePoints('ema20')" fill="none" stroke="#3b82f6" stroke-width="3" />
          <polyline :points="linePoints('close_price')" fill="none" stroke="#0f172a" stroke-width="4" />
          <g v-for="(bar, index) in volumeBars" :key="index">
            <rect :x="bar.x" :y="bar.y" :width="bar.width" :height="bar.height" :fill="bar.fill" opacity="0.7" />
          </g>
        </svg>
        <p class="mt-4 rounded-lg bg-slate-50 p-4 text-sm font-bold leading-6 text-slate-600">
          핵심 관찰: 현재가는 {{ latestPrice }}원이며, 종합 점수 {{ report.score.total_score }}점으로
          {{ report.score.verdict }} 상태입니다. {{ report.score.warning }}
        </p>
      </div>

      <div class="mt-6 grid gap-6 lg:grid-cols-[280px_1fr]">
        <aside class="space-y-4">
          <div class="panel p-5">
            <p class="text-sm font-black text-slate-500">이 회사 자체는 좋은가?</p>
            <p class="mt-3 text-6xl font-black text-rose-500">{{ report.score.total_score }}</p>
            <p class="text-xl font-black text-slate-700">점</p>
            <p class="mt-3 inline-flex rounded-full bg-amber-100 px-3 py-1 text-sm font-black text-amber-700">{{ report.score.verdict }}</p>
          </div>

          <div class="panel p-5">
            <p class="text-sm font-black text-slate-500">회사 가치 × 진입 타이밍</p>
            <div class="mt-4 grid h-40 grid-cols-2 grid-rows-2 overflow-hidden rounded-lg border border-slate-100">
              <div class="bg-rose-50"></div>
              <div class="bg-emerald-50"></div>
              <div class="bg-slate-100"></div>
              <div class="bg-blue-50"></div>
              <span class="absolute"></span>
            </div>
            <div class="relative -mt-24 h-24">
              <div
                class="absolute h-4 w-4 rounded-full border-2 border-white bg-rose-500 shadow"
                :style="{ left: `${report.score.company_score}%`, bottom: `${report.score.timing_score - 50}%` }"
              ></div>
            </div>
            <p class="mt-3 text-sm font-bold text-slate-600">
              회사 {{ report.score.company_score }}점 · 타이밍 {{ report.score.timing_score }}점
            </p>
          </div>

          <div class="panel divide-y divide-slate-100">
            <div class="flex justify-between p-4">
              <span class="text-slate-500">현재가</span>
              <strong>{{ latestPrice }}원</strong>
            </div>
            <div class="flex justify-between p-4">
              <span class="text-slate-500">목표가</span>
              <strong>{{ formatNumber(report.financialMetric.target_price) }}원</strong>
            </div>
            <div class="flex justify-between p-4">
              <span class="text-slate-500">목표가 상승여력</span>
              <strong :class="report.score.target_upside_clipped ? 'text-amber-600' : 'text-slate-900'">{{ targetUpsideText }}</strong>
            </div>
            <div class="flex justify-between p-4">
              <span class="text-slate-500">PER</span>
              <strong>{{ report.financialMetric.per }}배</strong>
            </div>
            <div class="flex justify-between p-4">
              <span class="text-slate-500">ROE</span>
              <strong>{{ report.financialMetric.roe }}%</strong>
            </div>
          </div>
        </aside>

        <main class="space-y-6">
          <section class="panel p-5">
            <h2 class="border-l-4 border-emerald-500 pl-3 text-2xl font-black text-slate-950">데이터 정제 및 계산 근거</h2>
            <div class="mt-5 grid gap-3 md:grid-cols-2">
              <div class="rounded-lg bg-slate-50 p-4">
                <p class="text-sm font-black text-slate-500">Signal</p>
                <p class="mt-1 font-black text-slate-900">{{ report.score.signal }}</p>
              </div>
              <div class="rounded-lg bg-slate-50 p-4">
                <p class="text-sm font-black text-slate-500">Consensus / Confidence</p>
                <p class="mt-1 font-black text-slate-900">{{ report.score.consensus || "-" }} · {{ report.score.confidence || "-" }}</p>
              </div>
              <div class="rounded-lg bg-slate-50 p-4">
                <p class="text-sm font-black text-slate-500">Area Scores</p>
                <p class="mt-1 font-bold text-slate-700">
                  Momentum {{ report.score.area_scores?.momentum }} · Value {{ report.score.area_scores?.value }} · Quality {{ report.score.area_scores?.quality }}
                </p>
              </div>
              <div class="rounded-lg bg-slate-50 p-4">
                <p class="text-sm font-black text-slate-500">RS / RSI / 거래량</p>
                <p class="mt-1 font-bold text-slate-700">
                  RS {{ report.score.rs_rank ?? "-" }} · RSI {{ report.score.rsi ?? "-" }} · 거래량 {{ report.score.volume_ratio }}x
                </p>
              </div>
            </div>
            <div class="mt-4 space-y-2">
              <p v-for="log in report.score.scoring_log" :key="log" class="rounded-lg border border-slate-100 p-3 text-sm font-bold text-slate-600">
                {{ log }}
              </p>
            </div>
          </section>

          <section class="panel p-5">
            <h2 class="border-l-4 border-emerald-500 pl-3 text-2xl font-black text-slate-950">CAN SLIM 분석</h2>
            <div class="mt-5 space-y-3">
              <div
                v-for="item in report.score.can_slim"
                :key="item.code"
                class="flex gap-3 rounded-lg p-3"
                :class="statusSoftClass(item.status)"
              >
                <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-500 text-sm font-black text-white">{{ item.code }}</span>
                <div>
                  <p class="font-black text-slate-800">{{ item.label }}</p>
                  <p class="text-sm text-slate-600">{{ item.reason }}</p>
                </div>
              </div>
            </div>
          </section>

          <section class="panel p-5">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 class="border-l-4 border-emerald-500 pl-3 text-2xl font-black text-slate-950">AI 3줄 코멘트</h2>
                <p class="mt-2 text-sm font-bold text-slate-500">기업 점수, 타이밍 점수, 리스크 할인 요인을 바탕으로 긍정 요인, 주의 요인, 종합 의견을 요약합니다.</p>
              </div>
              <button class="btn-primary" type="button" :disabled="aiLoading" @click="loadAiComment">
                {{ aiLoading ? "분석 중" : aiLoadingLabel }}
              </button>
            </div>

            <div v-if="aiError" class="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-bold text-red-700">
              {{ aiError }}
            </div>
            <div v-else-if="aiComment" class="mt-5 grid gap-3">
              <div class="rounded-lg bg-emerald-50 p-4">
                <p class="text-sm font-black text-emerald-700">긍정 요인</p>
                <p class="mt-1 font-bold leading-7 text-slate-800">{{ aiComment.positive }}</p>
              </div>
              <div class="rounded-lg bg-amber-50 p-4">
                <p class="text-sm font-black text-amber-700">주의 요인</p>
                <p class="mt-1 font-bold leading-7 text-slate-800">{{ aiComment.negative }}</p>
              </div>
              <div class="rounded-lg bg-slate-100 p-4">
                <p class="text-sm font-black text-slate-600">종합 의견</p>
                <p class="mt-1 font-bold leading-7 text-slate-800">{{ aiComment.conclusion }}</p>
                <p class="mt-2 text-xs font-bold text-slate-400">
                  {{ aiComment.provider }} · {{ aiComment.cached ? "캐시 사용" : "새로 생성" }}
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 class="mb-4 border-l-4 border-emerald-500 pl-3 text-2xl font-black text-slate-950">스코어 카드</h2>
            <div class="grid gap-4 md:grid-cols-2">
              <article v-for="card in report.score.score_cards" :key="`${card.code}-${card.title}`" class="panel p-5">
                <div class="flex items-start justify-between gap-3">
                  <div class="flex items-center gap-3">
                    <span class="rounded-lg bg-blue-500 px-3 py-2 text-sm font-black text-white">{{ card.code }}</span>
                    <div>
                      <h3 class="font-black text-slate-900">{{ card.title }}</h3>
                      <p class="text-sm text-slate-500">{{ card.rawValue }}</p>
                    </div>
                  </div>
                  <span class="text-xs font-black uppercase text-slate-400">{{ card.group }}</span>
                </div>
                <p class="mt-4 text-center text-4xl font-black" :class="scoreColor(card.score)">{{ card.score }}</p>
                <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
                  <div class="h-full rounded-full" :class="scoreBar(card.score)" :style="{ width: `${card.score}%` }"></div>
                </div>
                <p class="mt-3 text-sm leading-6 text-slate-600">{{ card.reason }}</p>
              </article>
            </div>
          </section>

          <IndicatorSection title="기술 지표" :items="report.score.technical_indicators" />
          <IndicatorSection title="재무 지표" :items="report.score.financial_indicators" />

          <section class="panel p-5">
            <h2 class="border-l-4 border-emerald-500 pl-3 text-2xl font-black text-slate-950">공시·뉴스</h2>
            <div class="mt-5 rounded-lg bg-emerald-50 p-4">
              <p class="font-black text-emerald-700">뉴스 감성분석: 긍정 우위</p>
              <p class="mt-1 text-sm text-emerald-700">MVP에서는 제목 키워드 기반으로 긍정/중립/부정을 분류합니다.</p>
            </div>
            <div class="mt-4 divide-y divide-slate-100">
              <p v-for="news in report.score.news" :key="news.title" class="py-3 text-sm font-bold text-blue-600">
                {{ news.publishedAt }} · {{ news.title }}
              </p>
            </div>
            <div class="mt-5 rounded-lg border border-slate-100">
              <p v-for="disclosure in report.score.disclosures" :key="disclosure.title" class="border-b border-slate-100 p-3 text-sm">
                <span class="text-slate-400">{{ disclosure.date }}</span>
                <span class="ml-3 font-bold text-blue-600">{{ disclosure.title }}</span>
              </p>
            </div>
          </section>
        </main>
      </div>

      <p class="mt-6 rounded-lg bg-slate-100 p-4 text-sm font-bold text-slate-600">{{ report.investmentNotice }}</p>
    </template>
  </section>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from "vue";

import { api } from "../api/client";

const props = defineProps({
  ticker: {
    type: String,
    required: true,
  },
});

const report = ref(null);
const loading = ref(true);
const error = ref("");
const captureHint = ref(false);
const aiComment = ref(null);
const aiLoading = ref(false);
const aiError = ref("");

const aiLoadingLabel = computed(() => (aiComment.value ? "다시 보기" : "AI 분석 보기"));

const latestPrice = computed(() => {
  const price = report.value?.priceSeries?.at(-1)?.close_price;
  return formatNumber(price || report.value?.financialMetric?.current_price || 0);
});

const targetUpsideText = computed(() => {
  const upside = report.value?.score?.target_upside;
  if (upside === null || upside === undefined) return "목표가 미산정";
  return report.value?.score?.target_upside_clipped ? `${upside}%+` : `${upside}%`;
});

const chartBounds = computed(() => {
  const prices = report.value?.priceSeries || [];
  const values = prices.flatMap((point) => [
    point.close_price,
    point.ema20,
    point.ema50,
    point.ema200,
    point.bb_upper,
    point.bb_lower,
  ]).filter(Boolean);
  const min = Math.min(...values);
  const max = Math.max(...values);
  return { min, max: max === min ? max + 1 : max };
});

const volumeBars = computed(() => {
  const prices = report.value?.priceSeries || [];
  const maxVolume = Math.max(...prices.map((point) => point.volume), 1);
  return prices.map((point, index) => {
    const x = 45 + (index / Math.max(prices.length - 1, 1)) * 820;
    const height = (point.volume / maxVolume) * 58;
    return {
      x,
      y: 270 - height,
      width: Math.max(2, 780 / Math.max(prices.length, 1)),
      height,
      fill: index > 0 && point.close_price >= prices[index - 1].close_price ? "#3b82f6" : "#fb7185",
    };
  });
});

function linePoints(field) {
  const prices = report.value?.priceSeries || [];
  const { min, max } = chartBounds.value;
  return prices
    .map((point, index) => {
      const value = point[field];
      const x = 45 + (index / Math.max(prices.length - 1, 1)) * 820;
      const y = 255 - ((value - min) / (max - min)) * 210;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("ko-KR");
}

function statusSoftClass(status) {
  if (status === "pass") return "bg-emerald-50 text-emerald-800";
  if (status === "fail") return "bg-rose-50 text-rose-800";
  return "bg-slate-100 text-slate-700";
}

function scoreColor(score) {
  if (score >= 80) return "text-emerald-600";
  if (score >= 55) return "text-amber-500";
  return "text-rose-500";
}

function scoreBar(score) {
  if (score >= 80) return "bg-emerald-500";
  if (score >= 55) return "bg-amber-400";
  return "bg-rose-500";
}

async function loadAiComment() {
  aiLoading.value = true;
  aiError.value = "";
  try {
    const response = await api.post(`/stocks/${props.ticker}/ai-comment/`, { risk_type: "neutral" });
    aiComment.value = response.data;
  } catch (err) {
    aiError.value = "AI 코멘트를 생성하지 못했습니다. 잠시 후 다시 시도하세요.";
  } finally {
    aiLoading.value = false;
  }
}

const IndicatorSection = defineComponent({
  props: {
    title: { type: String, required: true },
    items: { type: Array, default: () => [] },
  },
  setup(sectionProps) {
    return () =>
      h("section", { class: "panel p-5" }, [
        h("h2", { class: "border-l-4 border-emerald-500 pl-3 text-2xl font-black text-slate-950" }, sectionProps.title),
        h(
          "div",
          { class: "mt-5 space-y-3" },
          sectionProps.items.map((item) =>
            h("div", { class: "flex items-center justify-between gap-4 rounded-lg border border-slate-100 p-4" }, [
              h("div", [
                h("p", { class: "font-black text-slate-800" }, item.name),
                h("p", { class: "text-sm text-slate-500" }, item.description),
              ]),
              h("div", { class: "text-right" }, [
                h("p", { class: "text-lg font-black text-slate-950" }, item.value),
                h("p", { class: "text-sm font-bold text-emerald-600" }, item.status),
              ]),
            ]),
          ),
        ),
      ]);
  },
});

onMounted(async () => {
  try {
    const response = await api.get(`/stocks/${props.ticker}/report/`);
    report.value = response.data;
  } catch (err) {
    error.value = "종목 리포트를 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
});
</script>
