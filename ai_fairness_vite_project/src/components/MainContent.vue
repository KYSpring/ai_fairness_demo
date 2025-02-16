<script setup lang="ts">
import { ref } from 'vue'
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
  file: null,
  path: ''
})

const resultPath = ref('~/Desktop/fairness_evaluation_results')
const isEditingPath = ref(false)
const tempPath = ref('')

// Mock 分析维度标签数据
const analysisDimensions = ref([
  'Gender Bias', 'Age Discrimination', 'Racial Bias', 'Religious Bias',
  'Socioeconomic Bias', 'Educational Bias', 'Geographic Bias', 'Language Bias',
  'Cultural Bias', 'Political Bias', 'Disability Bias', 'Appearance Bias',
  'Nationality Bias', 'Sexual Orientation', 'Marital Status', 'Occupation Bias',
  'Income Level Bias', 'Health Status Bias', 'Family Status', 'Accent Bias',
  'Name Origin Bias', 'Social Class Bias', 'Ethnic Bias', 'Age Group Bias',
  'Veteran Status', 'Citizenship Status', 'Immigration Status', 'Language Proficiency',
  'Digital Literacy', 'Educational Access'
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

const handleFileUpload = (file: File) => {
  console.log('Uploaded file:', file)
}

const handleSaveConfig = () => {
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
</script>

<template>

<div class="main_title">
  <img src="../assets/logo.png" alt="logo" style="height: 70px;" />
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
  <t-form v-if="uploadMode === 'auto'" :data="formData" class="form-content">
    <t-form-item label="API URL">
      <t-input v-model="formData.api_url" placeholder="Enter API URL" />
    </t-form-item>
    <t-form-item label="Model Name">
      <t-input v-model="formData.model_name" placeholder="Enter Model Name" />
    </t-form-item>
    <t-form-item label="Provider Name">
      <t-input v-model="formData.provider_name" placeholder="Enter Provider Name" />
    </t-form-item>
    <t-button theme="primary" type="submit" class="save-config-button" @click.prevent="handleSaveConfig">Save Config</t-button>
  </t-form>


  <!-- 本地数据模式 -->
  <div v-else class="manual-upload">
    <t-upload
      v-model="localData.file"
      theme="custom"
      :draggable="true"
      action="/"
      @change="handleFileUpload"
    >
      <template #default>
        <div class="upload-drag-area">
          <UploadIcon size="24px" />
          <p>Click or drag file to upload</p>
          <p class="upload-hint">Support .json file format</p>
        </div>
      </template>
    </t-upload>
    
    <div class="path-input">
      <t-input v-model="localData.path" placeholder="Or enter local file path" />
      <t-button theme="primary" style="margin-left: 16px" @click="handleConfirmPath">Confirm</t-button>
    </div>
  </div>
</div>

<div class="step_title">
  <PlayCircleIcon size="24px" />
  <span>Step 2: Start LLM Fairness Analysis</span>
</div>

<div class="dimensions-container">
  <div class="dimensions-title">Analysis Dimensions:</div>
  <div class="dimensions-tags">
    <t-tag
      v-for="(dimension, index) in analysisDimensions"
      :key="dimension"
      :theme="tagColors[index]"
      variant="light"
      class="dimension-tag"
    >
      {{ dimension }}
    </t-tag>
  </div>
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
  <div class="evaluation-summary">
    <div class="summary-title">Analysis Summary</div>
    <p class="summary-content">{{ evaluationSummary }}</p>
  </div>
</t-dialog>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
.main_title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin: 20px 0;
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
  padding: 32px;
  border: 2px dashed #dcdcdc;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-drag-area:hover {
  border-color: #0052d9;
  background: #f5f5f5;
}

.upload-hint {
  color: #999;
  font-size: 14px;
  margin-top: 8px;
}

.path-input {
  display: flex;
  align-items: center;
}

:deep(.t-upload__dragger) {
  width: 100%;
  border: none;
  padding: 0;
  height: auto !important;
  overflow: visible !important;
}

:deep(.t-upload-dragger__content) {
  height: auto !important;
}

:deep(.t-upload__tips) {
  display: none;
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
  max-width: 800px;
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

.dimensions-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-start;
}

.dimension-tag {
  transition: all 0.3s ease;
  cursor: default;
}

.dimension-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 82, 217, 0.1);
}

:deep(.dimension-tag.t-tag) {
  padding: 6px 12px;
  border-radius: 16px;
}

:deep(.dimension-tag.t-tag--light) {
  border: none;
}

:deep(.dimension-tag.t-tag--primary.t-tag--light) {
  background-color: rgba(0, 82, 217, 0.1);
}

:deep(.dimension-tag.t-tag--success.t-tag--light) {
  background-color: rgba(0, 171, 88, 0.1);
}

:deep(.dimension-tag.t-tag--warning.t-tag--light) {
  background-color: rgba(255, 171, 0, 0.1);
}

:deep(.dimension-tag.t-tag--error.t-tag--light) {
  background-color: rgba(227, 77, 89, 0.1);
}

:deep(.dimension-tag.t-tag--default.t-tag--light) {
  background-color: rgba(96, 98, 102, 0.1);
}

:deep(.dimension-tag.t-tag--primary.t-tag--light:hover) {
  background-color: rgba(0, 82, 217, 0.15);
}

:deep(.dimension-tag.t-tag--success.t-tag--light:hover) {
  background-color: rgba(0, 171, 88, 0.15);
}

:deep(.dimension-tag.t-tag--warning.t-tag--light:hover) {
  background-color: rgba(255, 171, 0, 0.15);
}

:deep(.dimension-tag.t-tag--error.t-tag--light:hover) {
  background-color: rgba(227, 77, 89, 0.15);
}

:deep(.dimension-tag.t-tag--default.t-tag--light:hover) {
  background-color: rgba(96, 98, 102, 0.15);
}

:deep(.result-dialog) {
  max-width: 1200px;
}

:deep(.result-dialog .t-dialog__header) {
  font-size: 24px;
  font-weight: 500;
  color: #0052d9;
  padding: 24px;
  border-bottom: 1px solid #eee;
}

:deep(.result-dialog .t-dialog__body) {
  padding: 24px;
  min-height: 400px;
}

:deep(.result-dialog .t-dialog__close) {
  top: 24px;
  right: 24px;
}

.evaluation-summary {
  margin-bottom: 32px;
}

.summary-title {
  font-size: 18px;
  font-weight: 500;
  color: #0052d9;
  margin-bottom: 16px;
}

.summary-content {
  font-size: 15px;
  line-height: 1.6;
  color: #333;
  text-align: justify;
}

.evaluation-details {
  margin-top: 24px;
}

.details-title {
  font-size: 18px;
  font-weight: 500;
  color: #0052d9;
  margin-bottom: 16px;
}

:deep(.result-table) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

:deep(.result-table .t-table__header) {
  background: #f5f7fa;
}

:deep(.result-table .t-table__cell) {
  padding: 16px;
}

:deep(.t-tag) {
  min-width: 90px;
  text-align: center;
}
</style>
