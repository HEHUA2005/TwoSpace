<script setup>
import { ref, onMounted } from 'vue'
import NavBar from '../components/NavBar.vue'
import api from '../api'

// ── Anniversary ───────────────────────────────────────────────────────────────
const anniversaries = ref([])
const annLoading = ref(false)
const showAnnForm = ref(false)
const annForm = ref({ title: '', date: '', is_yearly: true })
const annSubmitting = ref(false)
const annError = ref('')

async function loadAnn() {
  annLoading.value = true
  const { data } = await api.get('/anniversaries')
  anniversaries.value = data.sort((a, b) => a.days_until_next - b.days_until_next)
  annLoading.value = false
}

async function submitAnn() {
  if (!annForm.value.title.trim() || !annForm.value.date) return
  annSubmitting.value = true
  annError.value = ''
  try {
    await api.post('/anniversaries', annForm.value)
    showAnnForm.value = false
    annForm.value = { title: '', date: '', is_yearly: true }
    await loadAnn()
  } catch (e) {
    annError.value = e.response?.data?.detail || '保存失败，请重试'
  } finally {
    annSubmitting.value = false
  }
}

async function removeAnn(a) {
  if (!confirm(`确定删除「${a.title}」？`)) return
  await api.delete(`/anniversaries/${a.id}`)
  await loadAnn()
}

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// ── Counter ───────────────────────────────────────────────────────────────────
const counters = ref([])
const cntLoading = ref(false)
const showCntForm = ref(false)
const cntForm = ref({ title: '', emoji: '✨' })
const cntSubmitting = ref(false)
const cntError = ref('')

// Confirm increment dialog
const confirmTarget = ref(null) // counter object pending increment

async function loadCnt() {
  cntLoading.value = true
  const { data } = await api.get('/counters')
  counters.value = data
  cntLoading.value = false
}

function askIncrement(c) {
  confirmTarget.value = c
}

async function confirmIncrement() {
  if (!confirmTarget.value) return
  await api.post(`/counters/${confirmTarget.value.id}/increment`)
  confirmTarget.value = null
  await loadCnt()
}

async function submitCnt() {
  if (!cntForm.value.title.trim()) return
  cntSubmitting.value = true
  cntError.value = ''
  try {
    await api.post('/counters', cntForm.value)
    showCntForm.value = false
    cntForm.value = { title: '', emoji: '✨' }
    await loadCnt()
  } catch (e) {
    cntError.value = e.response?.data?.detail || '保存失败，请重试'
  } finally {
    cntSubmitting.value = false
  }
}

async function removeCnt(c) {
  if (!confirm(`确定删除「${c.emoji} ${c.title}」？`)) return
  await api.delete(`/counters/${c.id}`)
  await loadCnt()
}

onMounted(() => {
  loadAnn()
  loadCnt()
})
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="stats-page">

      <!-- ── 纪念日 section ──────────────────────────────────── -->
      <section class="section">
        <div class="section-header">
          <h2>🎂 纪念日</h2>
          <button class="btn btn-primary" @click="showAnnForm = true">+ 添加</button>
        </div>

        <!-- 添加纪念日弹窗 -->
        <div class="modal-overlay" v-if="showAnnForm" @click.self="showAnnForm = false">
          <div class="modal card">
            <h3>添加纪念日</h3>
            <div class="form-group">
              <label>名称</label>
              <input v-model="annForm.title" placeholder="我们在一起的日子" />
            </div>
            <div class="form-group">
              <label>日期</label>
              <input type="date" v-model="annForm.date" />
            </div>
            <div class="form-group toggle-group">
              <label>每年重复</label>
              <button
                :class="['toggle-btn', { on: annForm.is_yearly }]"
                @click="annForm.is_yearly = !annForm.is_yearly"
              >{{ annForm.is_yearly ? '是' : '否' }}</button>
            </div>
            <div class="form-actions">
              <p v-if="annError" class="form-error">{{ annError }}</p>
              <button class="btn btn-ghost" @click="showAnnForm = false">取消</button>
              <button class="btn btn-primary" @click="submitAnn" :disabled="annSubmitting">
                {{ annSubmitting ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="annLoading" class="loading">加载中...</div>
        <div v-else-if="!anniversaries.length" class="empty">还没有纪念日，快来添加吧 🎂</div>
        <div v-else class="ann-list">
          <div v-for="a in anniversaries" :key="a.id" class="ann-card card">
            <div class="ann-main">
              <div class="ann-info">
                <h3 class="ann-title">{{ a.title }}</h3>
                <p class="ann-date">{{ formatDate(a.date) }}{{ a.is_yearly ? ' · 每年' : '' }}</p>
                <p class="ann-passed">已过 {{ a.days_passed }} 天</p>
              </div>
              <div class="ann-countdown" :class="{ today: a.days_until_next === 0 }">
                <span class="countdown-num" v-if="a.days_until_next > 0">{{ a.days_until_next }}</span>
                <span class="countdown-num today-icon" v-else>🎉</span>
                <span class="countdown-label" v-if="a.days_until_next > 0">天后</span>
              </div>
            </div>
            <div class="ann-footer">
              <span class="next-date">下次：{{ formatDate(a.next_date) }}</span>
              <button class="btn btn-danger del-btn" @click="removeAnn(a)">删除</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ── 足迹 section ───────────────────────────────────── -->
      <section class="section">
        <div class="section-header">
          <h2>🌟 足迹</h2>
          <button class="btn btn-primary" @click="showCntForm = true">+ 新增卡片</button>
        </div>

        <!-- 新增卡片弹窗 -->
        <div class="modal-overlay" v-if="showCntForm" @click.self="showCntForm = false">
          <div class="modal card">
            <h3>新增统计卡片</h3>
            <div class="form-group">
              <label>名称</label>
              <input v-model="cntForm.title" placeholder="抱抱" maxlength="30" />
            </div>
            <div class="form-group">
              <label>Emoji</label>
              <input v-model="cntForm.emoji" placeholder="✨" maxlength="4" class="emoji-input" />
            </div>
            <div class="form-actions">
              <p v-if="cntError" class="form-error">{{ cntError }}</p>
              <button class="btn btn-ghost" @click="showCntForm = false">取消</button>
              <button class="btn btn-primary" @click="submitCnt" :disabled="cntSubmitting">
                {{ cntSubmitting ? '保存中...' : '添加' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 确认增加次数弹窗 -->
        <div class="modal-overlay" v-if="confirmTarget" @click.self="confirmTarget = null">
          <div class="modal card confirm-modal">
            <div class="confirm-emoji">{{ confirmTarget.emoji }}</div>
            <p class="confirm-text">记录一次「{{ confirmTarget.title }}」？</p>
            <p class="confirm-count">当前：{{ confirmTarget.count }} 次</p>
            <div class="form-actions">
              <button class="btn btn-ghost" @click="confirmTarget = null">取消</button>
              <button class="btn btn-primary" @click="confirmIncrement">确认 +1</button>
            </div>
          </div>
        </div>

        <div v-if="cntLoading" class="loading">加载中...</div>
        <div v-else-if="!counters.length" class="empty">还没有统计卡片，快来记录你们的足迹吧 🌟</div>
        <div v-else class="cnt-grid">
          <div v-for="c in counters" :key="c.id" class="cnt-card card" @click="askIncrement(c)">
            <button class="del-float" @click.stop="removeCnt(c)" title="删除">×</button>
            <div class="cnt-emoji">{{ c.emoji }}</div>
            <div class="cnt-title">{{ c.title }}</div>
            <div class="cnt-count">{{ c.count }}</div>
            <div class="cnt-label">次</div>
          </div>
        </div>
      </section>

    </main>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; }
.stats-page { max-width: 720px; margin: 0 auto; padding: 32px 16px 80px; display: flex; flex-direction: column; gap: 48px; }

.section {}
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.section-header h2 { font-size: 20px; font-weight: 700; }

.loading { text-align: center; padding: 40px; color: var(--text-muted); }
.empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 15px; }

/* ── Anniversary ── */
.ann-list { display: flex; flex-direction: column; gap: 14px; }
.ann-card { padding: 18px 22px; }
.ann-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.ann-title { font-size: 16px; font-weight: 600; margin-bottom: 3px; }
.ann-date { font-size: 13px; color: var(--text-muted); }
.ann-passed { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.ann-countdown {
  text-align: center; min-width: 68px; padding: 10px 12px;
  background: var(--pink-light); border-radius: 12px;
}
.ann-countdown.today { background: #fde8f1; }
.countdown-num { display: block; font-size: 28px; font-weight: 800; color: var(--pink-dark); line-height: 1; }
.today-icon { font-size: 24px; }
.countdown-label { font-size: 12px; color: var(--text-muted); margin-top: 2px; display: block; }
.ann-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 10px; border-top: 1px solid #f9d4e5; }
.next-date { font-size: 13px; color: var(--text-muted); }
.del-btn { padding: 4px 10px; font-size: 12px; }

/* ── Counter grid ── */
.cnt-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}
.cnt-card {
  position: relative;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 24px 16px 20px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  user-select: none;
  text-align: center;
}
.cnt-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(232, 116, 158, 0.2);
}
.cnt-card:active { transform: scale(0.97); }
.del-float {
  position: absolute; top: 8px; right: 10px;
  background: none; border: none;
  font-size: 16px; color: #ccc; cursor: pointer;
  line-height: 1; padding: 2px 4px;
  transition: color 0.15s;
}
.del-float:hover { color: #e87;  }
.cnt-emoji { font-size: 36px; margin-bottom: 8px; }
.cnt-title { font-size: 14px; font-weight: 600; color: var(--text-dark); margin-bottom: 10px; }
.cnt-count { font-size: 40px; font-weight: 800; color: var(--pink-dark); line-height: 1; }
.cnt-label { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

/* ── Confirm modal ── */
.confirm-modal { text-align: center; padding: 32px 24px; }
.confirm-emoji { font-size: 52px; margin-bottom: 12px; }
.confirm-text { font-size: 18px; font-weight: 600; margin-bottom: 6px; }
.confirm-count { font-size: 14px; color: var(--text-muted); margin-bottom: 20px; }

/* ── Shared modal ── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 16px;
}
.modal { width: 100%; max-width: 400px; }
.modal h3 { font-size: 17px; font-weight: 600; margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
.emoji-input { width: 80px; font-size: 20px; text-align: center; }
.toggle-group { display: flex; align-items: center; justify-content: space-between; }
.toggle-group label { margin: 0; }
.toggle-btn {
  padding: 6px 18px; border-radius: 50px; font-size: 13px;
  background: #f0f0f0; color: var(--text-muted); transition: all 0.2s;
}
.toggle-btn.on { background: var(--pink-dark); color: #fff; }
.form-actions { display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
.form-error { flex: 1 1 100%; color: #dc2626; font-size: 13px; margin-bottom: 4px; }
</style>
