<!-- src/pages/Reports.vue -->
<template>
  <div class="reports-page">
    
    <!-- Header Page Actions -->
    <div class="reports-header">
      <div class="header-left">
        <h1 class="page-title">Аналитические отчеты</h1>
        <p class="page-subtitle">Ежедневная сводка основных изменений</p>
      </div>
      
      <div class="header-actions">
        <button class="btn-action" @click="generateReport">
          <span v-if="isExporting">Генерация отчета...</span>
          <span v-else>Скачать в формате PDF</span>
          <span class="icon">⬇</span>
        </button>
      </div>
    </div>

    <!-- REPORT PREVIEW AREA (A4 Layout) -->
    <!-- Этот ID мы будем скармливать функции экспорта -->
    <div class="report-container-wrapper custom-scroll">
      <div id="report-content" class="a4-sheet">
        
        <!-- Report Header -->
        <div class="rep-header">
          <div class="rep-logo">ОАФИиОСС</div>
          <div class="rep-meta">
            <div class="rep-date">{{ currentDate }}</div>
          </div>
        </div>

        <div class="rep-divider"></div>

        <!-- Title -->
        <h2 class="rep-main-title">Ежедневная оценка рисков</h2>

        <!-- Executive Summary -->
        <section class="rep-section">
          <h3 class="sec-title">1. Краткое резюме</h3>
          <p class="sec-text">
            Портфель демонстрирует умеренную волатильность в текущем рыночном режиме. 
            Показатель <strong>Value-at-Risk (95%)</strong> остается в пределах установленных лимитов (-2.4%). 
            Наблюдается slight negative skewness в распределении доходностей, что указывает на 
            повышенный риск хвостовых событий.
          </p>
        </section>

        <!-- Key Metrics Grid -->
        <section class="rep-section">
          <h3 class="sec-title">2. Ключевые метрики</h3>
          <div class="metrics-grid">
            <div class="metric-box">
              <span class="m-label">Общий P&L (YTD)</span>
              <span class="m-value positive">+12.5%</span>
            </div>
            <div class="metric-box">
              <span class="m-label">Коэффициент Шарпа</span>
              <span class="m-value">1.84</span>
            </div>
            <div class="metric-box">
              <span class="m-label">VaR (95%, 1d)</span>
              <span class="m-value warning">-2.1%</span>
            </div>
            <div class="metric-box">
              <span class="m-label">Beta (β)</span>
              <span class="m-value">0.85</span>
            </div>
          </div>
        </section>

        <!-- Charts Placeholder (Обычно здесь реальные графики) -->
        <section class="rep-section">
          <h3 class="sec-title">3. Анализ подверженности риску</h3>
          <div class="chart-placeholder">
             <!-- Имитация графика для примера -->
             <div class="fake-chart-bars">
               <div class="bar" style="height: 40%"></div>
               <div class="bar" style="height: 70%"></div>
               <div class="bar" style="height: 50%"></div>
               <div class="bar" style="height: 85%"></div>
               <div class="bar" style="height: 60%"></div>
               <div class="bar" style="height: 90%"></div>
             </div>
             <div class="chart-label">Отраслевая структура портфеля</div>
          </div>
        </section>

        <!-- Footer -->
        <div class="rep-footer">
          <div class="footer-line"></div>
          <div class="footer-info">
            <span>Конфиденциально</span>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePdfExport } from '@/composables/usePdfExport'

const { exportToPdf, isExporting } = usePdfExport()

const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', { 
    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
})

const generateReport = () => {
  exportToPdf('report-content', `QuantPro_Report_${new Date().toISOString().slice(0,10)}.pdf`)
}
</script>

<style scoped>
.reports-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 24px 32px;
  color: #fff;
}

.reports-header {
  display: flex; justify-content: space-between; align-items: flex-end;
  margin-bottom: 24px;
}
.page-title { font-size: 24px; font-weight: 700; }
.page-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin-top: 4px; }

.btn-action {
  background: #3b82f6; color: white; border: none;
  padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; gap: 8px;
  transition: all 0.2s;
}
.btn-action:hover { background: #2563eb; }

/* Wrapper для скролла, если экран маленький */
.report-container-wrapper {
  flex: 1;
  background: rgba(0,0,0,0.2);
  border-radius: 16px;
  padding: 40px;
  display: flex;
  justify-content: center;
  overflow-y: auto;
}

/* A4 Sheet Simulation */
.a4-sheet {
  width: 210mm;
  min-height: 297mm;
  background: #0f172a; /* Темный фон для листа (можно #fff для печати) */
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 0 50px rgba(0,0,0,0.5);
  padding: 15mm;
  box-sizing: border-box;
  position: relative;
  /* Важно для html2pdf */
  color: #f1f5f9; 
}

/* Internal Report Styles */
.rep-header { display: flex; justify-content: space-between; align-items: center; }
.rep-logo { font-size: 18px; font-weight: 800; letter-spacing: 0.05em; }
.rep-logo span { color: #38bdf8; }
.rep-meta { text-align: right; font-size: 10px; color: rgba(255,255,255,0.4); font-family: monospace; }

.rep-divider { height: 2px; background: linear-gradient(90deg, #38bdf8, transparent); margin: 20px 0 30px; }

.rep-main-title { font-size: 28px; margin-bottom: 30px; font-weight: 300; letter-spacing: -0.02em; }

.rep-section { margin-bottom: 30px; }
.sec-title { font-size: 14px; text-transform: uppercase; color: #94a3b8; margin-bottom: 12px; letter-spacing: 0.05em; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 4px; display: inline-block; }
.sec-text { font-size: 12px; line-height: 1.6; color: #cbd5e1; text-align: justify; }

/* Metrics Grid */
.metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.metric-box {
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
  padding: 12px; border-radius: 6px;
}
.m-label { display: block; font-size: 10px; color: #64748b; margin-bottom: 4px; }
.m-value { font-size: 18px; font-weight: 600; font-family: monospace; }
.m-value.positive { color: #4ade80; }
.m-value.warning { color: #fbbf24; }

/* Fake Chart */
.chart-placeholder {
  height: 200px;
  background: rgba(255,255,255,0.02);
  border: 1px dashed rgba(255,255,255,0.1);
  border-radius: 8px;
  display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
  padding-bottom: 20px; position: relative;
}
.fake-chart-bars { display: flex; gap: 15px; align-items: flex-end; height: 100px; }
.bar { width: 30px; background: #38bdf8; opacity: 0.8; border-radius: 4px 4px 0 0; }
.bar:nth-child(even) { background: #6366f1; }
.chart-label { position: absolute; top: 10px; left: 10px; font-size: 10px; color: rgba(255,255,255,0.3); }

/* Footer */
.rep-footer { margin-top: 50px; }
.footer-line { height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 8px; }
.footer-info { display: flex; justify-content: space-between; font-size: 9px; color: rgba(255,255,255,0.2); }
</style>