<template>
  <RouterView v-slot="{ Component }">
    <transition name="page">
      <component :is="Component" />
    </transition>
  </RouterView>
</template>

<style>
.page-enter-active { animation: fadeIn 0.25s ease; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
