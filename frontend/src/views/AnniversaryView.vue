<script setup>
import { ref, onMounted } from 'vue'
import NavBar from '../components/NavBar.vue'
import api from '../api'

const anniversaries = ref([])
const loading = ref(false)
const showForm = ref(false)
const form = ref({ title: '', date: '', is_yearly: true })
const submitting = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  const { data } = await api.get('/anniversaries')
  anniversaries.value = data.sort((a, b) => a.days_until_next - b.days_until_next)
  loading.value = false
}

onMounted(load)

async function submit() {
  if (!form.value.title.trim() || !form.value.date) return
  submitting.value = true
  error.value = ''
  try {
    await api.post('/anniversaries', form.value)
    showForm.value = false
    form.value = { title: '', date: '', is_yearly: true }
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败，请重试'
  } finally {
    submitting.value = false
  }
}

async function remove(a) {
  if (!confirm(`确定删除「${a.title}」？`)) return
  await api.delete(`/anniversaries/${a.id}`)
  await load()
}

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

function daysLabel(n) {
  if (n === 0) return '就是今天 🎉'
  if (n === 1) return '明天'
  return `还有 ${n} 天`
}
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="ann-page">
      <div class="page-header">
        <h1>纪念日</h1>
        <button class="btn btn-primary" @click="showForm = true">+ 添加</button>
      </div>

      <!-- 表单弹窗 -->
      <div class="modal-overlay" v-if="showForm" @click.self="showForm = false">
        <div class="modal card">
          <h2>添加纪念日</h2>
          <div class="form-group">
            <label>名称</label>
            <input v-model="form.title" placeholder="我们在一起的日子" />
          </div>
          <div class="form-group">
            <label>日期</label>
            <input type="date" v-model="form.date" />
          </div>
          <div class="form-group toggle-group">
            <label>每年重复</label>
            <button
              :class="['toggle-btn', { on: form.is_yearly }]"
              @click="form.is_yearly = !form.is_yearly"
            >{{ form.is_yearly ? '是' : '否' }}</button>
          </div>
          <div class="form-actions">
            <p v-if="error" class="form-error">{{ error }}</p>
            <button class="btn btn-ghost" @click="showForm = false">取消</button>
            <button class="btn btn-primary" @click="submit" :disabled="submitting">
              {{ submitting ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
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
            <button class="btn btn-danger del-btn" @click="remove(a)">删除</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; }
.ann-page { max-width: 680px; margin: 0 auto; padding: 32px 16px 60px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
.page-header h1 { font-size: 24px; font-weight: 700; }
.empty { text-align: center; padding: 60px; color: var(--text-muted); }

.ann-list { display: flex; flex-direction: column; gap: 16px; }
.ann-card { padding: 20px 24px; }
.ann-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.ann-title { font-size: 17px; font-weight: 600; margin-bottom: 4px; }
.ann-date { font-size: 13px; color: var(--text-muted); }
.ann-passed { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

.ann-countdown {
  text-align: center;
  min-width: 72px;
  padding: 12px;
  background: var(--pink-light);
  border-radius: 12px;
}
.ann-countdown.today { background: #fde8f1; }
.countdown-num { display: block; font-size: 32px; font-weight: 800; color: var(--pink-dark); line-height: 1; }
.today-icon { font-size: 28px; }
.countdown-label { font-size: 12px; color: var(--text-muted); margin-top: 2px; display: block; }

.ann-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid #f9d4e5; }
.next-date { font-size: 13px; color: var(--text-muted); }
.del-btn { padding: 5px 12px; font-size: 12px; }

/* 弹窗 */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 16px;
}
.modal { width: 100%; max-width: 400px; }
.modal h2 { font-size: 18px; font-weight: 600; margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
.toggle-group { display: flex; align-items: center; justify-content: space-between; }
.toggle-group label { margin: 0; }
.toggle-btn {
  padding: 6px 18px;
  border-radius: 50px;
  font-size: 13px;
  background: #f0f0f0;
  color: var(--text-muted);
  transition: all 0.2s;
}
.toggle-btn.on { background: var(--pink-dark); color: #fff; }
.form-actions { display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
.form-error { flex: 1 1 100%; color: #dc2626; font-size: 13px; margin-bottom: 4px; }
</style>
