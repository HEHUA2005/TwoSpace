<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import api from '../api'

const router = useRouter()
const config = ref(null)
const recentDiaries = ref([])

onMounted(async () => {
  const [cfgRes, diaryRes] = await Promise.all([
    api.get('/config'),
    api.get('/diaries?page=1&limit=5'),
  ])
  config.value = cfgRes.data
  recentDiaries.value = diaryRes.data.items
})

const moodEmoji = { happy: '😊', sad: '😢', love: '💕' }
const moodLabel = { happy: '开心', sad: '难过', love: '甜蜜' }

function formatDate(dt) {
  return new Date(dt).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="home" v-if="config">
      <!-- 恋爱天数 -->
      <section class="hero">
        <div class="days-badge">
          <span class="days-num">{{ config.love_days }}</span>
          <span class="days-label">天</span>
        </div>
        <p class="days-sub">我们在一起已经 {{ config.love_days }} 天了 💕</p>
        <p class="quote">"{{ config.quote }}"</p>
      </section>

      <!-- 合照 -->
      <section class="photo-section">
        <div class="couple-photo card">
          <img :src="config.couple_photo" alt="我们" @error="e => e.target.style.display='none'" />
        </div>
      </section>

      <!-- 快捷入口 -->
      <section class="shortcuts">
        <button class="shortcut-btn card" @click="router.push('/diary')">
          <span class="sc-icon">📖</span>
          <span>写日记</span>
        </button>
        <button class="shortcut-btn card" @click="router.push('/gallery')">
          <span class="sc-icon">🖼</span>
          <span>相册</span>
        </button>
        <button class="shortcut-btn card" @click="router.push('/anniversary')">
          <span class="sc-icon">🎂</span>
          <span>纪念日</span>
        </button>
      </section>

      <!-- 最近日记 -->
      <section class="recent" v-if="recentDiaries.length">
        <h2 class="section-title">最近记录</h2>
        <div class="diary-list">
          <RouterLink
            to="/diary"
            v-for="d in recentDiaries"
            :key="d.id"
            class="diary-item card"
          >
            <div class="diary-header">
              <span class="diary-title">{{ d.title }}</span>
              <span :class="['mood-tag', `mood-${d.mood}`]">
                {{ moodEmoji[d.mood] }} {{ moodLabel[d.mood] }}
              </span>
            </div>
            <p class="diary-preview">{{ d.content.slice(0, 60) }}{{ d.content.length > 60 ? '...' : '' }}</p>
            <div class="diary-meta">
              <span>{{ d.author_name }}</span>
              <span>{{ formatDate(d.created_at) }}</span>
            </div>
          </RouterLink>
        </div>
        <RouterLink to="/diary" class="btn btn-ghost view-all">查看全部 →</RouterLink>
      </section>
    </main>

    <div v-else class="loading">加载中...</div>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; }
.home { max-width: 680px; margin: 0 auto; padding: 32px 16px 60px; }

.hero { text-align: center; padding: 40px 0 24px; }
.days-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  background: linear-gradient(135deg, var(--pink-dark), #f472b6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.days-num { font-size: 80px; font-weight: 800; line-height: 1; }
.days-label { font-size: 28px; font-weight: 600; }
.days-sub { color: var(--text-muted); margin-top: 8px; }
.quote {
  margin-top: 16px;
  font-size: 16px;
  color: var(--text);
  font-style: italic;
  padding: 12px 20px;
  background: var(--pink-light);
  border-radius: 12px;
  display: inline-block;
}

.photo-section { margin: 24px 0; }
.couple-photo { padding: 8px; overflow: hidden; }
.couple-photo img {
  width: 100%;
  border-radius: 12px;
  object-fit: cover;
  max-height: 400px;
  display: block;
}

.shortcuts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 24px 0;
}
.shortcut-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: var(--card-bg);
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  transition: all 0.2s;
}
.shortcut-btn:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(232,116,158,0.2); }
.sc-icon { font-size: 28px; }

.section-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; color: var(--text); }
.diary-list { display: flex; flex-direction: column; gap: 12px; }
.diary-item {
  display: block;
  padding: 16px 20px;
  transition: all 0.2s;
}
.diary-item:hover { transform: translateX(4px); box-shadow: 0 4px 20px rgba(232,116,158,0.15); }
.diary-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.diary-title { font-weight: 600; font-size: 15px; }
.diary-preview { color: var(--text-muted); font-size: 13px; line-height: 1.6; margin-bottom: 10px; }
.diary-meta { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted); }
.view-all { margin-top: 16px; display: inline-flex; }
</style>
