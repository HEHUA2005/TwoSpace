<script setup>
import { ref, onMounted } from 'vue'
import NavBar from '../components/NavBar.vue'
import ImageModal from '../components/ImageModal.vue'
import api from '../api'

const images = ref([])
const page = ref(1)
const limit = 30
const hasMore = ref(true)
const loading = ref(false)

const previewUrls = ref([])
const previewIdx = ref(0)
const showPreview = ref(false)

async function load(reset = false) {
  if (loading.value) return
  loading.value = true
  if (reset) { page.value = 1; images.value = []; hasMore.value = true }
  const { data } = await api.get(`/gallery?page=${page.value}&limit=${limit}`)
  images.value.push(...data)
  if (data.length < limit) hasMore.value = false
  loading.value = false
}

onMounted(() => load(true))

function loadMore() {
  page.value++
  load()
}

function openPreview(idx) {
  previewUrls.value = images.value.map(i => i.url)
  previewIdx.value = idx
  showPreview.value = true
}
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="gallery-page">
      <div class="page-header">
        <h1>相册</h1>
        <span class="count">{{ images.length }} 张</span>
      </div>

      <div v-if="!images.length && !loading" class="empty">还没有照片，在日记中上传图片吧 🖼</div>

      <!-- 瀑布流 -->
      <div class="masonry" v-else>
        <div
          v-for="(img, idx) in images"
          :key="img.id"
          class="masonry-item"
          @click="openPreview(idx)"
        >
          <img :src="img.url" :alt="img.diary_title" loading="lazy" />
          <div class="img-overlay">
            <span class="img-diary">{{ img.diary_title }}</span>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <div class="load-more" v-if="hasMore && !loading">
        <button class="btn btn-ghost" @click="loadMore">加载更多</button>
      </div>
    </main>

    <ImageModal
      v-if="showPreview"
      :images="previewUrls"
      :index="previewIdx"
      @close="showPreview = false"
    />
  </div>
</template>

<style scoped>
.page { min-height: 100vh; }
.gallery-page { max-width: 1000px; margin: 0 auto; padding: 32px 16px 60px; }
.page-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 24px; }
.page-header h1 { font-size: 24px; font-weight: 700; }
.count { color: var(--text-muted); font-size: 14px; }
.empty { text-align: center; padding: 60px; color: var(--text-muted); }

/* 瀑布流 */
.masonry {
  columns: 3;
  column-gap: 12px;
}
@media (max-width: 600px) { .masonry { columns: 2; } }
.masonry-item {
  break-inside: avoid;
  margin-bottom: 12px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}
.masonry-item img {
  width: 100%;
  display: block;
  border-radius: 12px;
  transition: transform 0.3s;
}
.masonry-item:hover img { transform: scale(1.03); }
.img-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.5));
  padding: 20px 10px 8px;
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 0 0 12px 12px;
}
.masonry-item:hover .img-overlay { opacity: 1; }
.img-diary { color: #fff; font-size: 12px; }

.load-more { text-align: center; margin-top: 24px; }
</style>
