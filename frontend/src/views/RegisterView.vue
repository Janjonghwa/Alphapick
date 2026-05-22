<template>
  <section class="page-shell flex min-h-[calc(100vh-65px)] items-center justify-center py-8">
    <form class="panel w-full max-w-xl p-6" @submit.prevent="submit">
      <h1 class="text-3xl font-black">회원가입</h1>
      <div class="mt-6 grid gap-4 md:grid-cols-2">
        <label class="block text-sm font-bold">아이디<input v-model="form.username" class="field mt-2" required /></label>
        <label class="block text-sm font-bold">닉네임<input v-model="form.nickname" class="field mt-2" /></label>
        <label class="block text-sm font-bold md:col-span-2">이메일<input v-model="form.email" class="field mt-2" type="email" /></label>
        <label class="block text-sm font-bold md:col-span-2">비밀번호<input v-model="form.password" class="field mt-2" type="password" minlength="8" required /></label>
      </div>
      <p v-if="error" class="mt-4 text-sm font-bold text-red-600">{{ error }}</p>
      <button class="btn-primary mt-6 w-full" type="submit">가입하고 시작</button>
    </form>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const error = ref("");
const form = reactive({
  username: "",
  email: "",
  password: "",
  nickname: "",
  level: "EASY",
  preferred_location: "",
  preferred_categories: [],
});

async function submit() {
  error.value = "";
  try {
    await auth.register(form);
    router.push("/onboarding");
  } catch {
    error.value = "가입 정보를 확인해 주세요.";
  }
}
</script>
