<template>
  <section class="mb-4 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
    <div class="grid grid-cols-2 gap-px bg-slate-100 p-px text-[13px] sm:grid-cols-3 xl:grid-cols-6">
      <template v-for="item in macro.items || []" :key="item.key">
        <div class="min-w-0 bg-white px-3 py-3">
          <div class="flex min-w-0 items-baseline justify-center gap-1.5 whitespace-nowrap xl:justify-start">
            <span class="shrink-0 font-bold text-slate-500">{{ item.label }}</span>
            <strong class="min-w-0 font-bold text-[#172033]">{{ formatValue(item) }}</strong>
            <span v-if="hasChange(item)" class="shrink-0 text-xs font-bold" :class="changeClass(item)">
              {{ changeArrow(item) }}{{ Math.abs(Number(item.change || 0)).toFixed(2) }}{{ item.unit || "%" }}
            </span>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { api } from "../api/client";

const macro = ref({ items: [], sentiment: null });

function formatValue(item) {
  const numberValue = Number(item.value || 0);
  const suffix = item.valueSuffix || "";
  if (Math.abs(numberValue) >= 10000) return numberValue.toLocaleString("ko-KR", { maximumFractionDigits: 0 });
  if (Math.abs(numberValue) >= 1000) return `${numberValue.toLocaleString("ko-KR", { maximumFractionDigits: 2 })}${suffix}`;
  return `${numberValue.toLocaleString("ko-KR", { minimumFractionDigits: suffix ? 2 : 0, maximumFractionDigits: 2 })}${suffix}`;
}

function hasChange(item) {
  return item.change !== null && item.change !== undefined;
}

function isPositiveForMarket(item) {
  const change = Number(item.change || 0);
  return item.invert ? change < 0 : change >= 0;
}

function changeClass(item) {
  return isPositiveForMarket(item) ? "text-rose-500" : "text-blue-500";
}

function changeArrow(item) {
  return Number(item.change || 0) >= 0 ? "▲" : "▼";
}

async function loadMarketData() {
  try {
    const macroResponse = await api.get("/market/macro/");
    macro.value = macroResponse.data;
  } catch {
    macro.value = {
      sentiment: { label: "데이터 준비 중", level: "neutral", summary: "시장 데이터를 불러오지 못했습니다." },
      items: [],
    };
  }
}

onMounted(loadMarketData);
</script>
