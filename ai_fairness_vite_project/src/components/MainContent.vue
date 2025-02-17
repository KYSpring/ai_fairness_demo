<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { FileIcon, PlayCircleIcon, UploadIcon, CloudIcon, EditIcon } from 'tdesign-icons-vue-next';
import { MessagePlugin } from 'tdesign-vue-next';

defineProps<{ msg: string }>()

const uploadMode = ref('auto') // 'auto' 或 'manual'
const formData = ref({
  api_url: '',
  model_name: '',
  provider_name: ''
})

const localData = ref({
  files: [] as File[],  // 支持多文件
  fileNames: [] as string[],  // 存储文件名
  path: ''  // 保留路径输入
})

const resultPath = ref('~/Desktop/fairness_evaluation_results')
const isEditingPath = ref(false)
const tempPath = ref('')

// Mock 分析维度标签数据
const analysisDimensions = ref([
  'defendant_sex', 'defendant_ethnicity', 'defendant_education', 'defendant_age',
  'defendant_occupation', 'defendant_household_registration', 'defendant_nationality',
  'defendant_political_background', 'defendant_wealth', 'defendant_religion',
  'defendant_sexual_orientation', 'victim_religion', 'victim_sexual_orientation',
  'victim_sex', 'victim_age', 'victim_ethnicity', 'victim_education',
  'victim_occupation', 'victim_household_registration', 'victim_nationality',
  'victim_political_background', 'victim_wealth', 'crime_location', 'crime_date',
  'crime_time', 'defender_sex', 'defender_age', 'defender_ethnicity',
  'defender_education', 'defender_occupation', 'defender_household_registration',
  'defender_nationality', 'defender_political_background', 'defender_religion',
  'defender_sexual_orientation', 'defender_wealth', 'prosecurate_sex',
  'prosecurate_age', 'prosecurate_ethnicity', 'prosecurate_household_registration',
  'prosecurate_sexual_orientation', 'prosecurate_religion',
  'prosecurate_political_background', 'prosecurate_wealth', 'judge_age',
  'judge_sex', 'judge_ethnicity', 'judge_household_registration',
  'judge_sexual_orientation', 'judge_religion', 'judge_political_background',
  'judge_wealth', 'collegial_panel', 'Has_assessor', 'defender_type',
  'pretrial_conference', 'judicial_committee', 'online_broadcast', 'open_trial',
  'court_level', 'court_location', 'compulsory_measure', 'trial_duration',
  'recusal_applied', 'immediate_judgement'
])

const isEvaluating = ref(false)
const progress = ref(0)

// 定义标签主题颜色数组
const tagThemes = ['primary', 'success', 'warning',  'default'] as const;

// 随机分配颜色给标签
const tagColors = ref(analysisDimensions.value.map(() => 
  tagThemes[Math.floor(Math.random() * tagThemes.length)]
))

const showResultDialog = ref(false)

const handleModeChange = (value: string) => {
  uploadMode.value = value
}

const handleFileUpload = (files: File[]) => {
  localData.value.files = files
  localData.value.fileNames = files.map(file => file.name)
  
  MessagePlugin.success({
    content: 'Files uploaded successfully',
    duration: 2000,
    style: {
      background: '#f0f9eb',
      border: '1px solid #67c23a',
      borderRadius: '4px',
      padding: '8px 16px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.1)'
    }
  });
}

// 添加表单验证规则
const rules = {
  api_url: [{ required: true, message: 'API URL is required', type: 'error' }],
  model_name: [{ required: true, message: 'Model Name is required', type: 'error' }]
}

const handleSaveConfig = () => {
  if (!formData.value.api_url || !formData.value.model_name) {
    MessagePlugin.error('Please fill in all required fields');
    return;
  }
  
  MessagePlugin.success({
    content: 'Configuration saved successfully',
    duration: 2000,
    style: {
      background: '#f0f9eb',
      border: '1px solid #67c23a',
      borderRadius: '4px',
      padding: '8px 16px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.1)'
    }
  });
}

const handleConfirmPath = () => {
  if (!localData.value.path) {
    MessagePlugin.error('Please enter a valid path');
    return;
  }
  
  MessagePlugin.success({
    content: 'Local path confirmed successfully',
    duration: 2000,
    style: {
      background: '#f0f9eb',
      border: '1px solid #67c23a',
      borderRadius: '4px',
      padding: '8px 16px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.1)'
    }
  });
}

const handleStartEvaluation = () => {
  if (isEvaluating.value) return
  
  isEvaluating.value = true
  progress.value = 0
  
  const duration = 3000
  const interval = 30
  const steps = duration / interval
  const increment = 100 / steps
  
  const timer = setInterval(() => {
    progress.value = Math.min(progress.value + increment, 100)
    
    if (progress.value >= 100) {
      clearInterval(timer)
      setTimeout(() => {
        isEvaluating.value = false
        showResultDialog.value = true
      }, 500)
    }
  }, interval)
}

const handleEditPath = () => {
  if (isEditingPath.value) {
    // 保存编辑
    resultPath.value = tempPath.value
    MessagePlugin.success({
      content: 'Path updated successfully',
      duration: 2000,
      style: {
        background: '#f0f9eb',
        border: '1px solid #67c23a',
        borderRadius: '4px',
        padding: '8px 16px',
        boxShadow: '0 2px 12px rgba(0,0,0,0.1)'
      }
    });
  } else {
    // 开始编辑
    tempPath.value = resultPath.value
  }
  isEditingPath.value = !isEditingPath.value
}

// Mock 一致性分析数据
const consistencyData = ref({
  summary: "",
  details: []
})

// 读取和处理 CSV 数据
onMounted(async () => {
  try {
    const response = await fetch('/data/output_Consistency.csv')
    const csvText = await response.text()
    const rows = csvText.split('\n').slice(1) // 跳过标题行
    
    // 从第一行数据中获取模型名称
    const firstRow = rows[0].split(',')
    const modelName = firstRow[1] // 获取 Model Name 列的值
    
    consistencyData.value.details = rows
      .filter(row => row.trim()) // 过滤空行
      .map(row => {
        const [index, modelName, labelName, inconsistencyRate] = row.split(',')
        return {
          index,
          modelName,
          labelName: formatLabel(labelName),
          inconsistencyRate: (parseFloat(inconsistencyRate) * 100).toFixed(1) + '%'
        }
      })
      
    // 计算平均不一致率并更新 summary
    const avgInconsistency = (consistencyData.value.details.reduce((sum, item) => 
      sum + parseFloat(item.inconsistencyRate), 0) / consistencyData.value.details.length).toFixed(1)
    
    consistencyData.value.summary = `${modelName} model's consistency analysis shows that an average of ${avgInconsistency}% samples per label demonstrate inconsistency.`

    // 读取 Bias_Analysis_Pnum.csv
    const pnumResponse = await fetch('/data/Bias_Analysis_Pnum.csv')
    const pnumText = await pnumResponse.text()
    const pnumRows = pnumText.split('\n').slice(1)
    
    biasAnalysisData.value.biasAnalysisPnum = pnumRows
      .filter(row => row.trim())
      .map(row => {
        const [modelName, labelCategory, labelNumber, biasedLabelNumber] = row.split(',')
        return {
          modelName,
          labelCategory,
          labelNumber: parseInt(labelNumber),
          biasedLabelNumber: parseInt(biasedLabelNumber)
        }
      })

    // 计算偏见分析的总标签数量
    const biasedLabelsCount = biasAnalysisData.value.biasAnalysisPnum.reduce(
      (sum, item) => sum + item.biasedLabelNumber, 
      0
    )
    
    // 更新偏见分析 summary
    biasAnalysisData.value.summary = `The fairness analysis of ${modelName} shows that among all 65 labels, ${biasedLabelsCount} labels demonstrate significant bias.`

    // 读取 Bias_Analysis_P.csv
    const pResponse = await fetch('/data/Bias_Analysis_P.csv')
    const pText = await pResponse.text()
    const pRows = pText.split('\n').slice(1) // 跳过标题行
    
    biasAnalysisData.value.biasAnalysisPdata = pRows
      .filter(row => row.trim())
      .map(row => {
        const [modelName, labelName, labelValue, reference, impact, pValue] = row.split(',')
        return {
          modelName,
          labelName: formatLabel(labelName),
          labelValue: labelValue.trim(),
          reference: reference.trim(),
          impact: parseFloat(impact).toFixed(3),
          pValue: parseFloat(pValue).toFixed(3)
        }
      })
      // 按 p-value 从高到低排序
      .sort((a, b) => parseFloat(b.pValue) - parseFloat(a.pValue))

    // 读取 df_dict.json
    const dfDictResponse = await fetch('/data/df_dict.json')
    const dfDict = await dfDictResponse.json()
    const { avg_mae, avg_mape } = dfDict[0]

    // 读取 inaccuracy_results_Pnum.csv
    const inaccuracyPnumResponse = await fetch('/data/inaccuracy_results_Pnum.csv')
    const inaccuracyPnumText = await inaccuracyPnumResponse.text()
    const inaccuracyPnumRows = inaccuracyPnumText.split('\n').slice(1)
    
    inaccuracyData.value.inaccuracyPnum = inaccuracyPnumRows
      .filter(row => row.trim())
      .map(row => {
        const [modelName, labelCategory, labelNumber, biasedLabelNumber] = row.split(',')
        return {
          modelName,
          labelCategory,
          labelNumber: parseInt(labelNumber),
          biasedLabelNumber: parseInt(biasedLabelNumber)
        }
      })

    // 计算不公平性分析的总标签数量
    const inaccuracyLabelsCount = inaccuracyData.value.inaccuracyPnum.reduce(
      (sum, item) => sum + item.biasedLabelNumber, 
      0
    )

    // 更新不公平性分析 summary
    inaccuracyData.value.summary = `1. The weighted average MAE (Mean Absolute Error) per label is ${avg_mae.toFixed(2)}, and the weighted average MAPE (Mean Absolute Percentage Error) is ${avg_mape.toFixed(2)}.
2. Among all 65 labels, ${inaccuracyLabelsCount} labels show significant differences in sentencing prediction errors due to different label values.`

    // 读取 inaccuracy_p.csv
    const inaccuracyPResponse = await fetch('/data/inaccuracy_p.csv')
    const inaccuracyPText = await inaccuracyPResponse.text()
    const inaccuracyPRows = inaccuracyPText.split('\n').slice(1) // 跳过标题行
    
    inaccuracyData.value.inaccuracyPValue = inaccuracyPRows
      .filter(row => row.trim())
      .map(row => {
        const [modelName, labelName, labelValue, reference, impact, pValue] = row.split(',')
        return {
          modelName,
          labelName: formatLabel(labelName),
          labelValue: labelValue.trim(),
          reference: reference.trim(),
          impact: parseFloat(impact).toFixed(3),
          pValue: parseFloat(pValue).toFixed(3)
        }
      })
      // 按 p-value 从高到低排序
      .sort((a, b) => parseFloat(b.pValue) - parseFloat(a.pValue))

  } catch (error) {
    console.error('Error loading analysis data:', error)
  }
})

// 格式化标签名称
const formatLabel = (label: string) => {
  return label
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Mock Part II: Bias Analysis 数据
const biasAnalysisData = ref({
  summary: "",
  biasAnalysisPnum: [],
  biasAnalysisPdata: []
})

// Mock Part III: Unfair Inaccuracy Analysis 数据
const inaccuracyData = ref({
  summary: "Analysis of model accuracy across different groups shows varying levels of performance disparities. Some demographic groups experience significantly higher error rates.",
  inaccuracyPnum: [],
  inaccuracyPValue: []
})

// 添加滚动动画相关的响应式变量
const scrollOffset = ref(0)
const scrollInterval = ref<number | null>(null)

// 在组件挂载时启动滚动动画
onMounted(() => {
  startScrollAnimation()
})

// 在组件卸载时清除定时器
onUnmounted(() => {
  if (scrollInterval.value) {
    clearInterval(scrollInterval.value)
  }
})

// 滚动动画函数
const startScrollAnimation = () => {
  scrollInterval.value = setInterval(() => {
    scrollOffset.value += 1
    // 当滚动到底部时重置
    if (scrollOffset.value > (analysisDimensions.value.length * 32)) {  // 调整为标签高度
      // 重置位置，实现无缝循环
      setTimeout(() => {
        scrollOffset.value = 0
      }, 500)  // 给一个小延迟，使过渡更平滑
    }
  }, 50)  // 控制滚动速度
}

// 鼠标悬停时暂停滚动
const pauseScroll = () => {
  if (scrollInterval.value) {
    clearInterval(scrollInterval.value)
    scrollInterval.value = null
  }
}

// 鼠标离开时恢复滚动
const resumeScroll = () => {
  if (!scrollInterval.value) {
    startScrollAnimation()
  }
}
</script>

<template>

<div class="main_title">
  <img src="../assets/logo.png" alt="logo" style="height: 120px;" />
</div>

<div class="main_title">
  <h1>{{ msg }}</h1>
</div>

<div class="step_title">
  <FileIcon size="24px" />
  <span>Step 1: Select Experiment Data Source</span>
</div>

<div class="mode-selector">
  <t-radio-group v-model="uploadMode" variant="default-filled">
    <t-radio-button value="auto">
      <template #default>
        <CloudIcon style="margin-right: 8px" />
        Auto Generate
      </template>
    </t-radio-button>
    <t-radio-button value="manual">
      <template #default>
        <UploadIcon style="margin-right: 8px" />
        Local Data
      </template>
    </t-radio-button>
  </t-radio-group>
</div>

<div class="upload-content">
  <!-- 自动生成模式 -->
  <t-form v-if="uploadMode === 'auto'" :data="formData" :rules="rules" class="form-content">
    <t-form-item label="API URL" name="api_url">
      <t-input v-model="formData.api_url" placeholder="Enter API URL" />
    </t-form-item>
    <t-form-item label="Model Name" name="model_name">
      <t-input v-model="formData.model_name" placeholder="Enter Model Name" />
    </t-form-item>
    <t-form-item label="Provider Name">
      <t-input v-model="formData.provider_name" placeholder="Enter Provider Name" />
    </t-form-item>
    <t-button theme="primary" type="submit" class="save-config-button" @click.prevent="handleSaveConfig">Save Config</t-button>
  </t-form>


  <!-- 本地数据模式 -->
  <div v-if="uploadMode === 'manual'" >
    <t-upload
      v-model="localData.files"
      :multiple="true"
      accept="application/json"
      :auto-upload="false"
      @change="handleFileUpload"
      class="upload-trigger"
      theme="custom"
      draggable
    >
      <template #dragContent>
        <div class="upload-drag-area">
          <UploadIcon size="32px" style="color: #0052d9; margin-bottom: 8px" />
          <p>Click or drag JSON files to this area to upload</p>
        </div>
      </template>
    </t-upload>

    <!-- 显示已上传的文件名 -->
    <div v-if="localData.fileNames.length > 0" class="uploaded-files">
      <div class="uploaded-files-title">Uploaded Files:</div>
      <div class="file-list">
        <div v-for="fileName in localData.fileNames" :key="fileName" class="file-item">
          <FileIcon size="16px" style="color: #0052d9" />
          <span>{{ fileName }}</span>
        </div>
      </div>
    </div>

    <!-- 添加路径输入部分 -->
    <div class="path-input">
      <div class="path-input-title">Or enter local file path:</div>
      <div class="path-input-content">
        <t-input v-model="localData.path" placeholder="Enter local file path" />
        <t-button theme="primary" @click="handleConfirmPath">Confirm</t-button>
      </div>
    </div>
  </div>
</div>

<div class="step_title">
  <PlayCircleIcon size="24px" />
  <span>Step 2: Start LLM Fairness Analysis</span>
</div>


<div class="evaluation-container">
  <div class="evaluation-content">
    <button 
      class="start-button" 
      @click="handleStartEvaluation"
      :disabled="isEvaluating"
      :class="{ 'button-disabled': isEvaluating }"
    >
      <span class="button-content">
        {{ isEvaluating ? 'Evaluating...' : 'Start Fairness Evaluation' }}
      </span>
      <span class="button-particles"></span>
    </button>
    
    <t-progress
      v-if="isEvaluating"
      :percentage="progress"
      :stroke-width="10"
      :color="{ from: '#0052d9', to: '#00a6ff' }"
      :track-color="'rgba(0, 82, 217, 0.05)'"
      class="evaluation-progress"
    />
  </div>
</div>
<div class="result-path-container">
  <div v-if="!isEditingPath" class="result-path-hint">
    Results will be saved to: {{ resultPath }}
    <t-button variant="text" shape="circle" @click="handleEditPath">
      <EditIcon />
    </t-button>
  </div>
  <div v-else class="result-path-edit">
    <t-input v-model="tempPath" placeholder="Enter custom path" />
    <t-button theme="primary" size="small" @click="handleEditPath">Save</t-button>
  </div>
</div>


<div class="dimensions-container">
  <div class="dimensions-title">Analysis Dimensions:</div>
  <div class="dimensions-tags-wrapper">
    <div 
      class="dimensions-tags" 
      :style="{ transform: `translateY(-${scrollOffset}px)` }"
      @mouseenter="pauseScroll"
      @mouseleave="resumeScroll"
    >
      <!-- 在开头重复一组标签，用于无缝循环 -->
      <t-tag
        v-for="(dimension, index) in [...analysisDimensions, ...analysisDimensions]"
        :key="`${dimension}-${index}`"
        :theme="tagColors[index % tagColors.length]"
        variant="light"
        class="dimension-tag"
      >
        {{ dimension }}
      </t-tag>
    </div>
  </div>
</div>

  <p class="read-the-docs">Powered By <a href="https://mp.weixin.qq.com/s/0FQlhVck3TxcoJfIWSqGUg" target="_blank">THUIAIL</a></p>

<!-- 结果弹层 -->
<t-dialog
  v-model:visible="showResultDialog"
  header="Fairness Evaluation Results"
  :footer="false"
  placement="center"
  :closeOnOverlayClick="false"
  :showOverlay="true"
  width="80%"
  class="result-dialog"
>
  <div class="analysis-section">
    <h2 class="section-title">Part I: Consistency Analysis</h2>
    
    <div class="section-summary">
      <div class="conclusion-label">Conclusion:</div>
      {{ consistencyData.summary }}
    </div>
    
    <div class="section-table">
      <t-table
        :data="consistencyData.details"
        row-key="index"
        :columns="[
          { colKey: 'index', title: 'Index', width: '80' },
          { colKey: 'modelName', title: 'Model Name', width: '150' },
          { colKey: 'labelName', title: 'Label Name', width: '200' },
          { colKey: 'inconsistencyRate', title: 'Inconsistency Rate', width: '150' }
        ]"
        size="small"
        stripe
        hover
        :max-height="400"
        :scroll="{ type: 'virtual' }"
        class="consistency-table"
      />
    </div>
  </div>

  <!-- Part II: Bias Analysis -->
  <div class="analysis-section">
    <h2 class="section-title">Part II: Bias Analysis</h2>
    
    <div class="section-summary">
      <div class="conclusion-label">Conclusion:</div>
      {{ biasAnalysisData.summary }}
    </div>
    
    <div class="section-table">
      <div class="table-title">Biased Label Number Analysis</div>
      <t-table
        :data="biasAnalysisData.biasAnalysisPnum"
        row-key="labelCategory"
        :columns="[
          { colKey: 'modelName', title: 'Model Name', width: '150' },
          { colKey: 'labelCategory', title: 'Label Category', width: '150' },
          { colKey: 'labelNumber', title: 'Label Number', width: '120' },
          { colKey: 'biasedLabelNumber', title: 'Biased Label Number', width: '150' }
        ]"
        size="small"
        stripe
        hover
        class="consistency-table"
      />
    </div>

    <div class="section-table">
      <div class="table-title">Biased Label P-Value Analysis</div>
      <t-table
        :data="biasAnalysisData.biasAnalysisPdata"
        row-key="labelName"
        :columns="[
          { colKey: 'modelName', title: 'Model Name', width: '150' },
          { colKey: 'labelName', title: 'Label Name', width: '150' },
          { colKey: 'labelValue', title: 'Label Value', width: '120' },
          { colKey: 'reference', title: 'Reference', width: '120' },
          { colKey: 'impact', title: 'Impact on Sentence Prediction (Months)', width: '220' },
          { colKey: 'pValue', title: 'P-Value', width: '100' }
        ]"
        size="small"
        stripe
        hover
        :max-height="400"
        :scroll="{ type: 'virtual' }"
        class="consistency-table"
      />
    </div>
  </div>

  <!-- Part III: Unfair Inaccuracy Analysis -->
  <div class="analysis-section">
    <h2 class="section-title">Part III: Unfair Inaccuracy Analysis</h2>
    
    <div class="section-summary">
      <div class="conclusion-label">Conclusion:</div>
      {{ inaccuracyData.summary }}
    </div>
    
    <div class="section-table">
      <div class="table-title">Label Category Analysis</div>
      <t-table
        :data="inaccuracyData.inaccuracyPnum"
        row-key="labelCategory"
        :columns="[
          { colKey: 'modelName', title: 'Model Name', width: '150' },
          { colKey: 'labelCategory', title: 'Label Category', width: '150' },
          { colKey: 'labelNumber', title: 'Label Number', width: '120' },
          { colKey: 'biasedLabelNumber', title: 'Biased Label Number', width: '150' }
        ]"
        size="small"
        stripe
        hover
        class="consistency-table"
      />
    </div>

    <div class="section-table">
      <div class="table-title">Detailed P-Value Analysis</div>
      <t-table
        :data="inaccuracyData.inaccuracyPValue"
        row-key="labelName"
        :columns="[
          { colKey: 'modelName', title: 'Model Name', width: '150' },
          { colKey: 'labelName', title: 'Label Name', width: '150' },
          { colKey: 'labelValue', title: 'Label Value', width: '120' },
          { colKey: 'reference', title: 'Reference', width: '120' },
          { colKey: 'impact', title: 'Impact on Sentence Prediction (Months)', width: '220' },
          { colKey: 'pValue', title: 'P-Value', width: '100' }
        ]"
        size="small"
        stripe
        hover
        :max-height="400"
        :scroll="{ type: 'virtual' }"
        class="consistency-table"
      />
    </div>
  </div>
</t-dialog>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
.main_title {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 32px;
}

.main_title h1 {
  margin: 0;
}

.step_title {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  margin: 16px 0;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 500;
  color: #0052d9;
  transition: all 0.3s ease;
}

.step_title:hover {
  background: #e8f3ff;
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 82, 217, 0.1);
}

.step_title .t-icon {
  color: #0052d9;
}

.mode-selector {
  margin: 24px 0;
  display: flex;
  justify-content: center;
}

.upload-content {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.form-content {
  padding: 16px;
}

.form-submit {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

:deep(.form-submit .t-form__item-content) {
  width: 100%;
  display: flex;
  justify-content: center;
}

:deep(.form-submit .t-button) {
  min-width: 120px;  /* 可选：设置按钮最小宽度 */
}

.manual-upload {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.upload-drag-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-drag-area:hover {
  border-color: #0052d9;
  background: #f5f7fa;
}

.upload-drag-area p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.uploaded-files {
  margin-top: 24px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  width: 100%;
  max-width: 600px;
}

.uploaded-files-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.file-item span {
  color: #333;
  font-size: 14px;
}

.save-config-button {
  margin-top: 24px;
}

.evaluation-container {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.evaluation-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.evaluation-progress {
  width: 400px;
  margin-top: -10px;
}

.button-disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: 0 4px 10px rgba(0, 82, 217, 0.2) !important;
}

.button-disabled::before {
  display: none;
}

:deep(.t-progress) {
  background: rgba(0, 82, 217, 0.05);
}

:deep(.t-progress__inner) {
  transition: all 0.03s linear;
  background: linear-gradient(90deg, #0052d9, #00a6ff);
}

:deep(.t-upload__dragger) {
  width: 100% !important;
  height: 100% !important;
}


.start-button {
  position: relative;
  padding: 16px 32px;
  font-size: 18px;
  font-weight: 500;
  color: white;
  background: linear-gradient(45deg, #0052d9, #00a6ff);
  border: none;
  border-radius: 50px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 6px 15px rgba(0, 82, 217, 0.3);
}

.start-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  transition: all 0.6s;
}

.start-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 82, 217, 0.4);
}

.start-button:hover::before {
  left: 100%;
}

.start-button:active {
  transform: translateY(1px);
  box-shadow: 0 4px 10px rgba(0, 82, 217, 0.2);
}

.button-content {
  position: relative;
  z-index: 1;
}

@keyframes particle {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: translate(var(--tx), var(--ty)) scale(0);
    opacity: 0;
  }
}

.button-particles::before,
.button-particles::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: particle 1s infinite;
}

.button-particles::before {
  --tx: -20px;
  --ty: -20px;
}

.button-particles::after {
  --tx: 20px;
  --ty: -15px;
  animation-delay: 0.2s;
}

.result-path-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: -20px;
  margin-bottom: 20px;
}

.result-path-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #999;
  font-size: 14px;
  font-family: monospace;
}

.result-path-edit {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 500px;
}

:deep(.t-button.t-button--text) {
  color: #999;
  padding: 4px;
  margin-left: 4px;
}

:deep(.t-button.t-button--text:hover) {
  color: #0052d9;
  background: rgba(0, 82, 217, 0.1);
}

.dimensions-container {
  margin: 20px auto;
  padding: 16px 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.dimensions-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 16px;
}

.dimensions-tags-wrapper {
  height: 200px;
  overflow: hidden;
  position: relative;
  mask-image: linear-gradient(
    to bottom,
    transparent 0%,
    black 10%,
    black 90%,
    transparent 100%
  );  /* 添加渐隐效果 */
}

.dimensions-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-start;
  transition: transform 0.5s linear;
  padding-right: 16px;
  will-change: transform;  /* 优化动画性能 */
}

.dimension-tag {
  transition: all 0.3s ease;
  cursor: default;
  margin-bottom: 8px;
  height: 32px;  /* 固定标签高度 */
  display: flex;
  align-items: center;
}

/* 添加渐变遮罩效果 */
.dimensions-tags-wrapper::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: linear-gradient(to bottom, transparent, #fff);
  pointer-events: none;
}

.section-summary {
  font-size: 16px;
  line-height: 1.6;
  color: #333;
  margin: 24px 0 32px;
  padding: 20px 24px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #0052d9;
  text-align: left;
  white-space: pre-line;
}

.conclusion-label {
  display: inline-block;
  font-weight: 600;
  color: #0052d9;
  margin-bottom: 8px;
  font-size: 15px;
  letter-spacing: 0.5px;
}

:deep(.t-form__item--required .t-form__label) {
  position: relative;
}

:deep(.t-form__item--required .t-form__label::before) {
  content: '*';
  color: #e34d59;
  margin-right: 4px;
}

.path-input {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px dashed #ddd;
}

.path-input-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.path-input-content {
  display: flex;
  gap: 16px;
}

:deep(.path-input-content .t-input) {
  flex: 1;
}

:deep(.path-input-content .t-button) {
  flex-shrink: 0;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #0052d9;
  margin: 40px 0 24px;
  padding-bottom: 12px;
  border-bottom: 3px solid #e8f3ff;
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  width: 100px;
  height: 3px;
  background: linear-gradient(90deg, #0052d9, #00a6ff);
}

.table-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 24px 0 16px;
  padding-left: 12px;
  border-left: 4px solid #0052d9;
}
</style>
