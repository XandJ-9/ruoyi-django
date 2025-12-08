<template>
  <div class="code-editor-container" :style="{ height }">
    <div ref="editorRef" class="code-editor"></div>
  </div>
</template>

<script setup>
// 轻量级代码编辑器组件，基于 Ace Editor（本地依赖）
// 特性：多行输入、语法高亮（SQL 等）、基础自动补全（SQL关键字 + 模板占位符）
// 使用：<CodeEditor v-model="text" language="sql" height="260px" />

import { onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
// 本地引入 ace-builds 依赖，不再使用 CDN 加载
import ace from 'ace-builds/src-noconflict/ace'
import 'ace-builds/src-noconflict/ext-language_tools'
import 'ace-builds/src-noconflict/mode-sql'
import 'ace-builds/src-noconflict/theme-github'
// 预加载当前语言的 snippets，避免运行时动态加载导致 basePath 提示
import 'ace-builds/src-noconflict/snippets/sql'
// 可选：如需 worker，可启用以下导入；默认禁用 worker 以减少资源
// import 'ace-builds/src-noconflict/worker-sql'

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: 'sql' },
  height: { type: String, default: '240px' },
  theme: { type: String, default: 'github' },
  placeholder: { type: String, default: '' }
})
const emit = defineEmits(['update:modelValue', 'change'])

const editorRef = ref(null)
let editor = null
let _aceLoaded = false

// function loadScript(src) {
//   return new Promise((resolve, reject) => {
//     const s = document.createElement('script')
//     s.src = src
//     s.onload = resolve
//     s.onerror = reject
//     document.head.appendChild(s)
//   })
// }

// async function ensureAce() {
//   if (window.ace && window.ace.edit) return
//   // 主脚本
//   await loadScript('https://cdn.jsdelivr.net/npm/ace-builds@1.32.3/src-min-noconflict/ace.js')
//   // 语言工具（自动补全）
//   await loadScript('https://cdn.jsdelivr.net/npm/ace-builds@1.32.3/src-min-noconflict/ext-language_tools.js')
//   // 模式与主题（按需加载常用）
//   await loadScript('https://cdn.jsdelivr.net/npm/ace-builds@1.32.3/src-min-noconflict/mode-sql.js')
//   await loadScript('https://cdn.jsdelivr.net/npm/ace-builds@1.32.3/src-min-noconflict/theme-github.js')
// }


function getAceMode(lang) {
  const l = String(lang || '').toLowerCase()
  if (l.includes('sql')) return 'ace/mode/sql'
  return 'ace/mode/sql'
}

function buildCompleter(lang) {
  const sqlKeywords = [
    'SELECT','FROM','WHERE','GROUP BY','ORDER BY','JOIN','LEFT JOIN','RIGHT JOIN',
    'INNER JOIN','OUTER JOIN','ON','LIMIT','OFFSET','INSERT','UPDATE','DELETE',
    'CREATE','ALTER','DROP','DISTINCT','AND','OR','NOT','IN','LIKE','BETWEEN','AS'
  ]
  const tplSnippets = [
    '{{ var }}','{% if condition %}','{% endif %}','{% for item in list %}','{% endfor %}',
    '{{ loop.index }}','{{ item.field }}'
  ]
  const words = [...sqlKeywords, ...tplSnippets]
  return {
    getCompletions(editor, session, pos, prefix, callback) {
      const list = words.map(w => ({
        caption: w,
        value: w,
        meta: 'suggestion'
      }))
      callback(null, list)
    }
  }
}

function initEditor() {
  if (!editorRef.value) return
  editor = ace.edit(editorRef.value)
  editor.session.setMode(getAceMode(props.language))
  editor.setTheme(`ace/theme/${props.theme}`)
  editor.setOptions({
    fontSize: 14,
    showPrintMargin: false,
    wrap: true,
    enableBasicAutocompletion: true,
    enableLiveAutocompletion: true,
    enableSnippets: true
  })
  // 关闭 worker（如需启用，请同时引入对应 worker）
  try { editor.session.setOptions({ useWorker: false }) } catch (_) {}
  // 占位提示
  editor.session.setValue(props.modelValue || '')
  // 光标与选择控制使用 editor.selection / editor API
  try { editor.selection.clearSelection() } catch (_) {}
  try { editor.moveCursorTo(0, 0) } catch (_) {}
  // 使用 Ace 的 placeholder 选项展示占位提示，而不写入实际内容
  if (props.placeholder) {
    try { editor.setOption('placeholder', props.placeholder) } catch (_) {}
  }
  // 自定义补全器
  const langTools = ace.require('ace/ext/language_tools')
  const customCompleter = buildCompleter(props.language)
  langTools.addCompleter(customCompleter)

  editor.session.on('change', () => {
    const val = editor.getValue()
    emit('update:modelValue', val)
    emit('change', val)
  })
}

onMounted(async () => {
  _aceLoaded = true
  nextTick(() => initEditor())
})

onBeforeUnmount(() => {
  if (editor) {
    editor.destroy()
    editor = null
  }
})

watch(() => props.modelValue, (v) => {
  if (!_aceLoaded || !editor) return
  const cur = editor.getValue()
  if (v !== cur) editor.session.setValue(v || '')
})

watch(() => props.language, (l) => {
  if (editor) editor.session.setMode(getAceMode(l))
})
</script>

<style scoped>
.code-editor-container {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
}
.code-editor {
  width: 100%;
  height: 100%;
}
</style>