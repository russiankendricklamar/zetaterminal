<!-- src/pages/Reports.vue -->
<template>
  <div class="page-container">
    
    <!-- Header Page Actions -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Аналитические отчеты</h1>
        <p class="section-subtitle">Генерация PDF-сводки по состоянию портфеля</p>
      </div>
      
      <div class="header-actions">
        <button class="btn-glass primary" @click="generateReport" :disabled="isExporting">
          <span v-if="isExporting" class="flex items-center gap-2">
             <span class="spinner-mini"></span> Генерация...
          </span>
          <span v-else class="flex items-center gap-2">
             <span>Скачать PDF</span>
             <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
          </span>
        </button>
      </div>
    </div>

    <!-- REPORT PREVIEW AREA (A4 Layout) -->
    <div class="report-viewport custom-scroll">
      <!-- A4 Sheet (Target for PDF Export) -->
      <div id="report-content" class="a4-sheet">
        
        <!-- Report Header -->
        <div class="rep-header">
          <div class="rep-logo">
             <div class="logo-icon">RK</div>
             <span>Quant<span class="text-accent">Risk</span></span>
          </div>
          <div class="rep-meta">
            <div class="rep-label">ДАТА ОТЧЕТА</div>
            <div class="rep-date">{{ currentDate }}</div>
          </div>
        </div>

        <div class="rep-divider"></div>

        <!-- Main Title -->
        <div class="rep-hero">
            <h2 class="rep-main-title">Ежедневная оценка рыночных рисков</h2>
            <div class="rep-tags">
               <span class="rep-tag">Portfolio Alpha</span>
               <span class="rep-tag">Daily Brief</span>
            </div>
        </div>

        <!-- Executive Summary -->
        <section class="rep-section">
          <h3 class="sec-title">1. Краткое резюме</h3>
          <p class="sec-text">
            Портфель демонстрирует умеренную волатильность в текущем рыночном режиме. 
            Показатель <strong>Value-at-Risk (95%)</strong> остается в пределах установленных лимитов (-2.4%). 
            Наблюдается незначительная отрицательная асимметрия (negative skewness) в распределении доходностей, что указывает на 
            повышенный риск хвостовых событий в случае коррекции S&P 500.
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

        <!-- Charts Simulation -->
        <section class="rep-section">
          <h3 class="sec-title">3. Структура риска (Exposure)</h3>
          <div class="chart-container-print">
             <!-- SVG Chart for Print -->
             <svg viewBox="0 0 600 200" class="print-chart">
                 <!-- Grid -->
                 <line x1="0" y1="150" x2="600" y2="150" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
                 <line x1="0" y1="100" x2="600" y2="100" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
                 <line x1="0" y1="50" x2="600" y2="50" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
                 
                 <!-- Bars -->
                 <rect x="50" y="80" width="60" height="70" fill="#3b82f6" rx="2" />
                 <rect x="150" y="40" width="60" height="110" fill="#8b5cf6" rx="2" />
                 <rect x="250" y="100" width="60" height="50" fill="#fbbf24" rx="2" />
                 <rect x="350" y="60" width="60" height="90" fill="#ef4444" rx="2" />
                 <rect x="450" y="90" width="60" height="60" fill="#10b981" rx="2" />
                 
                 <!-- Labels -->
                 <text x="80" y="170" fill="#94a3b8" font-size="10" text-anchor="middle">Tech</text>
                 <text x="180" y="170" fill="#94a3b8" font-size="10" text-anchor="middle">Fin</text>
                 <text x="280" y="170" fill="#94a3b8" font-size="10" text-anchor="middle">Gold</text>
                 <text x="380" y="170" fill="#94a3b8" font-size="10" text-anchor="middle">Bonds</text>
                 <text x="480" y="170" fill="#94a3b8" font-size="10" text-anchor="middle">Energy</text>
             </svg>
          </div>
        </section>
        
        <!-- Table -->
        <section class="rep-section">
            <h3 class="sec-title">4. Топ-5 активов по волатильности</h3>
            <table class="print-table">
                <thead>
                    <tr>
                        <th>Актив</th>
                        <th>Вес</th>
                        <th>Волатильность (30d)</th>
                        <th>Вклад в VaR</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>TSLA (Tesla Inc)</td>
                        <td>5.2%</td>
                        <td>45.2%</td>
                        <td class="text-red">12.4%</td>
                    </tr>
                    <tr>
                        <td>NVDA (Nvidia Corp)</td>
                        <td>4.8%</td>
                        <td>38.1%</td>
                        <td class="text-red">10.1%</td>
                    </tr>
                    <tr>
                        <td>BTC (Bitcoin)</td>
                        <td>2.1%</td>
                        <td>55.0%</td>
                        <td class="text-red">8.5%</td>
                    </tr>
                </tbody>
            </table>
        </section>

        <!-- Footer -->
        <div class="rep-footer">
          <div class="footer-line"></div>
          <div class="footer-info">
            <span>© 2026 QuantRisk Analytics. Confidential.</span>
            <span>Page 1 of 1</span>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// --- Mocking usePdfExport for demo if you don't have it ---
// If you have it: import { usePdfExport } from '@/composables/usePdfExport'
const isExporting = ref(false)

const exportToPdf = async (elementId: string, filename: string) => {
    isExporting.value = true
    console.log(`Generating PDF from #${elementId} to ${filename}...`)
    
    // Simulate generation delay
    await new Promise(r => setTimeout(r, 2000))
    
    // In real app: use html2pdf.js or jspdf here
    // import html2pdf from 'html2pdf.js'
    // const element = document.getElementById(elementId)
    // html2pdf().set({ margin: 0, filename: filename }).from(element).save()
    
    alert('PDF сгенерирован (эмуляция)')
    isExporting.value = false
}
// ---------------------------------------------------------

const currentDate = computed(() => {
  return new Date().toLocaleDateString('ru-RU', { 
    year: 'numeric', month: 'long', day: 'numeric'
  })
})

const generateReport = () => {
  exportToPdf('report-content', `QuantReport_${new Date().toISOString().slice(0,10)}.pdf`)
}
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 24px; padding: 24px 32px;
  max-width: 1600px; margin: 0 auto; height: 100%;
}

.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

/* ============================================
   BUTTONS
   ============================================ */
.btn-glass {
  height: 38px; padding: 0 16px; border-radius: 10px; font-weight: 600; font-size: 13px;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  cursor: pointer; border: none; transition: all 0.2s;
}
.btn-glass.primary { background: #3b82f6; color: #fff; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
.btn-glass.primary:hover:not(:disabled) { background: #2563eb; transform: translateY(-1px); }
.btn-glass:disabled { opacity: 0.7; cursor: not-allowed; }

.flex { display: flex; }
.items-center { align-items: center; }
.gap-2 { gap: 8px; }

/* ============================================
   VIEWPORT & A4 SHEET
   ============================================ */
.report-viewport {
  flex: 1;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 40px;
  display: flex; justify-content: center;
  overflow-y: auto;
}

.a4-sheet {
  width: 210mm;
  min-height: 297mm;
  /* Glass Paper Look */
  background: radial-gradient(circle at 0% 0%, #1e293b 0%, #0f172a 100%);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
  padding: 15mm;
  box-sizing: border-box;
  position: relative;
  color: #f1f5f9;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* ============================================
   REPORT INTERNAL STYLES
   ============================================ */
.rep-header { display: flex; justify-content: space-between; align-items: center; }

.rep-logo { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
.logo-icon { width: 32px; height: 32px; background: #3b82f6; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; border-radius: 8px; }
.text-accent { color: #3b82f6; }

.rep-meta { text-align: right; }
.rep-label { font-size: 9px; color: rgba(255,255,255,0.4); text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 2px; }
.rep-date { font-size: 12px; color: #fff; font-family: "SF Mono", monospace; }

.rep-divider { height: 1px; background: rgba(255,255,255,0.1); margin: 24px 0 32px; }

.rep-main-title { font-size: 26px; margin: 0 0 12px 0; font-weight: 700; letter-spacing: -0.01em; color: #fff; }
.rep-tags { display: flex; gap: 8px; margin-bottom: 40px; }
.rep-tag { font-size: 10px; padding: 4px 8px; background: rgba(255,255,255,0.05); border-radius: 4px; color: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.05); }

/* SECTIONS */
.rep-section { margin-bottom: 36px; }
.sec-title { 
    font-size: 12px; text-transform: uppercase; color: #3b82f6; margin-bottom: 12px; 
    font-weight: 700; letter-spacing: 0.05em; display: flex; align-items: center; gap: 8px;
}
.sec-title::after { content: ""; flex: 1; height: 1px; background: rgba(59, 130, 246, 0.2); }

.sec-text { font-size: 13px; line-height: 1.6; color: rgba(255,255,255,0.8); text-align: justify; }

/* METRICS */
.metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.metric-box {
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
  padding: 16px; border-radius: 8px; display: flex; flex-direction: column; gap: 4px;
}
.m-label { font-size: 10px; color: rgba(255,255,255,0.5); text-transform: uppercase; font-weight: 600; }
.m-value { font-size: 20px; font-weight: 700; font-family: "SF Mono", monospace; }
.m-value.positive { color: #4ade80; }
.m-value.warning { color: #fbbf24; }

/* CHART & TABLE */
.chart-container-print {
  height: 180px; background: rgba(255,255,255,0.02); border-radius: 8px; padding: 20px;
  border: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center;
}
.print-chart { width: 100%; height: 100%; }

.print-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.print-table th { text-align: left; color: rgba(255,255,255,0.4); border-bottom: 1px solid rgba(255,255,255,0.1); padding: 8px 0; font-weight: 600; text-transform: uppercase; font-size: 10px; }
.print-table td { border-bottom: 1px solid rgba(255,255,255,0.05); padding: 10px 0; color: rgba(255,255,255,0.9); }
.print-table tr:last-child td { border-bottom: none; }
.text-red { color: #f87171; }

/* FOOTER */
.rep-footer { margin-top: auto; padding-top: 40px; }
.footer-line { height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 12px; }
.footer-info { display: flex; justify-content: space-between; font-size: 9px; color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 0.05em; }

/* SPINNER */
.spinner-mini { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .page-container {
    padding: 16px 20px;
    gap: 20px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .report-viewport {
    padding: 20px;
  }
  
  .a4-sheet {
    width: 100%;
    max-width: 210mm;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
    gap: 16px;
  }
  
  .section-title {
    font-size: 22px;
  }
  
  .section-subtitle {
    font-size: 12px;
  }
  
  .report-viewport {
    padding: 16px;
  }
  
  .a4-sheet {
    padding: 12mm;
  }
  
  .rep-main-title {
    font-size: 20px;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .m-value {
    font-size: 18px;
  }
  
  .chart-container-print {
    height: 150px;
    padding: 12px;
  }
  
  .print-table {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
    gap: 12px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .section-subtitle {
    font-size: 11px;
  }
  
  .btn-glass {
    font-size: 12px;
    padding: 0 12px;
    height: 36px;
  }
  
  .report-viewport {
    padding: 12px;
  }
  
  .a4-sheet {
    padding: 10mm;
  }
  
  .rep-main-title {
    font-size: 18px;
  }
  
  .rep-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .rep-meta {
    text-align: left;
  }
  
  .m-value {
    font-size: 16px;
  }
  
  .chart-container-print {
    height: 120px;
    padding: 8px;
  }
  
  .print-table {
    font-size: 10px;
  }
  
  .print-table th,
  .print-table td {
    padding: 6px 0;
  }
}
</style>