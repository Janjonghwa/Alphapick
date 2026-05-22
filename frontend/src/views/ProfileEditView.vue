<template>
  <section class="page-shell py-8">
    <form class="panel mx-auto max-w-2xl p-6" @submit.prevent="submit">
      <h1 class="text-3xl font-black">프로필 수정</h1>
      <label class="mt-6 block text-sm font-bold">닉네임<input v-model="form.nickname" class="field mt-2" /></label>
      <label class="mt-4 block text-sm font-bold">운동 레벨
        <select v-model="form.level" class="field mt-2">
          <option value="EASY">쉬움</option>
          <option value="MEDIUM">보통</option>
          <option value="HARD">어려움</option>
        </select>
      </label>
      <label class="mt-4 block text-sm font-bold">선호 지역<input v-model="form.preferred_location" class="field mt-2" /></label>
      <button class="btn-primary mt-6 w-full" type="submit">저장</button>
    </form>
  </section>
</template>

<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const form = reactive({
  nickname: auth.user?.nickname || "",
  level: auth.user?.level || "EASY",
  preferred_location: auth.user?.preferred_location || "",
  onboarding_completed: true,
});

async function submit() {
  await auth.updateMe(form);
  router.push("/me");
}
</script>
