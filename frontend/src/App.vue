<template>
  <div class="min-h-screen bg-fog text-ink">
    <AppHeader />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import AppHeader from "./components/layout/AppHeader.vue";
</script>
