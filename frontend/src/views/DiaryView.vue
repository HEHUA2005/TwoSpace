<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import NavBar from '../components/NavBar.vue'
import ImageModal from '../components/ImageModal.vue'
import api from '../api'

const auth = useAuthStore()

// 列表
const diaries = ref([])
const total = ref(0)
const page = ref(1)
const limit = 20
const loadingList = ref(false)

// 新建/编辑表单
const showForm = ref(false)
const editTarget = ref(null)
const form = ref({ title: '', content: '', mood: 'love', date: '' })

function todayStr() {
  return new Date().toISOString().slice(0, 10)
}
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
  const { data } = await api.get(`/diaries?page=${page.value}&limit=${limit}`)
  diaries.value = data.items
  total.value = data.total
  loadingList.value = false
}

onMounted(loadDiaries)

function openCreate() {
  editTarget.value = null
  form.value = { title: '', content: '', mood: 'love', date: todayStr() }
  showForm.value = true
}

function openEdit(d) {
  editTarget.value = d
  form.value = {
    title: d.title,
    content: d.content,
    mood: d.mood,
    date: d.created_at.slice(0, 10),
  }
  showForm.value = true
}

async function submitForm() {
  if (!form.value.title.trim()) return
  submitting.value = true
  // 将日期字符串转为 ISO datetime（取当天 00:00 本地时间）
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

async function uploadImages(diaryId, files) {
  for (const file of files) {
    const fd = new FormData()
    fd.append('file', file)
    await api.post(`/diaries/${diaryId}/images`, fd)
  }
  await loadDiaries()
}

async function onFileChange(e, diary) {
  const files = [...e.target.files]
  if (!files.length) return
  uploadingImages.value.push(diary.id)
  try {
    await uploadImages(diary.id, files)
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
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="diary-page">
      <div class="page-header">
        <h1>日记</h1>
        <button class="btn btn-primary" @click="openCreate">✏️ 写日记</button>
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
            <input type="date" v-model="form.date" :max="todayStr()" />
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

      <!-- 时间轴 -->
      <div v-if="loadingList" class="loading">加载中...</div>
      <div v-else-if="!diaries.length" class="empty">还没有日记，去写第一篇吧 💕</div>
      <div v-else class="timeline">
        <div v-for="d in diaries" :key="d.id" class="timeline-item">
          <div class="timeline-dot" :class="`mood-dot-${d.mood}`"></div>
          <div class="diary-card card">
            <div class="card-header">
              <div class="card-meta">
                <span :class="['mood-tag', `mood-${d.mood}`]">{{ moodEmoji[d.mood] }}</span>
                <span class="author">{{ d.author_name }}</span>
                <span class="date">{{ formatDate(d.created_at) }}</span>
              </div>
              <div class="card-actions" v-if="canEdit(d)">
                <button class="icon-btn" @click="openEdit(d)" title="编辑">✏️</button>
                <button class="icon-btn" @click="deleteDiary(d)" title="删除">🗑</button>
              </div>
            </div>
            <h3 class="diary-title">{{ d.title }}</h3>
            <p class="diary-content" v-if="d.content">{{ d.content }}</p>

            <!-- 图片网格 -->
            <div class="image-grid" v-if="d.images.length">
              <img
                v-for="(img, idx) in d.images"
                :key="img.id"
                :src="img.url"
                class="diary-img"
                @click="openPreview(d.images, idx)"
              />
              <!-- 删除图片按钮（仅作者） -->
              <template v-if="canEdit(d)">
                <div
                  v-for="img in d.images"
                  :key="`del-${img.id}`"
                  class="img-del-wrap"
                >
                  <button class="img-del-btn" @click.stop="deleteImage(d, img.id)">×</button>
                </div>
              </template>
            </div>

            <!-- 上传图片 -->
            <div class="upload-area" v-if="canEdit(d)">
              <label :class="['upload-btn', { uploading: uploadingImages.includes(d.id) }]">
                <input type="file" accept="image/*" multiple hidden @change="e => onFileChange(e, d)" />
                {{ uploadingImages.includes(d.id) ? '上传中...' : '+ 添加图片' }}
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="total > limit">
        <button class="btn btn-ghost" :disabled="page === 1" @click="page--; loadDiaries()">上一页</button>
        <span>{{ page }} / {{ Math.ceil(total / limit) }}</span>
        <button class="btn btn-ghost" :disabled="page * limit >= total" @click="page++; loadDiaries()">下一页</button>
      </div>
    </main>

    <ImageModal
      v-if="showPreview"
      :images="previewImages"
      :index="previewIndex"
      @close="showPreview = false"
    />
  </div>
</template>

<style scoped>
.page { min-height: 100vh; }
.diary-page { max-width: 720px; margin: 0 auto; padding: 32px 16px 60px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
.page-header h1 { font-size: 24px; font-weight: 700; }
.empty { text-align: center; padding: 60px; color: var(--text-muted); }

/* 时间轴 */
.timeline { position: relative; padding-left: 24px; }
.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, var(--pink), transparent);
}
.timeline-item { position: relative; margin-bottom: 28px; }
.timeline-dot {
  position: absolute;
  left: -20px;
  top: 20px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #fff;
}
.mood-dot-love  { background: var(--pink-dark); }
.mood-dot-happy { background: #f59e0b; }
.mood-dot-sad   { background: #60a5fa; }

.diary-card { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-meta { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text-muted); }
.card-actions { display: flex; gap: 4px; }
.icon-btn { background: none; font-size: 15px; padding: 4px; border-radius: 6px; transition: background 0.15s; }
.icon-btn:hover { background: var(--pink-light); }
.diary-title { font-size: 17px; font-weight: 600; margin-bottom: 10px; }
.diary-content { font-size: 14px; line-height: 1.8; color: var(--text); white-space: pre-wrap; margin-bottom: 14px; }

/* 图片 */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}
.diary-img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.2s;
}
.diary-img:hover { transform: scale(1.03); }

.upload-area { margin-top: 8px; }
.upload-btn {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 13px;
  background: var(--pink-light);
  color: var(--pink-dark);
  cursor: pointer;
  transition: background 0.2s;
}
.upload-btn:hover { background: #f9d4e5; }
.upload-btn.uploading { opacity: 0.6; cursor: not-allowed; }

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 16px;
}
.modal {
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
}
.modal h2 { font-size: 18px; font-weight: 600; margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
.mood-select { display: flex; gap: 8px; }
.mood-btn {
  flex: 1;
  padding: 8px;
  border-radius: 10px;
  font-size: 13px;
  background: var(--pink-light);
  color: var(--text);
  transition: all 0.2s;
}
.mood-btn.active { background: var(--pink-dark); color: #fff; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 32px; }
</style>
