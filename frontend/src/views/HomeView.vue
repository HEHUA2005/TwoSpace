<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import AnniversaryBanner from '../components/AnniversaryBanner.vue'
import api from '../api'

const router = useRouter()
const config = ref(null)
const recentDiaries = ref([])
const todayAnniversaries = ref([])

onMounted(async () => {
  // 各请求独立捕获，任一失败不影响其他
  try {
    const { data } = await api.get('/config')
    config.value = data
  } catch (e) {
    console.error('config 加载失败', e)
  }

  try {
    const { data } = await api.get('/diaries?page=1&limit=10')
    recentDiaries.value = data.items
  } catch (e) {
    console.error('日记加载失败', e)
  }

  try {
    const { data } = await api.get('/anniversaries')
    todayAnniversaries.value = data.filter(a => a.days_until_next === 0)
  } catch (e) {
    console.error('纪念日加载失败', e)
  }

  // 等 DOM 更新后再挂载 Observer
  await nextTick()

  // 滚动渐显
  const revealObs = new IntersectionObserver(
    entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible') }),
    { threshold: 0.12 }
  )
  document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el))
})

const moodEmoji = { happy: '😊', sad: '😢', love: '💕' }
const moodLabel = { happy: '开心', sad: '难过', love: '甜蜜' }

function formatDate(dt) {
  return new Date(dt).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
}
</script>

<template>
  <div class="page">
    <NavBar />

    <!-- 纪念日广播 -->
    <AnniversaryBanner :anniversaries="todayAnniversaries" />

    <main class="home" v-if="config">

      <!-- Hero 区 -->
      <section class="hero reveal">
        <!-- 装饰浮动爱心 -->
        <span class="deco deco-1">💗</span>
        <span class="deco deco-2">✨</span>
        <span class="deco deco-3">💗</span>

        <div class="days-badge">
          <span class="days-num">{{ config.love_days }}</span>
          <span class="days-label">天</span>
        </div>
        <p class="days-sub">我们在一起已经 {{ config.love_days }} 天了</p>
        <p class="quote">"{{ config.quote }}"</p>
      </section>

      <!-- 合照 -->
      <section class="photo-section reveal">
        <div class="couple-photo card">
          <img :src="config.couple_photo" alt="我们" @error="e => e.target.style.display='none'" />
        </div>
      </section>

      <!-- 快捷入口 -->
      <section class="shortcuts reveal">
        <button class="shortcut-btn card" @click="router.push('/diary')">
          <span class="sc-icon">📖</span>
          <span>写日记</span>
        </button>
        <button class="shortcut-btn card" @click="router.push('/gallery')">
          <span class="sc-icon">🖼</span>
          <span>相册</span>
        </button>
      </section>

      <!-- 最近日记（大图卡片流） -->
      <section class="recent" v-if="recentDiaries.length">
        <h2 class="section-title reveal">最近记录</h2>
        <div class="diary-feed">
          <div
            v-for="d in recentDiaries"
            :key="d.id"
            class="feed-card card reveal"
            @click="router.push('/diary')"
          >
            <!-- 封面图 -->
            <div class="feed-cover" :class="{ 'no-img': !d.images.length }">
              <img
                v-if="d.images.length"
                :src="d.images[0].url"
                :alt="d.title"
                loading="lazy"
              />
              <div v-else class="cover-placeholder">
                <span>{{ moodEmoji[d.mood] }}</span>
              </div>
            </div>
            <!-- 内容 -->
            <div class="feed-body">
              <div class="feed-meta">
                <span :class="['mood-tag', `mood-${d.mood}`]">{{ moodEmoji[d.mood] }} {{ moodLabel[d.mood] }}</span>
                <span class="feed-author">{{ d.author_name }}</span>
                <span class="feed-date">{{ formatDate(d.created_at) }}</span>
              </div>
              <h3 class="feed-title">{{ d.title }}</h3>
              <p class="feed-preview" v-if="d.content">
                {{ d.content.slice(0, 80) }}{{ d.content.length > 80 ? '...' : '' }}
              </p>
            </div>
          </div>
        </div>
      </section>

    </main>

    <div v-else class="loading">加载中...</div>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; }
.home { max-width: 680px; margin: 0 auto; padding: 24px 16px 60px; }

/* ── Hero ───────────────────────────────────────── */
.hero {
  text-align: center;
  padding: 48px 0 28px;
  position: relative;
  overflow: hidden;
}
.deco {
  position: absolute;
  font-size: 22px;
  animation: float-deco 4s ease-in-out infinite alternate;
  pointer-events: none;
  opacity: 0.6;
}
.deco-1 { top: 16px; left: 8%;  animation-delay: 0s; }
.deco-2 { top: 28px; right: 12%; animation-delay: 1s; font-size: 16px; }
.deco-3 { bottom: 20px; left: 20%; animation-delay: 2s; font-size: 16px; }

@keyframes float-deco {
  from { transform: translateY(0) rotate(-8deg); }
  to   { transform: translateY(-10px) rotate(8deg); }
}

.days-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  background: linear-gradient(135deg, var(--pink-dark), #f472b6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.days-num { font-size: 88px; font-weight: 800; line-height: 1; }
.days-label { font-size: 30px; font-weight: 600; }
.days-sub { color: var(--text-muted); margin-top: 8px; font-size: 15px; }
.quote {
  margin-top: 18px;
  font-size: 15px;
  color: var(--text);
  font-style: italic;
  padding: 12px 24px;
  background: linear-gradient(135deg, rgba(253,232,241,0.8), rgba(237,233,254,0.6));
  border-radius: 50px;
  display: inline-block;
  border: 1px solid rgba(232,116,158,0.2);
}

/* ── 合照 ───────────────────────────────────────── */
.photo-section { margin: 20px 0; }
.couple-photo { padding: 8px; overflow: hidden; }
.couple-photo img {
  width: 100%;
  border-radius: 12px;
  object-fit: cover;
  max-height: 420px;
  display: block;
}

/* ── 快捷入口 ───────────────────────────────────── */
.shortcuts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin: 20px 0;
}
.shortcut-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  transition: all 0.25s;
}
.shortcut-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(232,116,158,0.22);
}
.sc-icon { font-size: 28px; }

/* ── 日记大图卡片流 ──────────────────────────────── */
.section-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; color: var(--text); }
.diary-feed { display: flex; flex-direction: column; gap: 16px; }

.feed-card {
  padding: 0;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.25s, box-shadow 0.25s;
}
.feed-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px rgba(232,116,158,0.18);
}

.feed-cover {
  width: 100%;
  aspect-ratio: 16 / 7;
  overflow: hidden;
  background: linear-gradient(135deg, #fde8f1, #ede9fe);
}
.feed-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s;
}
.feed-card:hover .feed-cover img { transform: scale(1.04); }
.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  opacity: 0.5;
}

.feed-body { padding: 14px 18px 16px; }
.feed-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.feed-author, .feed-date { font-size: 12px; color: var(--text-muted); }
.feed-title { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
.feed-preview { font-size: 13px; color: var(--text-muted); line-height: 1.7; }

/* ── 哨兵 ───────────────────────────────────────── */
</style>
