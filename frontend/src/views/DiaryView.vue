<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import NavBar from '../components/NavBar.vue'
import ImageModal from '../components/ImageModal.vue'
import api from '../api'

const auth = useAuthStore()

const diaries = ref([])
const total = ref(0)
const page = ref(1)
const limit = 20
const loadingList = ref(false)
const order = ref('desc') // 'desc' 最新在前，'asc' 最早在前

// 当前阅读到第几篇（0-based）
const current = ref(0)
const pageRefs = ref([])

// 日历状态
const calYear  = ref(new Date().getFullYear())
const calMonth = ref(new Date().getMonth()) // 0-based

// 日记日期索引 Map: 'YYYY-MM-DD' -> 日记在 diaries 数组中的下标
const diaryDateMap = computed(() => {
  const map = {}
  diaries.value.forEach((d, idx) => {
    const key = d.created_at.slice(0, 10)
    if (!(key in map)) map[key] = idx  // 同一天多篇取第一篇
  })
  return map
})

// 当前日历月的所有格子（含前后补白）
const calDays = computed(() => {
  const year = calYear.value
  const month = calMonth.value
  const firstDay = new Date(year, month, 1).getDay() // 0=Sun
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = []
  // 前补白（周一为第一列，调整 Sunday=0 → 7）
  const startPad = (firstDay === 0 ? 7 : firstDay) - 1
  for (let i = 0; i < startPad; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)
  return cells
})

function calDateKey(day) {
  return `${calYear.value}-${String(calMonth.value + 1).padStart(2,'0')}-${String(day).padStart(2,'0')}`
}

function prevMonth() {
  if (calMonth.value === 0) { calYear.value--; calMonth.value = 11 }
  else calMonth.value--
}
function nextMonth() {
  if (calMonth.value === 11) { calYear.value++; calMonth.value = 0 }
  else calMonth.value++
}

const MONTH_NAMES = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
const WEEK_DAYS   = ['一','二','三','四','五','六','日']

const showSidebar = ref(false)
const showForm = ref(false)
const editTarget = ref(null)
const form = ref({ title: '', content: '', mood: 'love', date: '' })
const submitting = ref(false)
const uploadingImages = ref([])

// 图片预览
const previewImages = ref([])
const previewIndex = ref(0)
const showPreview = ref(false)

const moodOptions = [
  { value: 'love',  label: '💕 甜蜜' },
  { value: 'happy', label: '😊 开心' },
  { value: 'sad',   label: '😢 难过' },
]
const moodEmoji = { happy: '😊', sad: '😢', love: '💕' }

function formatDate(dt) {
  return new Date(dt).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function loadDiaries() {
  loadingList.value = true
  const { data } = await api.get(`/diaries?page=${page.value}&limit=${limit}&order=${order.value}`)
  diaries.value = data.items
  total.value = data.total
  loadingList.value = false
}

async function toggleOrder() {
  order.value = order.value === 'desc' ? 'asc' : 'desc'
  page.value = 1
  current.value = 0
  await loadDiaries()
  // 回到第一篇
  const container = document.querySelector('.diary-scroll')
  container?.scrollTo({ top: 0, behavior: 'instant' })
}

onMounted(() => {
  loadDiaries()

  // 监听滚动，更新当前页索引（用于高亮索引栏）
  const container = document.querySelector('.diary-scroll')
  if (!container) return
  container.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  const container = document.querySelector('.diary-scroll')
  container?.removeEventListener('scroll', onScroll)
})

function onScroll() {
  const container = document.querySelector('.diary-scroll')
  if (!container) return
  const scrollTop = container.scrollTop
  const height = container.clientHeight
  current.value = Math.round(scrollTop / height)
}

function scrollTo(idx) {
  const container = document.querySelector('.diary-scroll')
  if (!container) return
  container.scrollTo({ top: idx * container.clientHeight, behavior: 'smooth' })
}

function openCreate() {
  editTarget.value = null
  form.value = { title: '', content: '', mood: 'love', date: new Date().toISOString().slice(0, 10) }
  showForm.value = true
}

function openEdit(d) {
  editTarget.value = d
  form.value = { title: d.title, content: d.content, mood: d.mood, date: d.created_at.slice(0, 10) }
  showForm.value = true
}

async function submitForm() {
  if (!form.value.title.trim()) return
  submitting.value = true
  const payload = {
    title: form.value.title,
    content: form.value.content,
    mood: form.value.mood,
    created_at: form.value.date ? new Date(form.value.date + 'T00:00:00').toISOString() : undefined,
  }
  try {
    if (editTarget.value) {
      await api.put(`/diaries/${editTarget.value.id}`, payload)
    } else {
      await api.post('/diaries', payload)
    }
    showForm.value = false
    await loadDiaries()
  } finally {
    submitting.value = false
  }
}

async function deleteDiary(d) {
  if (!confirm(`确定删除「${d.title}」？`)) return
  await api.delete(`/diaries/${d.id}`)
  await loadDiaries()
}

async function onFileChange(e, diary) {
  const files = [...e.target.files]
  if (!files.length) return
  uploadingImages.value.push(diary.id)
  try {
    for (const file of files) {
      const fd = new FormData()
      fd.append('file', file)
      await api.post(`/diaries/${diary.id}/images`, fd)
    }
    await loadDiaries()
  } finally {
    uploadingImages.value = uploadingImages.value.filter(id => id !== diary.id)
    e.target.value = ''
  }
}

async function deleteImage(diary, imgId) {
  await api.delete(`/diaries/${diary.id}/images/${imgId}`)
  await loadDiaries()
}

function openPreview(images, idx) {
  previewImages.value = images.map(i => i.url)
  previewIndex.value = idx
  showPreview.value = true
}

const canEdit = (d) => d.author_id === auth.user?.id

// 根据图片数量返回图片网格的 class
function imgGridClass(n) {
  if (n === 1) return 'grid-1'
  if (n === 2) return 'grid-2'
  if (n === 3) return 'grid-3'
  if (n === 4) return 'grid-4'
  if (n === 5) return 'grid-5'
  return 'grid-many'
}

// 加载下一批
async function loadMore() {
  page.value++
  loadingList.value = true
  const { data } = await api.get(`/diaries?page=${page.value}&limit=${limit}&order=${order.value}`)
  diaries.value.push(...data.items)
  total.value = data.total
  loadingList.value = false
}
</script>

<template>
  <div class="page">
    <NavBar />

    <div class="diary-layout">
      <!-- 移动端侧边栏遮罩 -->
      <div class="sidebar-mask" v-if="showSidebar" @click="showSidebar = false"></div>

      <!-- 左侧日历索引 -->
      <aside class="index-bar" :class="{ 'sidebar-open': showSidebar }" v-if="diaries.length">
        <!-- 月份导航 -->
        <div class="cal-header">
          <button class="cal-nav" @click="prevMonth">‹</button>
          <span class="cal-title">{{ calYear }} 年 {{ MONTH_NAMES[calMonth] }}</span>
          <button class="cal-nav" @click="nextMonth">›</button>
        </div>

        <!-- 星期标题 -->
        <div class="cal-weekdays">
          <span v-for="w in WEEK_DAYS" :key="w">{{ w }}</span>
        </div>

        <!-- 日期格子 -->
        <div class="cal-grid">
          <div
            v-for="(day, i) in calDays"
            :key="i"
            :class="[
              'cal-cell',
              {
                empty: !day,
                'has-diary': day && calDateKey(day) in diaryDateMap,
                active: day && diaries[current] && calDateKey(day) === diaries[current].created_at.slice(0,10),
                today: day && calDateKey(day) === new Date().toISOString().slice(0,10),
              }
            ]"
            @click="day && calDateKey(day) in diaryDateMap && scrollTo(diaryDateMap[calDateKey(day)])"
          >
            <span v-if="day">{{ day }}</span>
            <!-- 有日记的圆点 -->
            <span
              v-if="day && calDateKey(day) in diaryDateMap"
              class="cal-dot"
              :class="`dot-${diaries[diaryDateMap[calDateKey(day)]]?.mood}`"
            ></span>
          </div>
        </div>

        <div class="cal-legend">
          <span class="legend-item"><i class="dot-love"></i> 甜蜜</span>
          <span class="legend-item"><i class="dot-happy"></i> 开心</span>
          <span class="legend-item"><i class="dot-sad"></i> 难过</span>
        </div>

        <button class="btn btn-primary write-btn" @click="openCreate">✏️ 写日记</button>
        <button class="order-btn" @click="toggleOrder" :title="order === 'desc' ? '当前：最新在前' : '当前：最早在前'">
          {{ order === 'desc' ? '↓ 最新' : '↑ 最早' }}
        </button>
        <!-- 移动端关闭侧边栏 -->
        <button class="sidebar-close" @click="showSidebar = false">关闭 ×</button>
      </aside>

      <!-- 主内容：全屏分页滚动 -->
      <div class="diary-scroll">

        <!-- 空状态 -->
        <div v-if="!loadingList && !diaries.length" class="empty-page">
          <p>还没有日记，去写第一篇吧 💕</p>
          <button class="btn btn-primary" @click="openCreate">✏️ 写日记</button>
        </div>

        <!-- 每篇日记占一屏 -->
        <div
          v-for="(d, idx) in diaries"
          :key="d.id"
          class="diary-page-item"
        >
          <!-- 顶部信息条 -->
          <div class="dp-header">
            <div class="dp-meta">
              <span :class="['mood-tag', `mood-${d.mood}`]">{{ moodEmoji[d.mood] }}</span>
              <span class="dp-author">{{ d.author_name }}</span>
              <span class="dp-date">{{ formatDate(d.created_at) }}</span>
            </div>
            <div class="dp-actions" v-if="canEdit(d)">
              <button class="icon-btn" @click="openEdit(d)">✏️</button>
              <button class="icon-btn" @click="deleteDiary(d)">🗑</button>
            </div>
          </div>

          <!-- 标题 -->
          <h2 class="dp-title">{{ d.title }}</h2>

          <!-- 内容区：文字 + 图片并排 -->
          <div class="dp-body" :class="{ 'has-images': d.images.length }">
            <!-- 文字 -->
            <p class="dp-content" v-if="d.content">{{ d.content }}</p>
            <p class="dp-content empty-content" v-else>（没有文字）</p>

            <!-- 图片区 -->
            <div
              class="dp-images"
              :class="imgGridClass(d.images.length + (canEdit(d) ? 1 : 0))"
              v-if="d.images.length"
            >
              <div
                v-for="(img, imgIdx) in d.images"
                :key="img.id"
                class="dp-img-wrap"
              >
                <img
                  :src="img.url"
                  class="dp-img"
                  loading="lazy"
                  @click="openPreview(d.images, imgIdx)"
                />
                <button
                  v-if="canEdit(d)"
                  class="dp-img-del"
                  @click.stop="deleteImage(d, img.id)"
                >×</button>
              </div>
              <!-- 上传占位格 -->
              <label v-if="canEdit(d)" :class="['dp-upload', { uploading: uploadingImages.includes(d.id) }]">
                <input type="file" accept="image/*" multiple hidden @change="e => onFileChange(e, d)" />
                <span>+</span>
              </label>
            </div>
          </div>

          <!-- 无图时的上传入口 -->
          <div class="upload-row" v-if="canEdit(d) && !d.images.length">
            <label :class="['upload-btn', { uploading: uploadingImages.includes(d.id) }]">
              <input type="file" accept="image/*" multiple hidden @change="e => onFileChange(e, d)" />
              {{ uploadingImages.includes(d.id) ? '上传中...' : '+ 添加图片' }}
            </label>
          </div>

          <!-- 翻页提示 -->
          <div class="dp-nav">
            <button class="dp-nav-btn" v-if="idx > 0" @click="scrollTo(idx - 1)">↑ 上一篇</button>
            <button
              class="dp-nav-btn dp-nav-next"
              v-if="idx < diaries.length - 1"
              @click="scrollTo(idx + 1)"
            >↓ 下一篇</button>
            <button
              class="dp-nav-btn dp-nav-more"
              v-if="idx === diaries.length - 1 && diaries.length < total"
              @click="loadMore"
              :disabled="loadingList"
            >{{ loadingList ? '加载中...' : '加载更多 ↓' }}</button>
          </div>
        </div>

      </div>
    </div>

    <!-- 表单弹窗 -->
    <div class="modal-overlay" v-if="showForm" @click.self="showForm = false">
      <div class="modal card">
        <h2>{{ editTarget ? '编辑日记' : '新建日记' }}</h2>
        <div class="form-group">
          <label>标题</label>
          <input v-model="form.title" placeholder="今天发生了什么..." />
        </div>
        <div class="form-group">
          <label>心情</label>
          <div class="mood-select">
            <button
              v-for="m in moodOptions"
              :key="m.value"
              :class="['mood-btn', { active: form.mood === m.value }]"
              @click="form.mood = m.value"
            >{{ m.label }}</button>
          </div>
        </div>
        <div class="form-group">
          <label>日期</label>
          <input type="date" v-model="form.date" :max="new Date().toISOString().slice(0,10)" />
        </div>
        <div class="form-group">
          <label>内容</label>
          <textarea v-model="form.content" placeholder="写下你的故事..." rows="6" />
        </div>
        <div class="form-actions">
          <button class="btn btn-ghost" @click="showForm = false">取消</button>
          <button class="btn btn-primary" @click="submitForm" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <ImageModal
      v-if="showPreview"
      :images="previewImages"
      :index="previewIndex"
      @close="showPreview = false"
    />

    <!-- 移动端悬浮按钮组 -->
    <div class="fab-group">
      <button class="fab-write" @click="openCreate">✏️ 写日记</button>
      <button class="fab-calendar" v-if="diaries.length" @click="showSidebar = true">📅</button>
    </div>
  </div>
</template>

<style scoped>
.page { height: 100dvh; display: flex; flex-direction: column; overflow: hidden; }

/* ── 整体布局 ──────────────────────────────────── */
.diary-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ── 左侧日历索引 ──────────────────────────────── */
.index-bar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 20px 14px 16px;
  border-right: 1px solid rgba(249,164,201,0.2);
  background: rgba(255,249,251,0.7);
  backdrop-filter: blur(8px);
  gap: 10px;
}

.cal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.cal-title { font-size: 13px; font-weight: 600; color: var(--text); }
.cal-nav {
  background: none;
  font-size: 18px;
  color: var(--text-muted);
  padding: 2px 6px;
  border-radius: 6px;
  transition: background 0.15s, color 0.15s;
  line-height: 1;
}
.cal-nav:hover { background: var(--pink-light); color: var(--pink-dark); }

.cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
}
.cal-weekdays span { font-size: 10px; color: var(--text-muted); padding: 2px 0; }

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}
.cal-cell {
  position: relative;
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-muted);
  cursor: default;
  transition: background 0.15s;
  user-select: none;
}
.cal-cell.empty { pointer-events: none; }
.cal-cell.today { font-weight: 700; color: var(--text); }
.cal-cell.today > span { text-decoration: underline; text-underline-offset: 2px; }
.cal-cell.has-diary {
  cursor: pointer;
  color: var(--text);
  font-weight: 600;
}
.cal-cell.has-diary:hover { background: var(--pink-light); }
.cal-cell.active {
  background: var(--pink-dark);
  color: #fff;
}
.cal-cell.active .cal-dot { background: #fff !important; }

.cal-dot {
  width: 4px; height: 4px;
  border-radius: 50%;
  position: absolute;
  bottom: 3px;
}
.dot-love  { background: var(--pink-dark); }
.dot-happy { background: #f59e0b; }
.dot-sad   { background: #60a5fa; }

.cal-legend {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 2px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: var(--text-muted);
}
.legend-item i {
  display: inline-block;
  width: 6px; height: 6px;
  border-radius: 50%;
  font-style: normal;
}

.write-btn {
  margin-top: auto;
  justify-content: center;
  font-size: 13px;
  padding: 9px 12px;
}
.order-btn {
  width: 100%;
  padding: 7px 12px;
  border-radius: 10px;
  font-size: 12px;
  color: var(--text-muted);
  background: none;
  border: 1.5px solid #f0d0df;
  transition: all 0.15s;
  margin-top: 6px;
}
.order-btn:hover { background: var(--pink-light); color: var(--pink-dark); border-color: var(--pink); }

/* ── 分页滚动容器 ───────────────────────────────── */
.diary-scroll {
  flex: 1;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}
/* 隐藏滚动条但保留功能 */
.diary-scroll::-webkit-scrollbar { display: none; }
.diary-scroll { scrollbar-width: none; }

/* ── 每篇日记（一屏） ──────────────────────────── */
.diary-page-item {
  height: 100dvh;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  padding: 32px 48px 24px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.empty-page {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  color: var(--text-muted);
  font-size: 16px;
}

/* 顶部信息条 */
.dp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-shrink: 0;
}
.dp-meta { display: flex; align-items: center; gap: 10px; }
.dp-author, .dp-date { font-size: 13px; color: var(--text-muted); }
.dp-actions { display: flex; gap: 4px; }
.icon-btn {
  background: none; font-size: 15px; padding: 4px 6px;
  border-radius: 6px; transition: background 0.15s;
}
.icon-btn:hover { background: var(--pink-light); }

/* 标题 */
.dp-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 16px;
  flex-shrink: 0;
  line-height: 1.3;
}

/* 内容区 */
.dp-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
  min-height: 0;
}
.dp-body.has-images {
  flex-direction: row;
  gap: 24px;
}

/* 文字 */
.dp-content {
  font-size: 15px;
  line-height: 1.9;
  color: var(--text);
  white-space: pre-wrap;
  overflow-y: auto;
  flex: 1;
  min-width: 0;
}
.dp-content::-webkit-scrollbar { width: 4px; }
.empty-content { color: var(--text-muted); font-style: italic; }

/* 图片区 —— 撑满右侧高度 */
.dp-images {
  display: grid;
  gap: 6px;
  /* 宽度和高度由父容器决定 */
  width: 45%;
  flex-shrink: 0;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

/* 1张：单格全占 */
.dp-images.grid-1 {
  grid-template-columns: 1fr;
  grid-template-rows: 1fr;
}

/* 2张：上下两行 */
.dp-images.grid-2 {
  grid-template-columns: 1fr;
  grid-template-rows: 1fr 1fr;
}

/* 3张：左边1大 + 右边2小叠放 */
.dp-images.grid-3 {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
}
.dp-images.grid-3 .dp-img-wrap:first-child,
.dp-images.grid-3 .dp-upload:first-child {
  grid-row: 1 / 3;
}

/* 4张：2×2 */
.dp-images.grid-4 {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
}

/* 5张：左2列 + 右3列各一行，用 2×3 网格，第1格跨行 */
.dp-images.grid-5 {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr 1fr;
}
.dp-images.grid-5 .dp-img-wrap:first-child,
.dp-images.grid-5 .dp-upload:first-child {
  grid-row: 1 / 3;
}

/* 6张及以上：3列，行数自动均分 */
.dp-images.grid-many {
  grid-template-columns: repeat(3, 1fr);
  grid-auto-rows: 1fr;
}

.dp-img-wrap {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  min-height: 0;
}
.dp-img {
  width: 100%; height: 100%;
  object-fit: cover;
  cursor: zoom-in;
  transition: transform 0.25s;
  display: block;
}
.dp-img:hover { transform: scale(1.04); }
.dp-img-del {
  position: absolute;
  top: 5px; right: 5px;
  width: 24px; height: 24px;
  border-radius: 50%;
  background: rgba(0,0,0,0.5);
  color: #fff;
  font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.dp-img-del:hover { background: rgba(220,38,38,0.85); }

/* 上传占位格 */
.dp-upload {
  border-radius: 10px;
  border: 2px dashed #f0d0df;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px;
  color: var(--pink);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  min-height: 0;
}
.dp-upload:hover { border-color: var(--pink-dark); background: var(--pink-light); }
.dp-upload.uploading { opacity: 0.5; cursor: not-allowed; }

/* 无图时上传 */
.upload-row { margin-top: 8px; flex-shrink: 0; }
.upload-btn {
  display: inline-block; padding: 6px 16px;
  border-radius: 50px; font-size: 13px;
  background: var(--pink-light); color: var(--pink-dark);
  cursor: pointer; transition: background 0.2s;
}
.upload-btn:hover { background: #f9d4e5; }
.upload-btn.uploading { opacity: 0.6; cursor: not-allowed; }

/* 翻页按钮 */
.dp-nav {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  flex-shrink: 0;
  justify-content: flex-end;
}
.dp-nav-btn {
  font-size: 13px;
  color: var(--text-muted);
  background: none;
  padding: 4px 10px;
  border-radius: 50px;
  transition: background 0.15s, color 0.15s;
}
.dp-nav-btn:hover { background: var(--pink-light); color: var(--pink-dark); }
.dp-nav-next { color: var(--pink-dark); font-weight: 500; }
.dp-nav-more { color: var(--pink-dark); font-weight: 500; }

/* ── 表单弹窗 ──────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 16px;
}
.modal { width: 100%; max-width: 520px; max-height: 90vh; overflow-y: auto; }
.modal h2 { font-size: 18px; font-weight: 600; margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
.mood-select { display: flex; gap: 8px; }
.mood-btn {
  flex: 1; padding: 8px; border-radius: 10px; font-size: 13px;
  background: var(--pink-light); color: var(--text); transition: all 0.2s;
}
.mood-btn.active { background: var(--pink-dark); color: #fff; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

/* 响应式：窄屏侧边栏改为抽屉 */
.sidebar-mask { display: none; }
.sidebar-close { display: none; }
.fab-group { display: none; }

@media (max-width: 640px) {
  /* 遮罩 */
  .sidebar-mask {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.35);
    z-index: 90;
  }

  /* 侧边栏默认隐藏，滑入时显示 */
  .index-bar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 95;
    width: 240px;
    transform: translateX(-100%);
    transition: transform 0.28s ease;
    box-shadow: 4px 0 24px rgba(232,116,158,0.15);
  }
  .index-bar.sidebar-open {
    transform: translateX(0);
  }

  /* 关闭按钮 */
  .sidebar-close {
    display: block;
    margin-top: 4px;
    width: 100%;
    padding: 8px;
    border-radius: 10px;
    font-size: 13px;
    color: var(--text-muted);
    background: none;
    border: 1.5px solid #f0d0df;
    cursor: pointer;
  }

  .diary-page-item { padding: 16px 18px calc(80px + env(safe-area-inset-bottom)) 18px; }
  .dp-body.has-images { flex-direction: column; }
  .dp-body.has-images .dp-images { width: 100%; height: 45vw; }
  .dp-title { font-size: 20px; }
  .dp-nav { justify-content: center; }

  /* 悬浮按钮组 */
  .fab-group {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 10px;
    position: fixed;
    right: 20px;
    bottom: calc(68px + env(safe-area-inset-bottom));
    z-index: 50;
  }
  .fab-write {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--pink-dark);
    color: #fff;
    border: none;
    border-radius: 50px;
    padding: 12px 20px;
    font-size: 15px;
    font-weight: 600;
    box-shadow: 0 4px 20px rgba(232,116,158,0.45);
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
  }
  .fab-write:active { transform: scale(0.95); }
  .fab-calendar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: rgba(255,249,251,0.95);
    border: 1.5px solid rgba(249,164,201,0.5);
    font-size: 20px;
    box-shadow: 0 2px 12px rgba(232,116,158,0.2);
    cursor: pointer;
    transition: transform 0.15s;
  }
  .fab-calendar:active { transform: scale(0.92); }
}
</style>
