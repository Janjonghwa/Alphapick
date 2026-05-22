<template>
  <div class="relative h-[360px] overflow-hidden rounded-lg border border-ink/10 bg-white">
    <div ref="mapEl" class="h-full w-full"></div>
    <div v-if="fallback" class="absolute inset-0 flex flex-col justify-between bg-[linear-gradient(135deg,#f5f7f3,#e4f0eb)] p-5">
      <div>
        <p class="text-sm font-bold text-moss">경로 미리보기</p>
        <h3 class="mt-1 text-2xl font-black">{{ title }}</h3>
      </div>
      <svg class="h-40 w-full" viewBox="0 0 500 180" role="img" aria-label="route preview">
        <polyline points="20,140 110,90 210,112 310,50 470,80" fill="none" stroke="#326454" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" />
        <circle cx="20" cy="140" r="11" fill="#c87941" />
        <circle cx="470" cy="80" r="11" fill="#2c7da0" />
      </svg>
      <p class="text-sm text-ink/65">Kakao 지도 키가 없거나 SDK 로딩 전이면 간단 경로가 표시됩니다.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";

const props = defineProps({
  title: { type: String, default: "OUTFIT course" },
  lat: { type: Number, required: true },
  lng: { type: Number, required: true },
  path: { type: Array, default: () => [] },
  markerOnly: { type: Boolean, default: false },
});

const mapEl = ref(null);
const fallback = ref(false);
let map;

function loadKakao() {
  return new Promise((resolve, reject) => {
    if (!import.meta.env.VITE_KAKAO_MAP_KEY) {
      reject(new Error("missing key"));
      return;
    }
    if (window.kakao?.maps) {
      resolve(window.kakao);
      return;
    }
    const script = document.createElement("script");
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&autoload=false`;
    script.onload = () => window.kakao.maps.load(() => resolve(window.kakao));
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function renderMap() {
  try {
    const kakao = await loadKakao();
    const center = new kakao.maps.LatLng(props.lat, props.lng);
    map = new kakao.maps.Map(mapEl.value, { center, level: 5 });
    new kakao.maps.Marker({ map, position: center });
    if (!props.markerOnly && props.path.length > 1) {
      const linePath = props.path.map(([lng, lat]) => new kakao.maps.LatLng(lat, lng));
      new kakao.maps.Polyline({
        map,
        path: linePath,
        strokeWeight: 6,
        strokeColor: "#326454",
        strokeOpacity: 0.9,
        strokeStyle: "solid",
      });
      const bounds = new kakao.maps.LatLngBounds();
      linePath.forEach((point) => bounds.extend(point));
      map.setBounds(bounds);
    }
    fallback.value = false;
  } catch {
    fallback.value = true;
  }
}

onMounted(renderMap);
watch(() => [props.lat, props.lng, props.path], renderMap, { deep: true });
</script>
