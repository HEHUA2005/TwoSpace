<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  images: { type: Array, required: true },
  index:  { type: Number, default: 0 },
})
const emit = defineEmits(['close'])

const current = ref(props.index)

watch(() => props.index, v => { current.value = v })

function prev() { current.value = (current.value - 1 + props.images.length) % props.images.length }
function next() { current.value = (current.value + 1) % props.images.length }

function onKey(e) {
  if (e.key === 'ArrowLeft') prev()
  if (e.key === 'ArrowRight') next()
  if (e.key === 'Escape') emit('close')
}

function download() {
  const a = document.createElement('a')
  a.href = props.images[current.value]
  a.download = props.images[current.value].split('/').pop()
  a.click()
}
</script>

<template>
  <div class="overlay" @click.self="emit('close')" @keydown="onKey" tabindex="0" ref="el">
    <div class="modal">
      <button class="close-btn" @click="emit('close')">✕</button>
      <button class="nav-btn left" @click="prev" v-if="images.length > 1">‹</button>
      <img :src="images[current]" class="preview-img" />
      <button class="nav-btn right" @click="next" v-if="images.length > 1">›</button>
      <div class="toolbar">
        <span class="counter" v-if="images.length > 1">{{ current + 1 }} / {{ images.length }}</span>
        <button class="btn btn-ghost dl-btn" @click="download">⬇ 下载</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal { position: relative; max-width: 90vw; max-height: 90vh; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.preview-img { max-width: 90vw; max-height: 80vh; object-fit: contain; border-radius: 8px; }
.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(255,255,255,0.2);
  color: #fff;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.2);
  color: #fff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.nav-btn:hover { background: rgba(255,255,255,0.35); }
.nav-btn.left { left: -52px; }
.nav-btn.right { right: -52px; }
.toolbar { display: flex; align-items: center; gap: 12px; }
.counter { color: rgba(255,255,255,0.7); font-size: 14px; }
.dl-btn { background: rgba(255,255,255,0.15); color: #fff; font-size: 13px; padding: 6px 14px; }
.dl-btn:hover { background: rgba(255,255,255,0.25); }
</style>
