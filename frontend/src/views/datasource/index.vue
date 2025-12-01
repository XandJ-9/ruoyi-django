<!-- eslint-disable vue/no-v-model-argument -->
<template>
  <div class="app-container">
    <!-- 搜索栏 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true">
      <el-form-item label="数据源名称" prop="dataSourceName">
        <el-input v-model="queryParams.dataSourceName" placeholder="请输入数据源名称" clearable style="width: 200px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="数据库类型" prop="dbType">
        <el-select v-model="queryParams.dbType" placeholder="请选择数据库类型" clearable style="width: 200px">
          <el-option v-for="item in dbTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 200px">
          <el-option v-for="dict in sys_normal_disable" :key="dict.value" :label="dict.label" :value="dict.value" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 工具栏 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['system:datasource:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" plain icon="Edit" :disabled="single" @click="handleUpdate" v-hasPermi="['system:datasource:edit']">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['system:datasource:remove']">删除</el-button>
      </el-col>
      <right-toolbar
        :showSearch="showSearch"
        @update:showSearch="val => (showSearch = val)"
        @queryTable="getList"
      ></right-toolbar>
    </el-row>

    <!-- 列表 -->
    <el-table v-loading="loading" :data="dataList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="数据源名称" prop="dataSourceName" :show-overflow-tooltip="true" />
      <el-table-column label="数据库类型" prop="dbType" width="120" />
      <el-table-column label="主机" prop="host" :show-overflow-tooltip="true" />
      <el-table-column label="端口" prop="port" width="90" />
      <el-table-column label="数据库" prop="dbName" :show-overflow-tooltip="true" />
      <el-table-column label="用户名" prop="username" :show-overflow-tooltip="true" />
      <el-table-column label="状态" align="center" prop="status" width="90">
        <template #default="scope">
          <dict-tag :options="sys_normal_disable" :value="scope.row.status" />
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="220" fixed="right">
        <template #default="scope">
          <el-button link type="warning" icon="Link" @click="handleTest(scope.row)" v-hasPermi="['system:datasource:test']">测试</el-button>
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:datasource:edit']">修改</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:datasource:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <pagination
      v-show="total > 0"
      :total="total"
      :page="queryParams.pageNum"
      :limit="queryParams.pageSize"
      @update:page="val => (queryParams.pageNum = val)"
      @update:limit="val => (queryParams.pageSize = val)"
      @pagination="getList"
    />

    <!-- 新增/修改弹窗 -->
    <el-dialog :title="title" v-model="open" width="700px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数据源名称" prop="dataSourceName">
              <el-input v-model="form.dataSourceName" placeholder="请输入数据源名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数据库类型" prop="dbType">
              <el-select v-model="form.dbType" placeholder="请选择数据库类型">
                <el-option v-for="item in dbTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主机" prop="host">
              <el-input v-model="form.host" placeholder="示例：127.0.0.1 或 rds.example.com" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="端口" prop="port">
              <el-input-number v-model="form.port" :min="0" :max="65535" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数据库名" prop="dbName">
              <el-input v-model="form.dbName" placeholder="请输入数据库名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" placeholder="不改留空" type="password" show-password />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio v-for="dict in sys_normal_disable" :key="dict.value" :value="dict.value">{{ dict.label }}</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="连接参数" prop="params">
              <el-input v-model="form.params" type="textarea" :rows="3" placeholder="可选：JSON 或 key=value&..." />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="备注信息" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="warning" @click="testFormConnection">测试连接</el-button>
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Datasource">
/* eslint-disable vue/no-v-model-argument */
import { listDatasource, getDatasource, addDatasource, updateDatasource, delDatasource, testDatasource, testDatasourceByBody } from '@/api/datasource'

const { proxy } = getCurrentInstance()
const { sys_normal_disable } = proxy.useDict('sys_normal_disable')

const dataList = ref([])
const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const open = ref(false)
const title = ref('')

const dbTypeOptions = ref([
  { value: 'mysql', label: 'MySQL' },
  { value: 'postgres', label: 'PostgreSQL' },
  { value: 'sqlserver', label: 'SQL Server' },
  { value: 'oracle', label: 'Oracle' },
  { value: 'sqlite', label: 'SQLite' }
])

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    dataSourceName: undefined,
    dbType: undefined,
    status: undefined
  },
  rules: {
    dataSourceName: [{ required: true, message: '数据源名称不能为空', trigger: 'blur' }],
    dbType: [{ required: true, message: '数据库类型不能为空', trigger: 'change' }],
    port: [{ type: 'number', message: '端口需为数字', trigger: 'blur' }]
  }
})

const { form, queryParams, rules } = toRefs(data)

function getList() {
  loading.value = true
  listDatasource(queryParams.value).then(response => {
    dataList.value = response.rows
    total.value = response.total
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

function resetQuery() {
  proxy.resetForm('queryRef')
  handleQuery()
}

function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.dataSourceId)
  single.value = selection.length !== 1
  multiple.value = selection.length === 0
}

function reset() {
  form.value = {
    dataSourceId: undefined,
    dataSourceName: undefined,
    dbType: undefined,
    host: undefined,
    port: 0,
    dbName: undefined,
    username: undefined,
    password: undefined,
    params: undefined,
    status: '0',
    remark: undefined
  }
  proxy.resetForm('formRef')
}

function cancel() {
  open.value = false
  reset()
}

function handleAdd() {
  reset()
  open.value = true
  title.value = '添加数据源'
}

function handleUpdate(row) {
  reset()
  const id = row.dataSourceId || ids.value
  getDatasource(id).then(response => {
    form.value = response.data
    // 临时保存旧密码
    form.value.oldPassword = form.value.password
    open.value = true
    title.value = '修改数据源'
  })
}

function submitForm() {
  proxy.$refs['formRef'].validate(valid => {
    if (!valid) return
    if (form.value.dataSourceId !== undefined) {
      updateDatasource(form.value).then(() => {
        proxy.$modal.msgSuccess('修改成功')
        open.value = false
        getList()
      })
    } else {
      addDatasource(form.value).then(() => {
        proxy.$modal.msgSuccess('新增成功')
        open.value = false
        getList()
      })
    }
  })
}

function handleDelete(row) {
  const idsParam = row.dataSourceId || ids.value
  proxy.$modal.confirm('是否确认删除编号为"' + idsParam + '"的数据项？').then(function() {
    return delDatasource(idsParam)
  }).then(() => {
    getList()
    proxy.$modal.msgSuccess('删除成功')
  }).catch(() => {})
}

function testFormConnection() {
  proxy.$refs['formRef'].validate(valid => {
      if (!valid) return
    proxy.$modal.loading('正在测试连通性...')
    console.log(form.value)
    // 如果密码发生改变，则将新密码传参，否则密码为空
    if (form.value.password !== form.value.oldPassword) {
      form.value.passwordIsUpdated = true
    } else {
      form.value.passwordIsUpdated = false
    }
    testDatasourceByBody(form.value).then((res) => {
      proxy.$modal.closeLoading()
      const msg = res?.message || '测试成功'
      proxy.$modal.msgSuccess(msg)
    }).catch((err) => {
      proxy.$modal.closeLoading()
      const msg = err?.message || err?.response?.data?.message || '测试失败'
      proxy.$modal.msgError(msg)
    })
  })
}

function handleTest(row) {
  const id = row.dataSourceId
  if (!id) {
    proxy.$modal.msgError('请选择要测试的数据源')
    return
  }
  proxy.$modal.loading('正在测试连通性...')
  testDatasource(id).then((res) => {
    proxy.$modal.closeLoading()
    const msg = res?.message || '测试成功'
    proxy.$modal.msgSuccess(msg)
  }).catch((err) => {
    proxy.$modal.closeLoading()
    const msg = err?.message || err?.response?.data?.message || '测试失败'
    proxy.$modal.msgError(msg)
  })
}

getList()
</script>

<style scoped>
.mb8 { margin-bottom: 8px; }
</style>