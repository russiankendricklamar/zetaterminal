#!/usr/bin/env python
# coding: utf-8

# # **Расчет исторического VaR**

# In[ ]:


required_vars = ['results', 'returns', 'filtered_names']
missing_vars = []

for var_name in required_vars:
    try:
        eval(var_name)
    except NameError:
        missing_vars.append(var_name)

if missing_vars:
    raise NameError(
        f" Отсутствуют переменные: {', '.join(missing_vars)}\n"
        f"Убедитесь, что выполнены блоки 2.1-2.4 и блок 3.5"
    )

X_0 = 1_000_000
optimal_weights = results['optimal_weights']
asset_names_list = list(filtered_names)
n_assets = len(asset_names_list)

print(f" Параметры анализа:")
print(f"   Начальный капитал: {X_0:,} ₽")
print(f"   Активов в портфеле: {n_assets}")
print(f"   Периодов в истории: {len(returns)}")
print(f"   Дата начала: {returns.index[0]}")
print(f"   Дата конца: {returns.index[-1]}\n")

returns_filtered = returns[asset_names_list].copy()
portfolio_returns = (returns_filtered * optimal_weights).sum(axis=1)
portfolio_losses = -portfolio_returns
portfolio_losses_rub = portfolio_losses * X_0

print(f" Статистика портфельных потерь:\n")
print(f"   Средняя потеря: {portfolio_losses_rub.mean():>12,.0f} ₽")
print(f"   Макс потеря: {portfolio_losses_rub.max():>12,.0f} ₽")
print(f"   Мин потеря: {portfolio_losses_rub.min():>12,.0f} ₽")
print(f"   Стд.отклонение: {portfolio_losses_rub.std():>12,.0f} ₽\n")

var_loss_95_hist = np.percentile(portfolio_losses_rub, 95)
var_loss_99_hist = np.percentile(portfolio_losses_rub, 99)
var_capital_95_hist = X_0 - var_loss_95_hist
var_capital_99_hist = X_0 - var_loss_99_hist

print(f" ИСТОРИЧЕСКИЙ VaR:\n")
print(f"   VaR(95%):")
print(f"     • Потеря (95-й процентиль): {var_loss_95_hist:>12,.0f} ₽  ({var_loss_95_hist/X_0*100:>6.2f}%)")
print(f"     • Капитал: {var_capital_95_hist:>12,.0f} ₽")
print(f"\n   VaR(99%):")
print(f"     • Потеря (99-й процентиль): {var_loss_99_hist:>12,.0f} ₽  ({var_loss_99_hist/X_0*100:>6.2f}%)")
print(f"     • Капитал: {var_capital_99_hist:>12,.0f} ₽\n")

loss_var_95_mc = results['loss_var_95']
loss_var_99_mc = results['loss_var_99']
var_capital_95_mc = results['var_capital_95']
var_capital_99_mc = results['var_capital_99']

print(f" MONTE-CARLO VaR:\n")
print(f"   VaR(95%): капитал = {var_capital_95_mc:>12,.0f} ₽, потеря = {loss_var_95_mc:>12,.0f} ₽")
print(f"   VaR(99%): капитал = {var_capital_99_mc:>12,.0f} ₽, потеря = {loss_var_99_mc:>12,.0f} ₽\n")

print(f" ИСТОРИЧЕСКИЙ VaR:\n")
print(f"   VaR(95%): капитал = {var_capital_95_hist:>12,.0f} ₽, потеря = {var_loss_95_hist:>12,.0f} ₽")
print(f"   VaR(99%): капитал = {var_capital_99_hist:>12,.0f} ₽, потеря = {var_loss_99_hist:>12,.0f} ₽\n")

diff_95_capital = var_capital_95_mc - var_capital_95_hist
diff_99_capital = var_capital_99_mc - var_capital_99_hist
diff_95_loss = loss_var_95_mc - var_loss_95_hist
diff_99_loss = loss_var_99_mc - var_loss_99_hist

pct_diff_95_loss = (diff_95_loss / var_loss_95_hist * 100) if var_loss_95_hist > 0 else 0
pct_diff_99_loss = (diff_99_loss / var_loss_99_hist * 100) if var_loss_99_hist > 0 else 0

print(f" СРАВНЕНИЕ (MC - Историческое):\n")
print(f"{'Метрика':<30} | {'Историческое':<18} | {'MC':<18} | {'Разница':<18}")
print(f"{'-'*30}-+-{'-'*18}-+-{'-'*18}-+-{'-'*18}")
print(f"{'VaR(95%) потеря (₽)':<30} | {var_loss_95_hist:>16,.0f} | {loss_var_95_mc:>16,.0f} | {diff_95_loss:>+16,.0f}")
print(f"{'VaR(99%) потеря (₽)':<30} | {var_loss_99_hist:>16,.0f} | {loss_var_99_mc:>16,.0f} | {diff_99_loss:>+16,.0f}")
print(f"{'VaR(95%) потеря (%)':<30} | {var_loss_95_hist/X_0*100:>16.2f}% | {loss_var_95_mc/X_0*100:>16.2f}% | {pct_diff_95_loss:>+16.2f}%")
print(f"{'VaR(99%) потеря (%)':<30} | {var_loss_99_hist/X_0*100:>16.2f}% | {loss_var_99_mc/X_0*100:>16.2f}% | {pct_diff_99_loss:>+16.2f}%\n")

print(f" АНАЛИЗ:\n")

if diff_95_loss > 0:
    print(f" MC VaR(95%) БОЛЬШЕ, чем историческое")
    print(f"   → Модель консервативна (+{diff_95_loss:,.0f} ₽ = +{pct_diff_95_loss:.1f}%)")
else:
    print(f"  MC VaR(95%) МЕНЬШЕ, чем историческое")
    print(f"   → Модель недооценивает риск ({diff_95_loss:,.0f} ₽ = {pct_diff_95_loss:.1f}%)")

print()

if diff_99_loss > 0:
    print(f" MC VaR(99%) БОЛЬШЕ, чем историческое")
    print(f"   → Модель консервативна для хвоста (+{diff_99_loss:,.0f} ₽ = +{pct_diff_99_loss:.1f}%)")
else:
    print(f"  MC VaR(99%) МЕНЬШЕ, чем историческое")
    print(f"   → Модель недооценивает хвостовой риск ({diff_99_loss:,.0f} ₽ = {pct_diff_99_loss:.1f}%)")

print(f"\n ВЫВОД:")

if diff_95_loss > 0 and diff_99_loss > 0:
    print(f"   Модель MC консервативна и годится для использования")
    print(f"   в целях управления риском (переоценивает потери)")
elif diff_95_loss < 0 or diff_99_loss < 0:
    print(f"   Модель MC недооценивает риск")
    print(f"     Следует быть осторожнее при использовании")
else:
    print(f"   Модель в целом адекватна")

mc_vs_hist_comparison = {
    'var_95_mc': loss_var_95_mc,
    'var_99_mc': loss_var_99_mc,
    'var_95_hist': var_loss_95_hist,
    'var_99_hist': var_loss_99_hist,
    'diff_95': diff_95_loss,
    'diff_99': diff_99_loss,
    'pct_diff_95': pct_diff_95_loss,
    'pct_diff_99': pct_diff_99_loss,
}
