<template>
  <div class="app-container">
    <el-form :inline="true" label-width="80px">
      <el-form-item label="数据源">
        <el-select v-model="currentId" placeholder="选择数据源" style="width: 260px" @change="loadInfo">
          <el-option v-for="ds in dsList" :key="ds.dataSourceId" :label="ds.dataSourceName + ' (' + ds.dbType + ')'" :value="ds.dataSourceId" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="runQuery" :disabled="!currentId || running">执行</el-button>
        <el-button @click="resetResult">清空结果</el-button>
        <el-button type="info" @click="prevPage" :disabled="offset <= 0 || running">上一页</el-button>
        <el-button type="success" @click="nextPage" :disabled="!next || running">下一页</el-button>
      </el-form-item>
      <el-form-item label="每页行数">
        <el-input-number v-model="pageSize" :min="1" :max="1000" />
      </el-form-item>
    </el-form>

    <el-input v-model="sql" type="textarea" :rows="8" placeholder="输入 SQL" />

    <el-table v-loading="running" :data="rows" style="margin-top: 16px">
      <el-table-column v-for="col in columns" :key="col" :prop="col" :label="col" :width="columnWidth(col)" />
    </el-table>
  </div>
</template>

<script setup>
import { listDatasource, executeQueryById } from '@/api/datasource'
const route = useRoute()
const { proxy } = getCurrentInstance()



const currentId = ref(undefined)
const dsList = ref([])
const sql = ref('')
const columns = ref([])
const rows = ref([])
const running = ref(false)
const pageSize = ref(50)
const offset = ref(0)
const next = ref(null)

function getList() {
  listDatasource({ pageNum: 1, pageSize: 100 }).then(res => {
    dsList.value = res.rows || []
  })
}

function loadInfo() {}

function resetResult() {
  columns.value = []
  rows.value = []
  offset.value = 0
  next.value = null
}

function runQuery() {
  if (!currentId.value || !sql.value) return
  running.value = true
  executeQueryById(currentId.value, { sql: sql.value, pageSize: pageSize.value, offset: offset.value }).then(res => {
    const data = res.data || {}
    columns.value = data.columns || []
    rows.value = (data.rows || []).map(r => {
      const obj = {}
      for (let i = 0; i < columns.value.length; i++) obj[columns.value[i]] = r[i]
      return obj
    })
    next.value = data.next || null
  })
  .finally(() => {
    running.value = false
  })
}

function nextPage() {
  if (!next.value) return
  offset.value = Number(next.value.offset || 0)
  runQuery()
}

function prevPage() {
  if (offset.value <= 0) return
  const newOffset = Number(offset.value) - Number(pageSize.value)
  offset.value = newOffset > 0 ? newOffset : 0
  runQuery()
}

// 根据列名计算列宽度
const columnWidth = (columnName) => {
  // return calculateColumnWidth(columnName, {})
  if (rows.value.length === 0) return 200

  let maxWidth = 200
  rows.value.forEach(item => {
      const width = proxy.calculateColumnWidth(item[columnName], {
          minWidth: 150,  // 最小宽度
          maxWidth: 300   // 最大宽度
      })
      maxWidth = Math.max(maxWidth, width)
  })

  return maxWidth
}

onMounted(() => {
  getList()
  const pid = route.params.id
  if (pid) {
    currentId.value = Number(pid)
  }
})
</script>
