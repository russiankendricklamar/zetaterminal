// src/composables/usePdfExport.ts
import { ref } from 'vue'

export function usePdfExport() {
  const isExporting = ref(false)

  const exportToPdf = async (elementId: string, filename: string = 'report.pdf') => {
    isExporting.value = true
    
    try {
      // Динамический импорт: загружаем библиотеку только при клике
      // Если её нет, ошибка будет поймана в catch
      const html2pdfModule = await import('html2pdf.js')
      const html2pdf = html2pdfModule.default || html2pdfModule

      const element = document.getElementById(elementId)
      if (!element) throw new Error(`Element #${elementId} not found`)

      const opt = {
        margin: [10, 10, 10, 10],
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, backgroundColor: '#0f172a' },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      }

      await html2pdf().set(opt).from(element).save()

    } catch (e) {
      console.error('PDF Export Error:', e)
      alert('Ошибка экспорта PDF. Убедитесь, что html2pdf.js установлен (npm install html2pdf.js)')
    } finally {
      isExporting.value = false
    }
  }

  return { exportToPdf, isExporting }
}