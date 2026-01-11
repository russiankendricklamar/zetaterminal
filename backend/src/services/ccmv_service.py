"""
Сервис для CCMV (Cardinality-Constrained Mean-Variance) оптимизации портфеля.
Основан на методе кластеризации с ограничением кардинальности.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy.optimize import brentq
from math import floor
import cvxpy as cp
import warnings

warnings.filterwarnings('ignore')


def hierarchical_clustering(R: np.ndarray) -> np.ndarray:
    """
    Выполняет иерархическую кластеризацию активов на основе матрицы доходностей.
    
    Parameters:
    -----------
    R : np.ndarray
        Матрица доходностей (time_steps x num_assets)
    
    Returns:
    --------
    np.ndarray
        Массив меток кластеров для каждого актива
    """
    # 1. Вычисляем корреляционную матрицу
    tau = np.corrcoef(R, rowvar=False)
    
    # 2. Строим матрицу расстояний
    D = 1 - tau
    
    # 3. Инициализируем кластеры
    C = [[i] for i in np.arange(R.shape[1])]
    
    def d(Ci, Cj):
        """Вычисляет расстояние между двумя кластерами."""
        cent_i = 1 / len(Ci) * np.sum(D[Ci, :], axis=0)
        cent_j = 1 / len(Cj) * np.sum(D[Cj, :], axis=0)
        dist = (len(Ci) * len(Cj)) / (len(Ci) + len(Cj)) * np.linalg.norm(cent_i - cent_j) ** 2
        return dist
    
    # 4. Повторяем до тех пор, пока не останется один кластер
    merge_distances = []
    merge_log = []
    
    while len(C) > 1:
        min_distance = float('inf')
        best_pair = (0, 0)
        
        for i in range(len(C)):
            for j in range(i + 1, len(C)):
                distance = d(C[i], C[j])
                if distance < min_distance:
                    min_distance = distance
                    best_pair = (i, j)
        
        # Объединяем лучшую пару кластеров
        i, j = best_pair
        new_cluster = C[i] + C[j]
        merge_log.append((C[i], C[j], new_cluster, min_distance))
        
        del C[max(i, j)]  # Удаляем больший индекс сначала
        del C[min(i, j)]
        C.append(new_cluster)
        merge_distances.append(min_distance)
    
    # 5. Определяем оптимальное количество кластеров
    if len(merge_distances) > 1:
        gap = []
        for k in range(1, len(merge_distances)):
            gap.append(merge_distances[k] - merge_distances[k - 1])
        largest_gap = np.argmax(gap) + 1
        threshold = merge_distances[largest_gap]
    else:
        threshold = merge_distances[0] if merge_distances else 0
    
    # 6. Назначаем кластеры на основе порога
    clusters = [{i} for i in range(R.shape[1])]
    
    for log in merge_log:
        if log[3] <= threshold:
            Ci, Cj = log[0], log[1]
            to_merge = []
            for cluster in clusters:
                if any(i in cluster for i in Ci) or any(i in cluster for i in Cj):
                    to_merge.append(cluster)
            
            if len(to_merge) == 2:
                clusters.remove(to_merge[0])
                clusters.remove(to_merge[1])
                clusters.append(set(to_merge[0]).union(set(to_merge[1])))
    
    # Преобразуем в метки
    labels = np.empty(R.shape[1], dtype=int)
    for cluster_id, asset_set in enumerate(clusters):
        for asset in asset_set:
            labels[asset] = cluster_id
    
    return labels


def hierarchical_clustering_to_clusters(R: np.ndarray) -> List[List[int]]:
    """
    Выполняет иерархическую кластеризацию и возвращает список кластеров.
    
    Parameters:
    -----------
    R : np.ndarray
        Матрица доходностей (time_steps x num_assets)
    
    Returns:
    --------
    List[List[int]]
        Список кластеров, где каждый кластер - список индексов активов
    """
    labels = hierarchical_clustering(R)
    
    # Преобразуем метки в список кластеров
    num_clusters = len(np.unique(labels))
    clusters = [[] for _ in range(num_clusters)]
    
    for asset_idx, cluster_id in enumerate(labels):
        clusters[cluster_id].append(asset_idx)
    
    # Фильтруем пустые кластеры
    clusters = [c for c in clusters if len(c) > 0]
    
    return clusters


def allocate_cardinality(clusters: List[List[int]], mu: np.ndarray, Sigma: np.ndarray, 
                         Delta: int, gamma: float) -> List[int]:
    """
    Распределяет количество активов (Delta_k) по каждому кластеру.
    
    Parameters:
    -----------
    clusters : List[List[int]]
        Список кластеров, где каждый кластер - список индексов активов
    mu : np.ndarray
        Вектор ожидаемых доходностей
    Sigma : np.ndarray
        Ковариационная матрица
    Delta : int
        Общее количество активов для включения в портфель
    gamma : float
        Параметр неприятия риска
    
    Returns:
    --------
    List[int]
        Список Delta_k для каждого кластера
    """
    # Шаг 1: Вычисляем доходности и дисперсии на уровне кластера
    cluster_returns = []
    cluster_variances = []
    
    for cluster in clusters:
        cluster_assets = np.array(cluster)
        cluster_mu = mu[cluster_assets]
        cluster_Sigma = Sigma[np.ix_(cluster_assets, cluster_assets)]
        
        expected_return = np.mean(cluster_mu)
        variance = np.mean(np.diag(cluster_Sigma))
        
        cluster_returns.append(expected_return)
        cluster_variances.append(variance)
    
    # Шаг 2: Определяем функцию оценки
    def score_function(lambda_, mu_k, sigma2_k, gamma):
        scores = []
        for mu_i, sigma2_i in zip(mu_k, sigma2_k):
            if sigma2_i > 1e-10:
                raw = (gamma * mu_i - lambda_) / (2 * sigma2_i)
                scores.append(max(0, raw))
            else:
                scores.append(0.0)
        return scores
    
    def root_objective(lambda_, mu_k, sigma2_k, gamma):
        scores = score_function(lambda_, mu_k, sigma2_k, gamma)
        return sum(scores) - 1
    
    # Шаг 3: Решаем для lambda*
    try:
        lambda_star = brentq(root_objective, -1000, 1000, args=(cluster_returns, cluster_variances, gamma))
    except ValueError:
        # Если не удается найти корень, используем равномерное распределение
        lambda_star = 0
    
    # Шаг 4: Финальные оценки и распределение
    scores = score_function(lambda_star, cluster_returns, cluster_variances, gamma)
    
    # Нормализуем scores
    total_score = sum(scores)
    if total_score > 1e-10:
        scores = [s / total_score for s in scores]
    
    Delta_k = [max(1, floor(Delta * s)) for s in scores]
    
    # Убеждаемся, что сумма равна Delta
    total_delta = sum(Delta_k)
    if total_delta != Delta:
        diff = Delta - total_delta
        # Распределяем разницу
        for i in range(abs(diff)):
            idx = i % len(Delta_k)
            if diff > 0:
                Delta_k[idx] += 1
            else:
                Delta_k[idx] = max(1, Delta_k[idx] - 1)
    
    return Delta_k


def solve_intracluster_miqp(mu_cluster: np.ndarray, Sigma_cluster: np.ndarray,
                            delta_k: int, alpha_k: float, bar_w: float, gamma: float) -> np.ndarray:
    """
    Решает MIQP задачу для одного кластера C_k.
    
    Parameters:
    -----------
    mu_cluster : np.ndarray
        Ожидаемые доходности активов в кластере
    Sigma_cluster : np.ndarray
        Ковариационная матрица для кластера
    delta_k : int
        Количество активов для выбора в этом кластере
    alpha_k : float
        Доля общего веса портфеля, выделенная этому кластеру
    bar_w : float
        Максимально допустимый вес на актив
    gamma : float
        Параметр неприятия риска
    
    Returns:
    --------
    np.ndarray
        Оптимальные веса для активов в кластере
    """
    n = len(mu_cluster)  # количество активов в кластере
    
    # Шаг 1: Определяем переменные
    w = cp.Variable(n)
    z = cp.Variable(n, boolean=True)
    
    # Шаг 2: Определяем целевую функцию
    objective = cp.Minimize(cp.quad_form(w, Sigma_cluster) - gamma * mu_cluster @ w)
    
    # Шаг 3: Определяем ограничения
    constraints = [
        cp.sum(w) == alpha_k,
        w >= 0,
        w <= bar_w * z,
        cp.sum(z) <= delta_k
    ]
    
    # Шаг 4: Решаем задачу
    problem = cp.Problem(objective, constraints)
    
    # Выбираем решатель
    solver = None
    if 'GUROBI' in cp.installed_solvers():
        solver = cp.GUROBI
    elif 'ECOS_BB' in cp.installed_solvers():
        solver = cp.ECOS_BB
    elif 'SCIP' in cp.installed_solvers():
        solver = cp.SCIP
    else:
        # Fallback: используем приближенное решение без бинарных переменных
        w_simple = cp.Variable(n)
        objective_simple = cp.Minimize(cp.quad_form(w_simple, Sigma_cluster) - gamma * mu_cluster @ w_simple)
        constraints_simple = [
            cp.sum(w_simple) == alpha_k,
            w_simple >= 0,
            w_simple <= bar_w
        ]
        problem_simple = cp.Problem(objective_simple, constraints_simple)
        problem_simple.solve()
        
        # Выбираем топ delta_k активов
        if w_simple.value is not None:
            weights = w_simple.value
            top_indices = np.argsort(weights)[-delta_k:]
            result = np.zeros(n)
            for idx in top_indices:
                result[idx] = weights[idx]
            # Нормализуем
            total = np.sum(result)
            if total > 1e-10:
                result = result / total * alpha_k
            return result
        return np.ones(n) / n * alpha_k
    
    problem.solve(solver=solver)
    
    # Шаг 5: Возвращаем решение
    if w.value is not None:
        return w.value
    else:
        # Fallback: равномерное распределение
        result = np.zeros(n)
        num_selected = min(delta_k, n)
        weight_per_asset = alpha_k / num_selected
        for i in range(num_selected):
            result[i] = weight_per_asset
        return result


def delta_ccmv(R: np.ndarray, mu: np.ndarray, Sigma: np.ndarray, Delta: int,
               bar_w: float, gamma: float, asset_names: Optional[List[str]] = None) -> Dict:
    """
    Решает CCMV задачу с предварительным назначением количества активов в каждом кластере.
    
    Parameters:
    -----------
    R : np.ndarray
        Матрица доходностей
    mu : np.ndarray
        Ожидаемые доходности
    Sigma : np.ndarray
        Ковариационная матрица доходностей
    Delta : int
        Общее количество активов для включения в портфель
    bar_w : float
        Максимально допустимый вес на актив
    gamma : float
        Параметр неприятия риска
    asset_names : Optional[List[str]]
        Названия активов
    
    Returns:
    --------
    Dict
        Результаты оптимизации с весами, кластерами и статистикой
    """
    # Шаг 1: Получаем кластеры из R
    labels = hierarchical_clustering(R)
    
    # Преобразуем метки в список кластеров
    num_clusters = len(np.unique(labels))
    clusters = [[] for _ in range(num_clusters)]
    for asset_idx, cluster_id in enumerate(labels):
        clusters[cluster_id].append(asset_idx)
    
    # Фильтруем пустые кластеры
    clusters = [c for c in clusters if len(c) > 0]
    
    # Шаг 2: Предварительное распределение Delta
    Delta_k = allocate_cardinality(clusters, mu, Sigma, Delta, gamma)
    
    # Шаг 3: Оптимизация
    alpha_k = [1.0 / len(clusters) for _ in clusters]
    w = np.zeros(R.shape[1])
    
    cluster_info = []
    for i, cluster in enumerate(clusters):
        mu_cluster = mu[cluster]
        Sigma_cluster = Sigma[np.ix_(cluster, cluster)]
        delta_k = Delta_k[i]
        alpha_k_val = alpha_k[i]
        
        w_cluster = solve_intracluster_miqp(mu_cluster, Sigma_cluster, delta_k, alpha_k_val, bar_w, gamma)
        
        for j, asset_idx in enumerate(cluster):
            w[asset_idx] = w_cluster[j]
        
        # Информация о кластере
        cluster_info.append({
            'assets': [asset_names[idx] if asset_names else f'Asset_{idx}' for idx in cluster],
            'asset_indices': cluster,
            'delta_k': delta_k,
            'alpha_k': alpha_k_val,
            'weights': w_cluster.tolist() if isinstance(w_cluster, np.ndarray) else w_cluster
        })
    
    # Вычисляем статистику портфеля
    portfolio_return = np.dot(w, mu)
    portfolio_variance = np.dot(w, np.dot(Sigma, w))
    portfolio_volatility = np.sqrt(portfolio_variance)
    sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 1e-10 else 0.0
    
    # Объективная функция
    objective_value = portfolio_variance - gamma * portfolio_return
    
    return {
        'optimal_weights': w.tolist(),
        'clusters': cluster_info,
        'portfolio_stats': {
            'expected_return': float(portfolio_return),
            'volatility': float(portfolio_volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'objective_value': float(objective_value)
        },
        'method': 'delta',
        'Delta': Delta,
        'gamma': gamma,
        'bar_w': bar_w
    }


def alpha_ccmv(R: np.ndarray, mu: np.ndarray, Sigma: np.ndarray, Delta: int,
               bar_w: float, gamma: float, asset_names: Optional[List[str]] = None,
               alpha_k: Optional[List[float]] = None) -> Dict:
    """
    Решает CCMV задачу с предварительным назначением распределения весов по кластерам.
    
    Parameters:
    -----------
    R : np.ndarray
        Матрица доходностей
    mu : np.ndarray
        Ожидаемые доходности
    Sigma : np.ndarray
        Ковариационная матрица доходностей
    Delta : int
        Общее количество активов для включения в портфель
    bar_w : float
        Максимально допустимый вес на актив
    gamma : float
        Параметр неприятия риска
    asset_names : Optional[List[str]]
        Названия активов
    alpha_k : Optional[List[float]]
        Предустановленные доли весов по кластерам (если None, то равномерное распределение)
    
    Returns:
    --------
    Dict
        Результаты оптимизации с весами, кластерами и статистикой
    """
    # Шаг 1: Получаем кластеры из R
    clusters = hierarchical_clustering_to_clusters(R)
    
    # Шаг 2: Распределяем Delta по кластерам (пропорционально alpha_k)
    if alpha_k is None:
        alpha_k = [1.0 / len(clusters) for _ in clusters]
    
    # Вычисляем Delta_k пропорционально alpha_k
    Delta_k = []
    remaining_delta = Delta
    for i, alpha_val in enumerate(alpha_k):
        if i == len(alpha_k) - 1:
            delta_k = remaining_delta
        else:
            delta_k = max(1, floor(Delta * alpha_val))
            remaining_delta -= delta_k
        Delta_k.append(min(delta_k, len(clusters[i])))
    
    # Шаг 3: Оптимизация
    w = np.zeros(R.shape[1])
    
    cluster_info = []
    for i, cluster in enumerate(clusters):
        mu_cluster = mu[cluster]
        Sigma_cluster = Sigma[np.ix_(cluster, cluster)]
        delta_k = Delta_k[i]
        alpha_k_val = alpha_k[i]
        
        w_cluster = solve_intracluster_miqp(mu_cluster, Sigma_cluster, delta_k, alpha_k_val, bar_w, gamma)
        
        for j, asset_idx in enumerate(cluster):
            w[asset_idx] = w_cluster[j]
        
        # Информация о кластере
        cluster_info.append({
            'assets': [asset_names[idx] if asset_names else f'Asset_{idx}' for idx in cluster],
            'asset_indices': cluster,
            'delta_k': delta_k,
            'alpha_k': alpha_k_val,
            'weights': w_cluster.tolist() if isinstance(w_cluster, np.ndarray) else w_cluster
        })
    
    # Вычисляем статистику портфеля
    portfolio_return = np.dot(w, mu)
    portfolio_variance = np.dot(w, np.dot(Sigma, w))
    portfolio_volatility = np.sqrt(portfolio_variance)
    sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 1e-10 else 0.0
    
    # Объективная функция
    objective_value = portfolio_variance - gamma * portfolio_return
    
    return {
        'optimal_weights': w.tolist(),
        'clusters': cluster_info,
        'portfolio_stats': {
            'expected_return': float(portfolio_return),
            'volatility': float(portfolio_volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'objective_value': float(objective_value)
        },
        'method': 'alpha',
        'Delta': Delta,
        'gamma': gamma,
        'bar_w': bar_w
    }


def optimize_ccmv(R: np.ndarray, mu: np.ndarray, Sigma: np.ndarray, Delta: int,
                  bar_w: float, gamma: float, method: str = 'delta',
                  asset_names: Optional[List[str]] = None) -> Dict:
    """
    Полная CCMV оптимизация с выбором метода.
    
    Parameters:
    -----------
    R : np.ndarray
        Матрица доходностей
    mu : np.ndarray
        Ожидаемые доходности
    Sigma : np.ndarray
        Ковариационная матрица доходностей
    Delta : int
        Общее количество активов для включения в портфель
    bar_w : float
        Максимально допустимый вес на актив
    gamma : float
        Параметр неприятия риска
    method : str
        Метод оптимизации: 'delta' или 'alpha'
    asset_names : Optional[List[str]]
        Названия активов
    
    Returns:
    --------
    Dict
        Результаты оптимизации
    """
    if method == 'delta':
        return delta_ccmv(R, mu, Sigma, Delta, bar_w, gamma, asset_names)
    elif method == 'alpha':
        return alpha_ccmv(R, mu, Sigma, Delta, bar_w, gamma, asset_names)
    else:
        raise ValueError(f"Unknown method: {method}. Must be 'delta' or 'alpha'")
