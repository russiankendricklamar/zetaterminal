# Stochastic Dashboard

Financial analytics dashboard with bond valuation, portfolio management, and risk analysis.

## 🚀 Quick Start - Deployment

**Frontend** автоматически деплоится на GitHub Pages: 
👉 https://russiankendricklamar.github.io/stochastic-dashbord-v1/

**Backend** нужно развернуть отдельно. См. [DEPLOYMENT.md](./DEPLOYMENT.md) для инструкций.

### Самый быстрый способ (Railway):

1. Зарегистрируйся на [Railway.app](https://railway.app) через GitHub
2. **New Project** → **Deploy from GitHub repo** → выбери этот репозиторий
3. В настройках проекта:
   - **Root Directory**: `/backend`
   - Railway автоматически определит Python и запустит
4. Скопируй URL развернутого backend (например: `https://stochastic-backend.railway.app`)
5. В GitHub → **Settings** → **Secrets and variables** → **Actions**:
   - Добавь секрет `VITE_API_BASE_URL` = URL твоего backend
6. Следующий пуш автоматически обновит frontend с новым API URL

## 📁 Project Structure

```
├── frontend/          # Vue.js + TypeScript frontend
├── backend/           # FastAPI Python backend
├── .github/workflows/ # GitHub Actions для деплоя
└── DEPLOYMENT.md      # Подробная инструкция по деплою
```

## 🛠️ Local Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python run_backend.py
```

Backend будет доступен на `http://localhost:8000`
Frontend на `http://localhost:5173`

## 📚 Features

- **Bond Valuation**: Оценка облигаций с различными метриками (YTM, Duration, Convexity)
- **Portfolio Management**: Управление портфелем и анализ рисков
- **Monte Carlo Simulation**: Симуляции для оценки рисков
- **Stress Testing**: Стресс-тестирование портфеля
- **Forward/Swap Valuation**: Оценка форвардов и свопов
- И многое другое...

## 📝 License

See LICENSE file.
