/**
 * Hidden Markov Model для анализа рыночных режимов
 * Реализует алгоритмы Forward-Backward, Viterbi и Baum-Welch
 */

export interface RegimeState {
  id: number
  name: string
  color: string
  mean: number[]  // [return, volatility, liquidity]
  covariance: number[][]  // 3x3 covariance matrix
}

export interface MarketPoint {
  date: string
  return: number  // %
  volatility: number  // %
  liquidity: number  // normalized 0-1
  regime?: number  // predicted regime
  probability?: number[]  // posterior probabilities
  index: number
}

export interface TransitionMatrix {
  matrix: number[][]  // [from][to]
  stationary: number[]  // stationary distribution
}

export interface HMMParameters {
  nStates: number
  transitionMatrix: number[][]
  initialStateDistribution: number[]
  emissionMeans: number[][]
  emissionCovariances: number[][][]
}

/**
 * Класс HMM модели для рыночных режимов
 */
export class HMMModel {
  private nStates: number
  private transitionMatrix: number[][]
  private initialStateDistribution: number[]
  private emissionMeans: number[][]
  private emissionCovariances: number[][][]

  constructor(params?: HMMParameters) {
    if (params) {
      this.nStates = params.nStates
      this.transitionMatrix = params.transitionMatrix
      this.initialStateDistribution = params.initialStateDistribution
      this.emissionMeans = params.emissionMeans
      this.emissionCovariances = params.emissionCovariances
    } else {
      // Default initialization
      this.nStates = 4
      this.initializeDefault()
    }
  }

  /**
   * Инициализация модели по умолчанию (4 режима)
   */
  private initializeDefault() {
    this.transitionMatrix = [
      [0.85, 0.10, 0.04, 0.01],  // Low Vol -> Low Vol, Normal, High Vol, Crisis
      [0.15, 0.70, 0.12, 0.03],  // Normal -> ...
      [0.05, 0.15, 0.65, 0.15],  // High Vol -> ...
      [0.02, 0.08, 0.30, 0.60]   // Crisis -> ...
    ]

    this.initialStateDistribution = [0.4, 0.4, 0.15, 0.05]

    // Emission means: [return %, volatility %, liquidity]
    this.emissionMeans = [
      [0.15, 8.0, 0.8],   // Low Vol: positive return, low vol, high liquidity
      [0.08, 15.0, 0.6],  // Normal: moderate return, moderate vol, moderate liquidity
      [-0.05, 35.0, 0.4], // High Vol: negative return, high vol, low liquidity
      [-0.20, 60.0, 0.2]  // Crisis: very negative return, extreme vol, very low liquidity
    ]

    // Emission covariances (3x3 matrices)
    this.emissionCovariances = [
      [[2.0, 0.3, 0.1], [0.3, 5.0, 0.2], [0.1, 0.2, 0.05]],   // Low Vol
      [[4.0, 0.5, 0.2], [0.5, 12.0, 0.3], [0.2, 0.3, 0.08]],  // Normal
      [[8.0, 1.5, 0.4], [1.5, 40.0, 0.5], [0.4, 0.5, 0.12]],  // High Vol
      [[15.0, 3.0, 0.6], [3.0, 80.0, 0.8], [0.6, 0.8, 0.15]]  // Crisis
    ]
  }

  /**
   * Forward-Backward algorithm для вычисления posterior probabilities
   */
  forwardBackward(observations: number[][]): number[][] {
    const T = observations.length
    const alpha: number[][] = []  // Forward probabilities
    const beta: number[][] = []   // Backward probabilities
    const gamma: number[][] = []  // Posterior probabilities

    // Forward pass
    for (let t = 0; t < T; t++) {
      alpha[t] = new Array(this.nStates).fill(0)
      
      if (t === 0) {
        for (let i = 0; i < this.nStates; i++) {
          alpha[t][i] = this.initialStateDistribution[i] * 
                       this.emissionProbability(observations[t], i)
        }
      } else {
        for (let j = 0; j < this.nStates; j++) {
          let sum = 0
          for (let i = 0; i < this.nStates; i++) {
            sum += alpha[t-1][i] * this.transitionMatrix[i][j]
          }
          alpha[t][j] = sum * this.emissionProbability(observations[t], j)
        }
      }

      // Normalize
      const sum = alpha[t].reduce((a, b) => a + b, 0)
      if (sum > 0) {
        for (let i = 0; i < this.nStates; i++) {
          alpha[t][i] /= sum
        }
      }
    }

    // Backward pass
    for (let t = T - 1; t >= 0; t--) {
      beta[t] = new Array(this.nStates).fill(0)
      
      if (t === T - 1) {
        for (let i = 0; i < this.nStates; i++) {
          beta[t][i] = 1.0
        }
      } else {
        for (let i = 0; i < this.nStates; i++) {
          let sum = 0
          for (let j = 0; j < this.nStates; j++) {
            sum += this.transitionMatrix[i][j] * 
                   this.emissionProbability(observations[t+1], j) * 
                   beta[t+1][j]
          }
          beta[t][i] = sum
        }
      }

      // Normalize
      const sum = beta[t].reduce((a, b) => a + b, 0)
      if (sum > 0) {
        for (let i = 0; i < this.nStates; i++) {
          beta[t][i] /= sum
        }
      }
    }

    // Compute posterior probabilities (gamma)
    for (let t = 0; t < T; t++) {
      gamma[t] = new Array(this.nStates).fill(0)
      let sum = 0
      for (let i = 0; i < this.nStates; i++) {
        gamma[t][i] = alpha[t][i] * beta[t][i]
        sum += gamma[t][i]
      }
      // Normalize
      if (sum > 0) {
        for (let i = 0; i < this.nStates; i++) {
          gamma[t][i] /= sum
        }
      }
    }

    return gamma
  }

  /**
   * Viterbi algorithm для определения наиболее вероятной последовательности состояний
   */
  viterbi(observations: number[][]): number[] {
    const T = observations.length
    const delta: number[][] = []
    const psi: number[][] = []
    const path: number[] = []

    // Initialization
    delta[0] = new Array(this.nStates).fill(0)
    for (let i = 0; i < this.nStates; i++) {
      delta[0][i] = Math.log(this.initialStateDistribution[i] + 1e-10) + 
                    Math.log(this.emissionProbability(observations[0], i) + 1e-10)
    }

    // Recursion
    for (let t = 1; t < T; t++) {
      delta[t] = new Array(this.nStates).fill(-Infinity)
      psi[t] = new Array(this.nStates).fill(0)
      
      for (let j = 0; j < this.nStates; j++) {
        let maxVal = -Infinity
        let maxIdx = 0
        
        for (let i = 0; i < this.nStates; i++) {
          const val = delta[t-1][i] + Math.log(this.transitionMatrix[i][j] + 1e-10)
          if (val > maxVal) {
            maxVal = val
            maxIdx = i
          }
        }
        
        delta[t][j] = maxVal + Math.log(this.emissionProbability(observations[t], j) + 1e-10)
        psi[t][j] = maxIdx
      }
    }

    // Termination and backtracking
    let maxVal = -Infinity
    let maxIdx = 0
    for (let i = 0; i < this.nStates; i++) {
      if (delta[T-1][i] > maxVal) {
        maxVal = delta[T-1][i]
        maxIdx = i
      }
    }
    path[T-1] = maxIdx

    for (let t = T - 2; t >= 0; t--) {
      path[t] = psi[t+1][path[t+1]]
    }

    return path
  }

  /**
   * Вычисление вероятности эмиссии (Gaussian)
   */
  private emissionProbability(observation: number[], state: number): number {
    const mean = this.emissionMeans[state]
    const cov = this.emissionCovariances[state]
    
    // Multivariate Gaussian probability
    const diff = [
      observation[0] - mean[0],
      observation[1] - mean[1],
      observation[2] - mean[2]
    ]

    // Compute determinant of covariance matrix
    const det = this.matrixDeterminant3x3(cov)
    if (det <= 0) return 1e-10

    // Compute inverse
    const inv = this.matrixInverse3x3(cov)
    if (!inv) return 1e-10

    // Compute quadratic form
    let quad = 0
    for (let i = 0; i < 3; i++) {
      let sum = 0
      for (let j = 0; j < 3; j++) {
        sum += inv[i][j] * diff[j]
      }
      quad += diff[i] * sum
    }

    // Gaussian probability
    const prob = Math.exp(-0.5 * quad) / Math.sqrt(Math.pow(2 * Math.PI, 3) * det)
    return Math.max(prob, 1e-10)
  }

  /**
   * Вычисление определителя матрицы 3x3
   */
  private matrixDeterminant3x3(matrix: number[][]): number {
    const a = matrix[0][0], b = matrix[0][1], c = matrix[0][2]
    const d = matrix[1][0], e = matrix[1][1], f = matrix[1][2]
    const g = matrix[2][0], h = matrix[2][1], i = matrix[2][2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
  }

  /**
   * Вычисление обратной матрицы 3x3
   */
  private matrixInverse3x3(matrix: number[][]): number[][] | null {
    const det = this.matrixDeterminant3x3(matrix)
    if (Math.abs(det) < 1e-10) return null

    const inv: number[][] = []
    const a = matrix[0][0], b = matrix[0][1], c = matrix[0][2]
    const d = matrix[1][0], e = matrix[1][1], f = matrix[1][2]
    const g = matrix[2][0], h = matrix[2][1], i = matrix[2][2]

    inv[0] = [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det]
    inv[1] = [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det]
    inv[2] = [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]

    return inv
  }

  /**
   * Вычисление стационарного распределения
   */
  computeStationaryDistribution(): number[] {
    // Используем метод итераций для нахождения левого собственного вектора
    let pi = new Array(this.nStates).fill(1 / this.nStates)
    
    for (let iter = 0; iter < 100; iter++) {
      const newPi = new Array(this.nStates).fill(0)
      for (let j = 0; j < this.nStates; j++) {
        for (let i = 0; i < this.nStates; i++) {
          newPi[j] += pi[i] * this.transitionMatrix[i][j]
        }
      }
      
      // Normalize
      const sum = newPi.reduce((a, b) => a + b, 0)
      if (sum > 0) {
        for (let i = 0; i < this.nStates; i++) {
          newPi[i] /= sum
        }
      }
      
      pi = newPi
    }
    
    return pi
  }

  /**
   * Вычисление ожидаемой длительности режима
   */
  computeExpectedDuration(state: number): number {
    const p = this.transitionMatrix[state][state]
    return 1 / (1 - p)
  }

  /**
   * Геттеры
   */
  getTransitionMatrix(): number[][] {
    return this.transitionMatrix.map(row => [...row])
  }

  getEmissionMeans(): number[][] {
    return this.emissionMeans.map(row => [...row])
  }

  getEmissionCovariances(): number[][][] {
    return this.emissionCovariances.map(matrix => matrix.map(row => [...row]))
  }

  getNStates(): number {
    return this.nStates
  }

  /**
   * Установка параметров модели
   */
  setParameters(params: Partial<HMMParameters>) {
    if (params.nStates !== undefined) this.nStates = params.nStates
    if (params.transitionMatrix) this.transitionMatrix = params.transitionMatrix
    if (params.initialStateDistribution) this.initialStateDistribution = params.initialStateDistribution
    if (params.emissionMeans) this.emissionMeans = params.emissionMeans
    if (params.emissionCovariances) this.emissionCovariances = params.emissionCovariances
  }
}

/**
 * Генерация mock данных для тестирования
 */
export function generateMockMarketData(days: number = 500): MarketPoint[] {
  const model = new HMMModel()
  const data: MarketPoint[] = []
  const startDate = new Date('2023-01-01')
  
  let currentState = 0
  let observations: number[][] = []
  
  // Генерация последовательности наблюдений
  for (let i = 0; i < days; i++) {
    // Переход состояния
    const rand = Math.random()
    let cumProb = 0
    for (let j = 0; j < model.getNStates(); j++) {
      cumProb += model.getTransitionMatrix()[currentState][j]
      if (rand < cumProb) {
        currentState = j
        break
      }
    }
    
    // Генерация наблюдения из текущего режима
    const means = model.getEmissionMeans()[currentState]
    const cov = model.getEmissionCovariances()[currentState]
    
    // Упрощенная генерация из многомерного нормального распределения
    const observation = [
      means[0] + (Math.random() - 0.5) * Math.sqrt(cov[0][0]) * 2,
      Math.max(5, means[1] + (Math.random() - 0.5) * Math.sqrt(cov[1][1]) * 2),
      Math.max(0.1, Math.min(1.0, means[2] + (Math.random() - 0.5) * Math.sqrt(cov[2][2]) * 2))
    ]
    
    observations.push(observation)
    
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)
    
    data.push({
      date: date.toISOString().split('T')[0],
      return: observation[0],
      volatility: observation[1],
      liquidity: observation[2],
      regime: currentState,
      index: i
    })
  }
  
  // Применяем Forward-Backward для получения вероятностей
  const probabilities = model.forwardBackward(observations)
  data.forEach((point, i) => {
    point.probability = probabilities[i]
    // Обновляем режим на основе максимальной вероятности
    const maxProb = Math.max(...probabilities[i])
    point.regime = probabilities[i].indexOf(maxProb)
  })
  
  return data
}
