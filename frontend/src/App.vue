<template>
  <div class="min-h-screen bg-fog text-ink">
    <AppHeader />
    <main class="lg:pl-[220px]">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import AppHeader from "./components/layout/AppHeader.vue";
</script>
