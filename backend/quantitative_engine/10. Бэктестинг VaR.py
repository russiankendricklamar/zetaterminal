#!/usr/bin/env python
# coding: utf-8

# # **Бэктестинг VaR**

# In[ ]:


required_vars = {
    'priced_df': 'DataFrame цен',
    'asset_names': 'Список активов',
    'n_assets': 'Количество активов',
    'strategy': 'HJBStrategy объект'
}

print(" Проверка наличия основных данных:\n")

missing_vars = []
for var_name, description in required_vars.items():
    try:
        test_var = eval(var_name)
        print(f"    {var_name}: найдена ({description})")
    except NameError:
        missing_vars.append((var_name, description))
        print(f"    {var_name}: не найдена ({description})")

if missing_vars:
    error_msg = "\n Отсутствуют следующие переменные:\n"
    for var_name, description in missing_vars:
        error_msg += f"   • {var_name} ({description})\n"
    error_msg += "\nУбедитесь, что выполнены блоки 1.1 и 3.5\n"
    raise NameError(error_msg)

print()

original_start = priced_df.index[0]
original_end = priced_df.index[-1]

print(f"   Дата начала: {original_start.date()}")
print(f"   Дата конца:  {original_end.date()}")
print(f"   Количество дней: {len(priced_df)}")
print(f"   Активов в исходных данных: {n_assets}")
print(f"   Активы: {asset_names}\n")

try:
    weights = strategy.get_optimal_weights()

    weights = np.asarray(weights).flatten()

    print(f"    Веса успешно загружены из strategy объекта\n")

    weights_sum = np.sum(weights)
    print(f"    Статистика весов:")
    print(f"      Сумма весов: {weights_sum:.6f}")
    print(f"      Min вес: {np.min(weights)*100:>7.3f}%")
    print(f"      Max вес: {np.max(weights)*100:>7.3f}%")
    print(f"      Активов с ненулевыми весами: {np.sum(weights > 0)}\n")

    if abs(weights_sum - 1.0) > 0.01:
        print(f"     ВНИМАНИЕ: Сумма весов = {weights_sum:.6f} (ожидается ≈ 1.0)")
        print(f"      Веса возможно не нормализованы\n")

    print(f"    Веса по активам (из strategy):\n")
    for i, (ticker, w) in enumerate(zip(asset_names, weights)):
        if w > 0:
            print(f"      {ticker:>6} → {w*100:>6.2f}%")
        else:
            print(f"      {ticker:>6} → {w*100:>6.2f}% (исключен)")
    print()

    min_weight_threshold = 0.0001
    asset_names_to_load = [
        asset_names[i]
        for i in range(len(asset_names))
        if weights[i] > min_weight_threshold
    ]

    excluded_count = len(asset_names) - len(asset_names_to_load)
    if excluded_count > 0:
        excluded_assets = [
            asset_names[i]
            for i in range(len(asset_names))
            if weights[i] <= min_weight_threshold
        ]
        print(f"    Исключены активы с весом ≤ {min_weight_threshold*100:.2f}%:")
        print(f"      {', '.join(excluded_assets)}\n")

    weights_info = {
        'asset_names': asset_names,
        'weights': weights,
        'loaded_assets': asset_names_to_load,
        'min_weight_threshold': min_weight_threshold,
        'source': 'strategy.get_optimal_weights()'
    }

except AttributeError as e:
    print(f"    ОШИБКА: strategy объект не имеет метода get_optimal_weights()")
    print(f"      {e}\n")
    print(f"   Убедитесь, что блок 3.5 выполнен полностью\n")
    raise

except Exception as e:
    print(f"    ОШИБКА при извлечении весов: {e}\n")
    raise

print(f" К ЗАГРУЗКЕ: {len(asset_names_to_load)} активов")
print(f"   {', '.join(asset_names_to_load)}\n")

print(f"   Исходный период: {original_start.date()} - {original_end.date()}\n")

backtest_start = None
while backtest_start is None:
    try:
        backtest_start_str = input("Дата начала (DD.MM.YYYY): ").strip()
        backtest_start = pd.to_datetime(backtest_start_str, format='%d.%m.%Y')
    except ValueError:
        print(" Неверный формат! Используй DD.MM.YYYY\n")
        backtest_start = None

backtest_end = None
while backtest_end is None:
    try:
        backtest_end_str = input("Дата конца (DD.MM.YYYY): ").strip()
        backtest_end = pd.to_datetime(backtest_end_str, format='%d.%m.%Y')
    except ValueError:
        print(" Неверный формат! Используй DD.MM.YYYY\n")
        backtest_end = None

if backtest_start >= backtest_end:
    raise ValueError(" Дата начала должна быть раньше даты конца!")

has_warning = False

print(f" Проверка пересечений:\n")
print(f"   Исходный период:  {original_start.date()} - {original_end.date()}")
print(f"   Бэктест период:   {backtest_start.date()} - {backtest_end.date()}\n")

if backtest_end < original_start:
    print(f"    Бэктест ПОЛНОСТЬЮ ДО исходного периода")
    print(f"      (заканчивается {(original_start - backtest_end).days} дней ДО начала)\n")
elif backtest_start > original_end:
    print(f"    Бэктест ПОЛНОСТЬЮ ПОСЛЕ исходного периода")
    print(f"      (начинается {(backtest_start - original_end).days} дней ПОСЛЕ конца)\n")
else:
    overlap_start = max(original_start, backtest_start)
    overlap_end = min(original_end, backtest_end)
    overlap_days = (overlap_end - overlap_start).days

    print(f"     ВНИМАНИЕ: Обнаружено пересечение!")
    print(f"      Пересечение: {overlap_start.date()} - {overlap_end.date()}")
    print(f"      Длительность: {overlap_days} дней\n")

    response = input("   Продолжить? (рекомендуется исправить) (y/n): ").strip().lower()
    if response != 'y':
        raise ValueError("Выбери период БЕЗ пересечения")
    has_warning = True

print(f" ПАРАМЕТРЫ БЭКТЕСТА УСТАНОВЛЕНЫ:\n")
print(f"   Дата начала: {backtest_start.date()}")
print(f"   Дата конца:  {backtest_end.date()}")
print(f"   Длительность: {(backtest_end - backtest_start).days} дней\n")

def fetch_from_moex_complete_backtest(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:

    url = (
        f"https://iss.moex.com/iss/history/engines/stock/markets/shares/"
        f"boards/TQBR/securities/{ticker}.json"
    )

    all_rows = []
    start_idx = 0
    columns = None

    print(f"   ↓ {ticker}...", end=" ", flush=True)

    while True:
        params = {
            'from': start_date,
            'till': end_date,
            'sort_order': 'asc',
            'start': start_idx
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if 'history' not in data or 'data' not in data['history']:
                break

            rows = data['history']['data']

            if columns is None:
                columns = data['history']['columns']

            if len(rows) == 0:
                break

            all_rows.extend(rows)
            start_idx += len(rows)

            print(".", end="", flush=True)
            time.sleep(0.1)

        except Exception as e:
            print(f"ERROR: {e}")
            return None

    if len(all_rows) == 0:
        print(f"No data")
        return None

    print(f" ({len(all_rows)} rows)")

    try:
        df = pd.DataFrame(all_rows, columns=columns)
        df = df[['TRADEDATE', 'CLOSE']].copy()
        df.columns = ['Date', 'Close']

        df['Date'] = pd.to_datetime(df['Date'])
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

        df = df.drop_duplicates(subset=['Date'])
        df = df.dropna()
        df = df.sort_values('Date').reset_index(drop=True)

        return df
    except Exception as e:
        print(f"Parse error: {e}")
        return None

prices_backtest = {}

for ticker in asset_names_to_load:
    df = fetch_from_moex_complete_backtest(
        ticker,
        backtest_start.strftime('%Y-%m-%d'),
        backtest_end.strftime('%Y-%m-%d')
    )

    if df is not None and len(df) > 0:
        prices_backtest[ticker] = df.set_index('Date')['Close']

print()

prices_backtest_df = pd.DataFrame(prices_backtest)

if len(prices_backtest_df) == 0:
    raise ValueError("Не удалось загрузить данные ни для одного актива!")

print(f" СТАТИСТИКА ЗАГРУЖЕННЫХ ДАННЫХ:\n")
print(f"   Периодов: {len(prices_backtest_df)}")
print(f"   Активов: {len(prices_backtest_df.columns)}")
print(f"   Дата начала: {prices_backtest_df.index[0].date()}")
print(f"   Дата конца:  {prices_backtest_df.index[-1].date()}\n")

min_required_days = 20
valid_assets = []
for ticker in prices_backtest_df.columns:
    valid_count = prices_backtest_df[ticker].notna().sum()
    if valid_count >= min_required_days:
        valid_assets.append(ticker)
        print(f"    {ticker}: {valid_count} дней")
    else:
        print(f"     {ticker}: только {valid_count} дней (пропускается)")

print()

if not valid_assets:
    raise ValueError(" Нет активов с достаточным количеством данных!")

prices_backtest_df = prices_backtest_df[valid_assets]

prices_backtest_df = prices_backtest_df.fillna(method='ffill').fillna(method='bfill')

returns_backtest = np.log(prices_backtest_df / prices_backtest_df.shift(1)).dropna()

print(f" ДОХОДНОСТИ:\n")
print(f"   Периодов с доходностями: {len(returns_backtest)}")
print(f"   Средняя доходность: {returns_backtest.mean().mean()*100:>7.3f}%")
print(f"   Волатильность: {returns_backtest.std().mean()*100:>7.3f}%")
print(f"   Min: {returns_backtest.min().min()*100:>7.3f}%")
print(f"   Max: {returns_backtest.max().max()*100:>7.3f}%\n")

returns_original = np.log(priced_df / priced_df.shift(1)).dropna()
returns_original = returns_original[valid_assets]

print(f" СРАВНЕНИЕ ПЕРИОДОВ:\n")
print(f"{'Метрика':<25} | {'Исходный':<15} | {'Бэктест':<15} | {'Разница':<15}")
print(f"{'-'*25}-+-{'-'*15}-+-{'-'*15}-+-{'-'*15}")

for ticker in valid_assets[:3]:
    orig_vol = returns_original[ticker].std() * 100
    bt_vol = returns_backtest[ticker].std() * 100
    diff = bt_vol - orig_vol
    print(f"{ticker:>25} | {orig_vol:>13.2f}% | {bt_vol:>13.2f}% | {diff:>+13.2f}%")

print(f"\n{'ПОРТФЕЛЬ':<25} | {returns_original.mean().mean()*100:>13.3f}% | {returns_backtest.mean().mean()*100:>13.3f}% |")
print(f"{'Волатильность':<25} | {returns_original.std().mean()*100:>13.3f}% | {returns_backtest.std().mean()*100:>13.3f}% | {(returns_backtest.std().mean() - returns_original.std().mean())*100:>+13.3f}%\n")

vol_ratio = returns_backtest.std().mean() / returns_original.std().mean()

if vol_ratio > 1.5:
    print("  ВНИМАНИЕ: Волатильность в бэктест периоде ЗНАЧИТЕЛЬНО выше!")
    print("   Это означает смену режима ('regime change')")
    print("   Модель может недооценивать риск на этих данных\n")
elif vol_ratio < 0.7:
    print("  ВНИМАНИЕ: Волатильность в бэктест периоде ЗНАЧИТЕЛЬНО ниже!")
    print("   Модель может переоценивать риск на этих данных\n")
else:
    print(" Волатильность в обоих периодах примерно одинакова\n")

backtest_data = {
    'prices': prices_backtest_df,
    'returns': returns_backtest,
    'period_start': backtest_start,
    'period_end': backtest_end,
    'assets': valid_assets,
    'n_days': len(returns_backtest),
    'weights_info': weights_info,
}

print(f" ДАННЫЕ ЗАГРУЖЕНЫ И СОХРАНЕНЫ:\n")
print(f"    prices_backtest_df: {prices_backtest_df.shape}")
print(f"    returns_backtest: {returns_backtest.shape}")
print(f"    backtest_data: словарь со всеми параметрами\n")

print(f" ГОТОВНОСТЬ К БЭКТЕСТУ:")
if not has_warning:
    print(f"    Нет пересечения с исходным периодом")
else:
    print(f"     Есть пересечение с исходным периодом")

# In[ ]:


required_vars = {
    'priced_df': 'Цены на исходном периоде',
    'returns_backtest': 'Доходности на бэктест-периоде',
    'backtest_data': 'Словарь с данными бэктеста',
    'strategy': 'HJBStrategy объект'
}

print(" Проверка наличия данных:\n")

missing_vars = []
for var_name, description in required_vars.items():
    try:
        test_var = eval(var_name)
        print(f"    {var_name}: найдена ({description})")
    except NameError:
        missing_vars.append((var_name, description))
        print(f"    {var_name}: не найдена ({description})")

if missing_vars:
    error_msg = "\n Отсутствуют следующие переменные:\n"
    for var_name, description in missing_vars:
        error_msg += f"   • {var_name} ({description})\n"
    error_msg += "\nУбедитесь, что выполнены блоки 1.1, 3.5 и 3.7.1\n"
    raise NameError(error_msg)

print()

n_backtest_days = len(returns_backtest)
backtest_assets = list(returns_backtest.columns)
n_backtest_assets = len(backtest_assets)
n_original_days = len(priced_df)

print(f" ДАННЫЕ ЗАГРУЖЕНЫ:\n")
print(f"   Исходный период:     {priced_df.index[0].date()} - {priced_df.index[-1].date()} ({n_original_days} дней)")
print(f"   Бэктест период:      {backtest_data['period_start'].date()} - {backtest_data['period_end'].date()} ({n_backtest_days} дней)")
print(f"   Активов в портфеле:  {n_backtest_assets}")
print(f"   Активы:              {', '.join(backtest_assets)}\n")

weights = strategy.get_optimal_weights()
weights = np.asarray(weights).flatten()

weights_dict = dict(zip(backtest_data['weights_info']['asset_names'], weights))
backtest_weights = np.array([weights_dict[asset] for asset in backtest_assets])

backtest_weights = backtest_weights / backtest_weights.sum()

print(f" Веса портфеля:\n")
for asset, w in zip(backtest_assets, backtest_weights):
    print(f"   {asset:>6} → {w*100:>6.2f}%")
print(f"   {'Сумма':>6} → {backtest_weights.sum()*100:>6.2f}%\n")

print(" Расчет портфельных доходностей на исходном периоде:\n")

prices_original = priced_df[backtest_assets]

returns_original = np.log(prices_original / prices_original.shift(1)).dropna()

portfolio_returns_original = (returns_original * backtest_weights).sum(axis=1)

print(f"   Количество дней:     {len(portfolio_returns_original)}")
print(f"   Средняя доходность:  {portfolio_returns_original.mean()*100:>7.3f}%")
print(f"   Волатильность:       {portfolio_returns_original.std()*100:>7.3f}%")
print(f"   Min доходность:      {portfolio_returns_original.min()*100:>7.3f}%")
print(f"   Max доходность:      {portfolio_returns_original.max()*100:>7.3f}%\n")

var_95_pct = 5
var_99_pct = 1

var_95_return = np.percentile(portfolio_returns_original, var_95_pct)
var_99_return = np.percentile(portfolio_returns_original, var_99_pct)

print(f" ИСТОРИЧЕСКИЙ VaR (расчитан на исходном периоде):\n")
print(f"   95% VaR (5-й процентиль):")
print(f"      Доходность:   {var_95_return*100:>15.2f}%")
print(f"      Интерпретация: 5% дней доходность ниже этого значения")

print(f"\n   99% VaR (1-й процентиль):")
print(f"      Доходность:   {var_99_return*100:>15.2f}%")
print(f"      Интерпретация: 1% дней доходность ниже этого значения\n")

print(f" СПРАВОЧНО: Распределение доходностей на исходном периоде:\n")
percentiles = [1, 5, 25, 50, 75, 95, 99]
for pct in percentiles:
    val = np.percentile(portfolio_returns_original, pct)
    print(f"   {pct:>2}й процентиль: {val*100:>7.2f}%")

print()

portfolio_returns_backtest = (returns_backtest * backtest_weights).sum(axis=1)

print(f" ПОРТФЕЛЬНЫЕ ДОХОДНОСТИ НА БЭКТЕСТ-ПЕРИОДЕ:\n")
print(f"   Количество дней:     {len(portfolio_returns_backtest)}")
print(f"   Средняя доходность:  {portfolio_returns_backtest.mean()*100:>7.3f}%")
print(f"   Волатильность:       {portfolio_returns_backtest.std()*100:>7.3f}%")
print(f"   Min доходность:      {portfolio_returns_backtest.min()*100:>7.3f}%")
print(f"   Max доходность:      {portfolio_returns_backtest.max()*100:>7.3f}%\n")

breaches_95 = portfolio_returns_backtest < var_95_return
breaches_99 = portfolio_returns_backtest < var_99_return

n_breaches_95 = breaches_95.sum()
n_breaches_99 = breaches_99.sum()

breach_rate_95 = n_breaches_95 / n_backtest_days
breach_rate_99 = n_breaches_99 / n_backtest_days

expected_breaches_95 = n_backtest_days * 0.05
expected_breaches_99 = n_backtest_days * 0.01

print(f" ПРОБИТИЯ VaR 95%:\n")
print(f"   Пороговая доходность (VaR): {var_95_return*100:>7.2f}%")
print(f"   Количество пробитий:        {n_breaches_95:>7} из {n_backtest_days}")
print(f"   Частота пробитий:           {breach_rate_95*100:>7.2f}% (ожидалось 5.00%)")
print(f"   Ожидалось пробитий:         {expected_breaches_95:>7.1f}")

if breach_rate_95 > 0.05:
    direction = "НЕДООЦЕНИВАЕТ"
elif breach_rate_95 < 0.05:
    direction = "ПЕРЕОЦЕНИВАЕТ"
else:
    direction = "КОРРЕКТНА"

print(f"   {emoji} Модель {direction} риск\n")

print(f" ПРОБИТИЯ VaR 99%:\n")
print(f"   Пороговая доходность (VaR): {var_99_return*100:>7.2f}%")
print(f"   Количество пробитий:        {n_breaches_99:>7} из {n_backtest_days}")
print(f"   Частота пробитий:           {breach_rate_99*100:>7.2f}% (ожидалось 1.00%)")
print(f"   Ожидалось пробитий:         {expected_breaches_99:>7.1f}")

if breach_rate_99 > 0.01:
    direction = "НЕДООЦЕНИВАЕТ"
elif breach_rate_99 < 0.01:
    direction = "ПЕРЕОЦЕНИВАЕТ"
else:
    direction = "КОРРЕКТНА"

print(f"   {emoji} Модель {direction} риск\n")

breach_dates_95 = portfolio_returns_backtest[breaches_95].index.tolist()
breach_dates_99 = portfolio_returns_backtest[breaches_99].index.tolist()

print(f" ДАТЫ ПРОБИТИЙ VaR 95% (первые 10):")
if len(breach_dates_95) > 0:
    for date in breach_dates_95[:10]:
        ret = portfolio_returns_backtest[date]
        loss = ret - var_95_return
        print(f"   {date.date()}: {ret*100:>7.2f}% (превышение: {loss*100:>6.2f}%)")
    if len(breach_dates_95) > 10:
        print(f"   ... еще {len(breach_dates_95) - 10} дат")
else:
    print(f"   Пробитий нет")

print(f"\n ДАТЫ ПРОБИТИЙ VaR 99%:")
if len(breach_dates_99) > 0:
    for date in breach_dates_99:
        ret = portfolio_returns_backtest[date]
        loss = ret - var_99_return
        print(f"   {date.date()}: {ret*100:>7.2f}% (превышение: {loss*100:>6.2f}%)")
else:
    print(f"   Пробитий нет")

print()

def kupiec_test(n_breaches, n_observations, confidence_level):

    alpha = 1 - confidence_level
    p_hat = n_breaches / n_observations

    if p_hat == 0:
        p_hat = 1e-10
    if p_hat == 1:
        p_hat = 1 - 1e-10

    if n_breaches == 0:
        lr_stat = -2 * n_observations * np.log(1 - alpha)
    elif n_breaches == n_observations:
        lr_stat = -2 * n_observations * np.log(alpha)
    else:
        L0 = (alpha ** n_breaches) * ((1 - alpha) ** (n_observations - n_breaches))
        L1 = (p_hat ** n_breaches) * ((1 - p_hat) ** (n_observations - n_breaches))
        lr_stat = -2 * np.log(L0 / L1)

    p_value = 1 - stats.chi2.cdf(lr_stat, df=1)

    critical_value = stats.chi2.ppf(0.95, df=1)

    reject_h0 = lr_stat > critical_value

    return {
        'lr_statistic': lr_stat,
        'p_value': p_value,
        'critical_value': critical_value,
        'reject_h0': reject_h0,
        'expected_breaches': n_observations * alpha,
        'observed_breaches': n_breaches,
        'expected_rate': alpha,
        'observed_rate': p_hat
    }

kupiec_95 = kupiec_test(n_breaches_95, n_backtest_days, 0.95)

print(f" РЕЗУЛЬТАТЫ:\n")
print(f"   Наблюдений:           {n_backtest_days}")
print(f"   Пробитий (ожидалось): {kupiec_95['expected_breaches']:.1f} (5.00%)")
print(f"   Пробитий (наблюдено): {kupiec_95['observed_breaches']} ({kupiec_95['observed_rate']*100:.2f}%)")
print(f"\n   LR-статистика:        {kupiec_95['lr_statistic']:.4f}")
print(f"   Критическое значение: {kupiec_95['critical_value']:.4f} (α = 0.05)")
print(f"   p-value:              {kupiec_95['p_value']:.4f}")

print(f"\n ВЫВОД:")
if kupiec_95['reject_h0']:
    print(f"    Отвергаем H₀ (p = {kupiec_95['p_value']:.4f} < 0.05)")
    print(f"   → VaR 95% РАБОТАЕТ НЕКОРРЕКТНО")
    if kupiec_95['observed_rate'] > kupiec_95['expected_rate']:
        print(f"   → Модель НЕДООЦЕНИВАЕТ риск ({kupiec_95['observed_rate']*100:.2f}% пробитий вместо 5%)")
    else:
        print(f"   → Модель ПЕРЕОЦЕНИВАЕТ риск ({kupiec_95['observed_rate']*100:.2f}% пробитий вместо 5%)")
else:
    print(f"    Не отвергаем H₀ (p = {kupiec_95['p_value']:.4f} > 0.05)")
    print(f"   → VaR 95% РАБОТАЕТ КОРРЕКТНО")

kupiec_99 = kupiec_test(n_breaches_99, n_backtest_days, 0.99)

print(f" РЕЗУЛЬТАТЫ:\n")
print(f"   Наблюдений:           {n_backtest_days}")
print(f"   Пробитий (ожидалось): {kupiec_99['expected_breaches']:.1f} (1.00%)")
print(f"   Пробитий (наблюдено): {kupiec_99['observed_breaches']} ({kupiec_99['observed_rate']*100:.2f}%)")
print(f"\n   LR-статистика:        {kupiec_99['lr_statistic']:.4f}")
print(f"   Критическое значение: {kupiec_99['critical_value']:.4f} (α = 0.05)")
print(f"   p-value:              {kupiec_99['p_value']:.4f}")

print(f"\n ВЫВОД:")
if kupiec_99['reject_h0']:
    print(f"    Отвергаем H₀ (p = {kupiec_99['p_value']:.4f} < 0.05)")
    print(f"   → VaR 99% РАБОТАЕТ НЕКОРРЕКТНО")
    if kupiec_99['observed_rate'] > kupiec_99['expected_rate']:
        print(f"   → Модель НЕДООЦЕНИВАЕТ риск ({kupiec_99['observed_rate']*100:.2f}% пробитий вместо 1%)")
    else:
        print(f"   → Модель ПЕРЕОЦЕНИВАЕТ риск ({kupiec_99['observed_rate']*100:.2f}% пробитий вместо 1%)")
else:
    print(f"    Не отвергаем H₀ (p = {kupiec_99['p_value']:.4f} > 0.05)")
    print(f"   → VaR 99% РАБОТАЕТ КОРРЕКТНО")

print()

try:
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    ax1 = axes[0]
    ax1.plot(portfolio_returns_backtest.index, portfolio_returns_backtest.values * 100,
             label='Портфельная доходность', linewidth=0.8, alpha=0.7, color='steelblue')
    ax1.axhline(y=var_95_return * 100, color='red', linestyle='--',
                label=f'VaR 95% = {var_95_return*100:.2f}%', linewidth=2)
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.3)

    if len(breach_dates_95) > 0:
        breach_returns_95 = portfolio_returns_backtest[breach_dates_95] * 100
        ax1.scatter(breach_dates_95, breach_returns_95, color='red',
                   s=60, zorder=5, marker='X', label=f'Пробития ({n_breaches_95})')

    ax1.set_title(f'Бэктест VaR 95%: Портфельные доходности vs Исторический VaR\n' +
                  f'Пробитий: {breach_rate_95*100:.2f}% (ожидалось 5.00%)',
                  fontsize=12, fontweight='bold')
    ax1.set_xlabel('Дата')
    ax1.set_ylabel('Доходность (%)')
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.fill_between(portfolio_returns_backtest.index, var_95_return * 100,
                     ax1.get_ylim()[0], alpha=0.1, color='red', label='Зона риска')

    ax2 = axes[1]
    ax2.plot(portfolio_returns_backtest.index, portfolio_returns_backtest.values * 100,
             label='Портфельная доходность', linewidth=0.8, alpha=0.7, color='steelblue')
    ax2.axhline(y=var_99_return * 100, color='darkred', linestyle='--',
                label=f'VaR 99% = {var_99_return*100:.2f}%', linewidth=2)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.3)

    if len(breach_dates_99) > 0:
        breach_returns_99 = portfolio_returns_backtest[breach_dates_99] * 100
        ax2.scatter(breach_dates_99, breach_returns_99, color='darkred',
                   s=60, zorder=5, marker='X', label=f'Пробития ({n_breaches_99})')

    ax2.set_title(f'Бэктест VaR 99%: Портфельные доходности vs Исторический VaR\n' +
                  f'Пробитий: {breach_rate_99*100:.2f}% (ожидалось 1.00%)',
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel('Дата')
    ax2.set_ylabel('Доходность (%)')
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.fill_between(portfolio_returns_backtest.index, var_99_return * 100,
                     ax2.get_ylim()[0], alpha=0.1, color='darkred', label='Зона риска')

    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"  Ошибка при построении графиков: {e}\n")

backtest_results = {
    'n_days': n_backtest_days,
    'period_start': backtest_data['period_start'],
    'period_end': backtest_data['period_end'],
    'n_original_days': n_original_days,
    'var_method': 'historical',

    'var_95_return': var_95_return,
    'var_99_return': var_99_return,

    'portfolio_returns': portfolio_returns_backtest,
    'mean_return': portfolio_returns_backtest.mean(),
    'std_return': portfolio_returns_backtest.std(),
    'min_return': portfolio_returns_backtest.min(),
    'max_return': portfolio_returns_backtest.max(),

    'breaches_95': n_breaches_95,
    'breach_rate_95': breach_rate_95,
    'expected_breaches_95': expected_breaches_95,
    'breach_dates_95': breach_dates_95,

    'breaches_99': n_breaches_99,
    'breach_rate_99': breach_rate_99,
    'expected_breaches_99': expected_breaches_99,
    'breach_dates_99': breach_dates_99,

    'kupiec_95': kupiec_95,
    'kupiec_99': kupiec_99
}

print(" ИТОГОВАЯ СВОДКА ИСТОРИЧЕСКОГО БЭКТЕСТА VaR:\n")

print(f"   Исходный период:      {priced_df.index[0].date()} - {priced_df.index[-1].date()} ({n_original_days} дней)")
print(f"   Бэктест период:       {backtest_data['period_start'].date()} - {backtest_data['period_end'].date()} ({n_backtest_days} дней)")
print(f"   Метод расчета VaR:     ИСТОРИЧЕСКИЙ (квантили на исходном периоде)")
print(f"   Активов в портфеле:   {n_backtest_assets}")

print(f"   VaR 95% (5-й процентиль):   {var_95_return*100:>7.2f}%")
print(f"   VaR 99% (1-й процентиль):   {var_99_return*100:>7.2f}%")

print(f"   Средняя доходность:   {backtest_results['mean_return']*100:>7.3f}%")
print(f"   Волатильность:        {backtest_results['std_return']*100:>7.3f}%")
print(f"   Min доходность:       {backtest_results['min_return']*100:>7.3f}%")
print(f"   Max доходность:       {backtest_results['max_return']*100:>7.3f}%")

print(f"   VaR порог:            {var_95_return*100:>7.2f}%")
print(f"   Пробитий (ожидалось): {expected_breaches_95:>7.1f} (5.00%)")
print(f"   Пробитий (наблюдено): {n_breaches_95:>7} ({breach_rate_95*100:.2f}%)")
print(f"   Тест Купиеца:")
print(f"      LR-статистика:     {kupiec_95['lr_statistic']:>7.4f}")
print(f"      p-value:           {kupiec_95['p_value']:>7.4f}")
print(f"      Результат:         {' ОТВЕРГНУТЬ H₀' if kupiec_95['reject_h0'] else ' НЕ ОТВЕРГАТЬ H₀'}")

print(f"   VaR порог:            {var_99_return*100:>7.2f}%")
print(f"   Пробитий (ожидалось): {expected_breaches_99:>7.1f} (1.00%)")
print(f"   Пробитий (наблюдено): {n_breaches_99:>7} ({breach_rate_99*100:.2f}%)")
print(f"   Тест Купиеца:")
print(f"      LR-статистика:     {kupiec_99['lr_statistic']:>7.4f}")
print(f"      p-value:           {kupiec_99['p_value']:>7.4f}")
print(f"      Результат:         {' ОТВЕРГНУТЬ H₀' if kupiec_99['reject_h0'] else ' НЕ ОТВЕРГАТЬ H₀'}")

if not kupiec_95['reject_h0'] and not kupiec_99['reject_h0']:
    print("    ИСТОРИЧЕСКИЙ VaR РАБОТАЕТ КОРРЕКТНО")
    print("      Оба тесты (95% и 99%) не отвергают нулевую гипотезу.")
    print("      Частота пробитий соответствует ожидаемой на бэктест-периоде.")
elif kupiec_95['reject_h0'] and kupiec_99['reject_h0']:
    print("    ИСТОРИЧЕСКИЙ VaR РАБОТАЕТ НЕКОРРЕКТНО")
    print("      Оба тесты (95% и 99%) отвергают нулевую гипотезу.")
    if breach_rate_95 > 0.05 and breach_rate_99 > 0.01:
        print("      → Модель НЕДООЦЕНИВАЕТ риск на бэктест-периоде")
        print("      → Возможен режимный сдвиг (выше волатильность)")
    else:
        print("      → Модель ПЕРЕОЦЕНИВАЕТ риск на бэктест-периоде")
else:
    print("     ИСТОРИЧЕСКИЙ VaR РАБОТАЕТ ЧАСТИЧНО КОРРЕКТНО")
    if kupiec_95['reject_h0']:
        print("      VaR 95% отвергнут, VaR 99% не отвергнут")
    else:
        print("      VaR 99% отвергнут, VaR 95% не отвергнут")

print(f"\n ДОСТУПНЫЕ ПЕРЕМЕННЫЕ:\n")
print(f"   backtest_results:         словарь со всеми результатами")
print(f"   portfolio_returns_backtest: временной ряд доходностей бэктеста")
print(f"   portfolio_returns_original: временной ряд доходностей исходного периода")
print(f"   breach_dates_95:          список дат пробития VaR 95%")
print(f"   breach_dates_99:          список дат пробития VaR 99%")
print(f"   var_95_return, var_99_return: VaR пороги в процентах\n")

# In[ ]:


if 'backtest_data' in locals() and 'asset_names' in backtest_data:
    backtest_assets = backtest_data['asset_names']
elif 'returns_backtest' in locals() and hasattr(returns_backtest, 'columns'):
    backtest_assets = returns_backtest.columns.tolist()
else:
    raise ValueError("Не удается определить активы из бэктест-периода (3.7.2)")

print(f" АКТИВЫ ИЗ БЭКТЕСТ-ПЕРИОДА:\n   {', '.join(backtest_assets)}")
print(f"   Количество активов: {len(backtest_assets)}\n")

strategy_assets = strategy.asset_names

print(f" АКТИВЫ ИЗ СТРАТЕГИИ:\n   {', '.join(strategy_assets)}")
print(f"   Количество активов: {len(strategy_assets)}\n")

common_assets = list(set(backtest_assets) & set(strategy_assets))
common_assets.sort()

print(f" ПЕРЕСЕЧЕНИЕ АКТИВОВ:\n   {', '.join(common_assets)}")
print(f"   Количество активов: {len(common_assets)}\n")

if len(common_assets) != len(backtest_assets):
    print(f"  ВНИМАНИЕ: не все активы бэктеста есть в стратегии!")
    missing_in_strategy = set(backtest_assets) - set(strategy_assets)
    if missing_in_strategy:
        print(f"   Отсутствуют в стратегии: {', '.join(missing_in_strategy)}\n")

if len(common_assets) != len(strategy_assets):
    print(f"  ВНИМАНИЕ: в стратегии есть лишние активы!")
    extra_in_strategy = set(strategy_assets) - set(backtest_assets)
    if extra_in_strategy:
        print(f"   Лишние активы: {', '.join(extra_in_strategy)}")
        print(f"   → Они будут ИСКЛЮЧЕНЫ из МК симуляции\n")

filtered_assets = common_assets

print(f" ДЛЯ МК СИМУЛЯЦИИ БУДУТ ИСПОЛЬЗОВАНЫ:\n   {', '.join(filtered_assets)}")
print(f"   Количество активов: {len(filtered_assets)}\n")

required_vars = {
    'results': 'Результаты',
    'strategy': 'HJBStrategy объект',
    'X_0': 'Начальный капитал',
    'backtest_data': 'Информация о периоде',
    'backtest_results': 'Результаты исторического бэктеста',
    't_grid': 'Временная сетка'
}

print(" Проверка наличия данных:\n")

missing_vars = []
for var_name, description in required_vars.items():
    try:
        test_var = eval(var_name)
        print(f"    {var_name}: найдена ({description})")
    except NameError:
        missing_vars.append((var_name, description))
        print(f"    {var_name}: не найдена ({description})")

if missing_vars:
    error_msg = "\n Отсутствуют следующие переменные:\n"
    for var_name, description in missing_vars:
        error_msg += f"   • {var_name} ({description})\n"
    error_msg += "\nУбедитесь, что выполнены блоки 3.5, 3.7.1 и 3.7.2\n"
    raise NameError(error_msg)

print()

try:
    var_95_mc_original = results['var_capital_95']
    var_99_mc_original = results['var_capital_99']

    var_95_return_mc = (var_95_mc_original - X_0) / X_0
    var_99_return_mc = (var_99_mc_original - X_0) / X_0

    print(f" VaR ИЗ ИСХОДНОЙ МК СИМУЛЯЦИИ:\n")
    print(f"   95% VaR:")
    print(f"      Капитал:      {var_95_mc_original:>15,.0f} ₽")
    print(f"      Доходность:   {var_95_return_mc*100:>15.2f}%")

    print(f"\n   99% VaR:")
    print(f"      Капитал:      {var_99_mc_original:>15,.0f} ₽")
    print(f"      Доходность:   {var_99_return_mc*100:>15.2f}%\n")

except KeyError as e:
    print(f" ОШИБКА: В results отсутствует ключ {e}\n")
    raise

mu_full = strategy.mu
cov_matrix_full = strategy.cov_matrix
asset_names_full = strategy.asset_names

asset_indices = [list(asset_names_full).index(asset) for asset in filtered_assets]

mu = mu_full[asset_indices]
cov_matrix = cov_matrix_full[np.ix_(asset_indices, asset_indices)]
asset_names = filtered_assets

n_assets = len(asset_names)
rf = strategy.risk_free_rate
gamma = strategy.gamma

print(f" ПАРАМЕТРЫ СТРАТЕГИИ (ПОСЛЕ ФИЛЬТРАЦИИ):\n")
print(f"   Активов:              {n_assets}")
print(f"   Активы:               {', '.join(asset_names)}")
print(f"   Коэффициент риск-аверсии (γ): {gamma:.1f}")
print(f"   Безрисковая ставка:   {rf*100:.2f}%")

print(f"\n ПАРАМЕТРЫ ДИНАМИКИ (ПОСЛЕ ФИЛЬТРАЦИИ):\n")
print(f"   Среднее (μ) вектор:\n   {mu}\n")
print(f"   Ковариационная матрица (фрагмент):\n   {cov_matrix[:3, :3]}\n")

T = t_grid[-1]
n_steps = len(t_grid)
dt = T / (n_steps - 1)

print(f"⏱  ПАРАМЕТРЫ ИСХОДНОЙ СИМУЛЯЦИИ:\n")
print(f"   Временной горизонт:   {T:.1f} {'год' if T == 1 else 'года'}")
print(f"   Временных шагов:      {n_steps}")
print(f"   Количество путей:     {len(X_paths):,}\n")

eigenvalues = np.linalg.eigvalsh(cov_matrix)
min_eig = eigenvalues.min()

if min_eig > 1e-10:
    L = np.linalg.cholesky(cov_matrix)
else:
    epsilon = max(1e-6, abs(min_eig) * 10)
    cov_matrix_reg = cov_matrix + epsilon * np.eye(n_assets)
    L = np.linalg.cholesky(cov_matrix_reg)

n_paths_backtest = len(X_paths)
random_seed_backtest = 123

np.random.seed(random_seed_backtest)

print(f"  Параметры МК симуляции на бэктест-периоде:\n")
print(f"   Траекторий (n_paths):    {n_paths_backtest:,}")
print(f"   Временных шагов:         {n_steps}")
print(f"   Активов (отфильтровано): {n_assets}")
print(f"   Random seed:             {random_seed_backtest}\n")

start_time = time.time()

X_paths_backtest = np.zeros((n_paths_backtest, n_steps))
X_paths_backtest[:, 0] = X_0

dW = np.random.randn(n_paths_backtest, n_steps - 1, n_assets)
dR = np.zeros((n_paths_backtest, n_steps - 1, n_assets))

for t in range(n_steps - 1):
    dZ = dW[:, t, :] @ L.T
    dR[:, t, :] = (mu - 0.5 * np.diag(cov_matrix)) * dt + np.sqrt(dt) * dZ

    weights_t = strategy.get_optimal_weights()
    weights_t = weights_t[asset_indices]
    weights_t = weights_t / weights_t.sum()

    portfolio_return = np.sum(dR[:, t, :] * weights_t, axis=1)

    X_paths_backtest[:, t + 1] = X_paths_backtest[:, t] * np.exp(portfolio_return)

    if (t + 1) % (n_steps // 4) == 0:
        print(f"   Обработано {t + 1}/{n_steps - 1} временных шагов...")

elapsed = time.time() - start_time

final_capitals_backtest = X_paths_backtest[:, -1]
final_returns_backtest = (final_capitals_backtest - X_0) / X_0

breaches_95_mc = final_capitals_backtest < var_95_mc_original
breaches_99_mc = final_capitals_backtest < var_99_mc_original

n_breaches_95_mc = breaches_95_mc.sum()
n_breaches_99_mc = breaches_99_mc.sum()

breach_rate_95_mc = n_breaches_95_mc / n_paths_backtest
breach_rate_99_mc = n_breaches_99_mc / n_paths_backtest

expected_breaches_95_mc = n_paths_backtest * 0.05
expected_breaches_99_mc = n_paths_backtest * 0.01

print(f" СТАТИСТИКА ФИНАЛЬНЫХ КАПИТАЛОВ ИЗ НОВОЙ МК СИМУЛЯЦИИ:\n")
print(f"   Среднее значение:     {final_capitals_backtest.mean():>15,.0f} ₽")
print(f"   Медиана:              {np.median(final_capitals_backtest):>15,.0f} ₽")
print(f"   Std Dev:              {final_capitals_backtest.std():>15,.0f} ₽")
print(f"   Min:                  {final_capitals_backtest.min():>15,.0f} ₽")
print(f"   Max:                  {final_capitals_backtest.max():>15,.0f} ₽\n")

print(f" ПРОБИТИЯ VaR 95% (МК СИМУЛЯЦИЯ):\n")
print(f"   VaR порог капитала:     {var_95_mc_original:>15,.0f} ₽ ({var_95_return_mc*100:>6.2f}%)")
print(f"   Количество пробитий:    {n_breaches_95_mc:>7} из {n_paths_backtest:,}")
print(f"   Частота пробитий:       {breach_rate_95_mc*100:>7.2f}% (ожидалось 5.00%)")
print(f"   Ожидалось пробитий:     {expected_breaches_95_mc:>7.1f}\n")

print(f" ПРОБИТИЯ VaR 99% (МК СИМУЛЯЦИЯ):\n")
print(f"   VaR порог капитала:     {var_99_mc_original:>15,.0f} ₽ ({var_99_return_mc*100:>6.2f}%)")
print(f"   Количество пробитий:    {n_breaches_99_mc:>7} из {n_paths_backtest:,}")
print(f"   Частота пробитий:       {breach_rate_99_mc*100:>7.2f}% (ожидалось 1.00%)")
print(f"   Ожидалось пробитий:     {expected_breaches_99_mc:>7.1f}\n")

def kupiec_test_stable(n_breaches, n_observations, confidence_level):

    alpha = 1 - confidence_level
    p_hat = n_breaches / n_observations

    if n_breaches == 0:
        lr_stat = -2 * n_observations * np.log(1 - alpha)
    elif n_breaches == n_observations:
        lr_stat = -2 * n_observations * np.log(alpha)
    else:

        lr_stat = 2 * (
            n_breaches * np.log(p_hat / alpha) +
            (n_observations - n_breaches) * np.log((1 - p_hat) / (1 - alpha))
        )

    p_value = 1 - stats.chi2.cdf(lr_stat, df=1)
    critical_value = stats.chi2.ppf(0.95, df=1)
    reject_h0 = lr_stat > critical_value

    return {
        'lr_statistic': lr_stat,
        'p_value': p_value,
        'critical_value': critical_value,
        'reject_h0': reject_h0,
        'expected_breaches': n_observations * alpha,
        'observed_breaches': n_breaches,
        'expected_rate': alpha,
        'observed_rate': p_hat
    }

kupiec_95_mc = kupiec_test_stable(n_breaches_95_mc, n_paths_backtest, 0.95)

print(f" РЕЗУЛЬТАТЫ:\n")
print(f"   Наблюдений:           {n_paths_backtest:,}")
print(f"   Пробитий (ожидалось): {kupiec_95_mc['expected_breaches']:.1f} (5.00%)")
print(f"   Пробитий (наблюдено): {kupiec_95_mc['observed_breaches']} ({kupiec_95_mc['observed_rate']*100:.2f}%)")
print(f"\n   LR-статистика:        {kupiec_95_mc['lr_statistic']:.4f}")
print(f"   Критическое значение: {kupiec_95_mc['critical_value']:.4f} (α = 0.05)")
print(f"   p-value:              {kupiec_95_mc['p_value']:.6f}")

print(f"\n ВЫВОД:")
if kupiec_95_mc['reject_h0']:
    print(f"    Отвергаем H₀ (p = {kupiec_95_mc['p_value']:.6f} < 0.05)")
    print(f"   → МК модель VaR 95% РАБОТАЕТ НЕКОРРЕКТНО")
else:
    print(f"    Не отвергаем H₀ (p = {kupiec_95_mc['p_value']:.6f} > 0.05)")
    print(f"   → МК модель VaR 95% РАБОТАЕТ КОРРЕКТНО")

kupiec_99_mc = kupiec_test_stable(n_breaches_99_mc, n_paths_backtest, 0.99)

print(f" РЕЗУЛЬТАТЫ:\n")
print(f"   Наблюдений:           {n_paths_backtest:,}")
print(f"   Пробитий (ожидалось): {kupiec_99_mc['expected_breaches']:.1f} (1.00%)")
print(f"   Пробитий (наблюдено): {kupiec_99_mc['observed_breaches']} ({kupiec_99_mc['observed_rate']*100:.2f}%)")
print(f"\n   LR-статистика:        {kupiec_99_mc['lr_statistic']:.4f}")
print(f"   Критическое значение: {kupiec_99_mc['critical_value']:.4f} (α = 0.05)")
print(f"   p-value:              {kupiec_99_mc['p_value']:.6f}")

print(f"\n ВЫВОД:")
if kupiec_99_mc['reject_h0']:
    print(f"    Отвергаем H₀ (p = {kupiec_99_mc['p_value']:.6f} < 0.05)")
    print(f"   → МК модель VaR 99% РАБОТАЕТ НЕКОРРЕКТНО")
else:
    print(f"    Не отвергаем H₀ (p = {kupiec_99_mc['p_value']:.6f} > 0.05)")
    print(f"   → МК модель VaR 99% РАБОТАЕТ КОРРЕКТНО")

print()

hist_breaches_95 = backtest_results['breaches_95']
hist_breaches_99 = backtest_results['breaches_99']
hist_breach_rate_95 = backtest_results['breach_rate_95']
hist_breach_rate_99 = backtest_results['breach_rate_99']
hist_kupiec_95 = backtest_results['kupiec_95']
hist_kupiec_99 = backtest_results['kupiec_99']
n_hist_days = backtest_results['n_days']

print(" СРАВНЕНИЕ РЕЗУЛЬТАТОВ VaR 95%:\n")
print(f"{'Метрика':<30} | {'Исторический':<20} | {'МК симуляция':<20}")
print(f"{'-'*30}-+-{'-'*20}-+-{'-'*20}")
print(f"{'Пробитий':<30} | {hist_breaches_95:>6}/{n_hist_days:<12} | {n_breaches_95_mc:>6}/{n_paths_backtest:<12}")
print(f"{'Частота пробитий':<30} | {hist_breach_rate_95*100:>7.2f}% (ож. 5%)  | {breach_rate_95_mc*100:>7.2f}% (ож. 5%)")
print(f"{'LR-статистика':<30} | {hist_kupiec_95['lr_statistic']:>18.4f} | {kupiec_95_mc['lr_statistic']:>18.4f}")
print(f"{'p-value':<30} | {hist_kupiec_95['p_value']:>18.6f} | {kupiec_95_mc['p_value']:>18.6f}")
print(f"{'Результат':<30} | {'OK' if not hist_kupiec_95['reject_h0'] else 'FAIL':<20} | {'OK' if not kupiec_95_mc['reject_h0'] else 'FAIL':<20}")

print(f"\n СРАВНЕНИЕ РЕЗУЛЬТАТОВ VaR 99%:\n")
print(f"{'Метрика':<30} | {'Исторический':<20} | {'МК симуляция':<20}")
print(f"{'-'*30}-+-{'-'*20}-+-{'-'*20}")
print(f"{'Пробитий':<30} | {hist_breaches_99:>6}/{n_hist_days:<12} | {n_breaches_99_mc:>6}/{n_paths_backtest:<12}")
print(f"{'Частота пробитий':<30} | {hist_breach_rate_99*100:>7.2f}% (ож. 1%)  | {breach_rate_99_mc*100:>7.2f}% (ож. 1%)")
print(f"{'LR-статистика':<30} | {hist_kupiec_99['lr_statistic']:>18.4f} | {kupiec_99_mc['lr_statistic']:>18.4f}")
print(f"{'p-value':<30} | {hist_kupiec_99['p_value']:>18.6f} | {kupiec_99_mc['p_value']:>18.6f}")
print(f"{'Результат':<30} | {'OK' if not hist_kupiec_99['reject_h0'] else 'FAIL':<20} | {'OK' if not kupiec_99_mc['reject_h0'] else 'FAIL':<20}")

print()

try:
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    ax = axes[0, 0]
    ax.hist(final_capitals_backtest, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(x=var_95_mc_original, color='red', linestyle='--', linewidth=2,
               label=f'VaR 95% = {var_95_mc_original:,.0f} ₽')
    ax.axvline(x=X_0, color='green', linestyle='-', linewidth=2, label=f'Начальный = {X_0:,.0f} ₽')
    ax.set_title(f'Распределение финальных капиталов (МК)\nПробитий: {n_breaches_95_mc} ({breach_rate_95_mc*100:.2f}%)',
                 fontweight='bold')
    ax.set_xlabel('Капитал (₽)')
    ax.set_ylabel('Частота')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    ax.hist(final_capitals_backtest, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(x=var_99_mc_original, color='darkred', linestyle='--', linewidth=2,
               label=f'VaR 99% = {var_99_mc_original:,.0f} ₽')
    ax.axvline(x=X_0, color='green', linestyle='-', linewidth=2, label=f'Начальный = {X_0:,.0f} ₽')
    ax.set_title(f'Распределение финальных капиталов (МК)\nПробитий: {n_breaches_99_mc} ({breach_rate_99_mc*100:.2f}%)',
                 fontweight='bold')
    ax.set_xlabel('Капитал (₽)')
    ax.set_ylabel('Частота')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    categories = ['Исторический\nбэктест', 'МК\nсимуляция']
    rates = [hist_breach_rate_95 * 100, breach_rate_95_mc * 100]
    expected = 5.0
    colors = ['green' if not hist_kupiec_95['reject_h0'] else 'red',
              'green' if not kupiec_95_mc['reject_h0'] else 'red']

    bars = ax.bar(categories, rates, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.axhline(y=expected, color='blue', linestyle='--', linewidth=2, label=f'Ожидаемая (5%)')
    ax.set_ylabel('Частота пробитий (%)')
    ax.set_title('Сравнение частоты пробитий VaR 95%', fontweight='bold')
    ax.set_ylim([0, max(10, max(rates) * 1.2)])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.2f}%', ha='center', va='bottom', fontweight='bold')

    ax = axes[1, 1]
    rates = [hist_breach_rate_99 * 100, breach_rate_99_mc * 100]
    expected = 1.0
    colors = ['green' if not hist_kupiec_99['reject_h0'] else 'red',
              'green' if not kupiec_99_mc['reject_h0'] else 'red']

    bars = ax.bar(categories, rates, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.axhline(y=expected, color='blue', linestyle='--', linewidth=2, label=f'Ожидаемая (1%)')
    ax.set_ylabel('Частота пробитий (%)')
    ax.set_title('Сравнение частоты пробитий VaR 99%', fontweight='bold')
    ax.set_ylim([0, max(5, max(rates) * 1.2)])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.2f}%', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.show()


except Exception as e:
    print(f"  Ошибка при построении графиков: {e}\n")

mc_backtest_results = {
    'n_paths': n_paths_backtest,
    'n_steps': n_steps,
    'n_assets_filtered': n_assets,
    'asset_names_filtered': filtered_assets,
    'var_method': 'monte_carlo',
    'var_95_capital': var_95_mc_original,
    'var_99_capital': var_99_mc_original,
    'var_95_return': var_95_return_mc,
    'var_99_return': var_99_return_mc,
    'final_capitals': final_capitals_backtest,
    'final_returns': final_returns_backtest,
    'mean_final': final_capitals_backtest.mean(),
    'median_final': np.median(final_capitals_backtest),
    'std_final': final_capitals_backtest.std(),
    'breaches_95': n_breaches_95_mc,
    'breach_rate_95': breach_rate_95_mc,
    'expected_breaches_95': expected_breaches_95_mc,
    'breaches_99': n_breaches_99_mc,
    'breach_rate_99': breach_rate_99_mc,
    'expected_breaches_99': expected_breaches_99_mc,
    'kupiec_95': kupiec_95_mc,
    'kupiec_99': kupiec_99_mc
}

print(" ИТОГОВАЯ СВОДКА МК БЭКТЕСТА:\n")

print(f"   Пробитий (ожидалось):  {expected_breaches_95_mc:>7.1f} (5.00%)")
print(f"   Пробитий (наблюдено):  {n_breaches_95_mc:>7} ({breach_rate_95_mc*100:.2f}%)")
print(f"   LR-статистика:         {kupiec_95_mc['lr_statistic']:>7.4f}")
print(f"   p-value:               {kupiec_95_mc['p_value']:>7.6f}")
print(f"   Результат:             {'ОТВЕРГНУТЬ H₀' if kupiec_95_mc['reject_h0'] else 'НЕ ОТВЕРГАТЬ H₀'}")

print(f"   Пробитий (ожидалось):  {expected_breaches_99_mc:>7.1f} (1.00%)")
print(f"   Пробитий (наблюдено):  {n_breaches_99_mc:>7} ({breach_rate_99_mc*100:.2f}%)")
print(f"   LR-статистика:         {kupiec_99_mc['lr_statistic']:>7.4f}")
print(f"   p-value:               {kupiec_99_mc['p_value']:>7.6f}")
print(f"   Результат:             {'ОТВЕРГНУТЬ H₀' if kupiec_99_mc['reject_h0'] else 'НЕ ОТВЕРГАТЬ H₀'}")

print(f" АКТИВЫ СОГЛАСОВАНЫ МЕЖДУ БЛОКАМИ:")
print(f"   • 3.7.2 (исторический): {', '.join(backtest_assets)}")
print(f"   • 3.7.3 (МК):           {', '.join(filtered_assets)}\n")

if not kupiec_95_mc['reject_h0'] and not kupiec_99_mc['reject_h0']:
    print(" МК МОДЕЛЬ VaR КАЛИБРОВАНА КОРРЕКТНО")
    print("   → Проблемы в историческом бэктесте связаны с режимными сдвигами\n")
elif kupiec_95_mc['reject_h0'] and kupiec_99_mc['reject_h0']:
    print(" МК МОДЕЛЬ VaR НЕКОРРЕКТНА")
    print("   → Проблема в самой модели/калибровке\n")
else:
    print("  МК МОДЕЛЬ VaR РАБОТАЕТ ЧАСТИЧНО")
    print(f"   • VaR 95%: {'OK' if not kupiec_95_mc['reject_h0'] else 'FAIL'}")
    print(f"   • VaR 99%: {'OK' if not kupiec_99_mc['reject_h0'] else 'FAIL'}\n")
