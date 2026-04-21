<script setup>
defineProps({
  anniversaries: { type: Array, required: true }, // days_until_next === 0 的列表
})
</script>

<template>
  <div class="banner-wrap" v-if="anniversaries.length">
    <div
      v-for="a in anniversaries"
      :key="a.id"
      class="banner"
    >
      <span class="fireworks">🎉</span>
      <div class="banner-text">
        <span class="banner-title">今天是「{{ a.title }}」！</span>
        <span class="banner-sub">已经 {{ a.days_passed }} 天了 ✨</span>
      </div>
      <span class="fireworks">🎊</span>
    </div>
  </div>
</template>

<style scoped>
.banner-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 16px;
  max-width: 680px;
  margin: 12px auto 0;
}
.banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, #fde8f1, #fce7f3, #ede9fe);
  border: 1px solid rgba(232, 116, 158, 0.25);
  box-shadow: 0 4px 20px rgba(232, 116, 158, 0.15);
  animation: pulse-banner 2.5s ease-in-out infinite;
}
.fireworks {
  font-size: 22px;
  animation: bounce-fw 1.2s ease-in-out infinite alternate;
}
.fireworks:last-child {
  animation-delay: 0.6s;
}
.banner-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.banner-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--pink-dark);
}
.banner-sub {
  font-size: 13px;
  color: var(--text-muted);
}

@keyframes pulse-banner {
  0%, 100% { box-shadow: 0 4px 20px rgba(232, 116, 158, 0.15); }
  50%       { box-shadow: 0 4px 28px rgba(232, 116, 158, 0.32); }
}
@keyframes bounce-fw {
  from { transform: translateY(0) rotate(-5deg); }
  to   { transform: translateY(-5px) rotate(5deg); }
}
</style>
