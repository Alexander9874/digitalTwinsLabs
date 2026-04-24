import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, poisson, binom, uniform, chi2

df = pd.read_excel("data.xlsx", usecols="A", skiprows=2, nrows=300, header=None)
data = df.iloc[:, 0]

n = len(data)
mean = data.mean()
std_err = data.std() / np.sqrt(n)
median = data.median()
mode_series = data.mode()
mode = mode_series.iloc[0]
std_dev = data.std()
variance = data.var()
kurtosis = data.kurtosis()
skewness = data.skew()
min_val = data.min()
max_val = data.max()
total_sum = data.sum()
count = n

report = f"""
Описательная статистика выборки:
Среднее:                   {mean:.4f}
Стандартная ошибка:        {std_err:.4f}
Медиана:                   {median:.4f}
Мода:                      {mode:.4f}
Стандартное отклонение:    {std_dev:.4f}
Дисперсия выборки:         {variance:.4f}
Эксцесс:                   {kurtosis:.4f}
Асимметричность:           {skewness:.4f}
Минимум:                   {min_val:.4f}
Максимум:                  {max_val:.4f}
Сумма:                     {total_sum:.4f}
Количество:                {count}
"""
print(report)

bins = int(1 + np.log2(n))
counts, edges = np.histogram(data, bins=bins, density=True)
centers = (edges[:-1] + edges[1:]) / 2

plt.hist(data, bins=bins, density=True, alpha=0.3, edgecolor='black')

normal_pdf = norm.pdf(centers, mean, std_dev)
uniform_pdf = uniform.pdf(centers, loc=min_val, scale=max_val - min_val)
plt.bar(centers, counts, width=edges[1]-edges[0], alpha=0.3, edgecolor='black', label='Гистограмма')
plt.plot(centers, normal_pdf, marker='o', label='Нормальное')
plt.plot(centers, uniform_pdf, marker='o', label='Равномерное')

plt.title("Непрерывные распределения")
plt.xlabel("Значения")
plt.ylabel("Плотность")
plt.legend()
plt.grid(alpha=0.3)
plt.show()

data_int = data.round().astype(int)
min_int = data_int.min()
max_int = data_int.max()
bins_int = np.arange(min_int - 0.5, max_int + 1.5, 1)
plt.hist(data_int, bins=bins_int, density=True, alpha=0.6, edgecolor='black')
x_vals = np.arange(min_int, max_int + 1)
plt.plot(x_vals, poisson.pmf(x_vals, mean), marker='o', linestyle='-', label='Пуассон')
p = 1 - variance / mean
n_bin = int(round(mean / p))
plt.plot(x_vals, binom.pmf(x_vals, n_bin, p) , marker='o', linestyle='-', label='Биномиальное')

plt.title("Дискретные распределения")
plt.xlabel("Значения")
plt.ylabel("Вероятность")
plt.legend()
plt.grid(alpha=0.3)
plt.show()

def merge_small_expected(obs, exp, min_exp=5):
    obs = np.array(obs, dtype=float)
    exp = np.array(exp, dtype=float)
    merged_obs = []
    merged_exp = []
    accum_obs = 0
    accum_exp = 0
    
    for o, e in zip(obs, exp):
        accum_obs += o
        accum_exp += e
        if accum_exp >= min_exp:
            merged_obs.append(accum_obs)
            merged_exp.append(accum_exp)
            accum_obs = 0
            accum_exp = 0
    
    if accum_exp > 0:
        if len(merged_obs) == 0:
            merged_obs.append(accum_obs)
            merged_exp.append(accum_exp)
        else:
            merged_obs[-1] += accum_obs
            merged_exp[-1] += accum_exp
    
    return np.array(merged_obs), np.array(merged_exp), len(merged_obs)



counts_cont, edges_cont = np.histogram(data, bins=bins)

def expected_continuous(cdf, edges, n, params):
    exp = []
    for i in range(len(edges)-1):
        p = cdf(edges[i+1], *params) - cdf(edges[i], *params)
        exp.append(n * p)
    return np.array(exp)

# Нормальное (r=2)
exp_norm_raw = expected_continuous(norm.cdf, edges_cont, n, (mean, std_dev))
obs_norm, exp_norm, k_norm = merge_small_expected(counts_cont, exp_norm_raw)
chi2_norm = np.sum((obs_norm - exp_norm)**2 / exp_norm)
df_norm = k_norm - 2 - 1  # r=2

# Равномерное (r=2)
exp_unif_raw = expected_continuous(uniform.cdf, edges_cont, n, (min_val, max_val-min_val))
obs_unif, exp_unif, k_unif = merge_small_expected(counts_cont, exp_unif_raw)
chi2_unif = np.sum((obs_unif - exp_unif)**2 / exp_unif)
df_unif = k_unif - 2 - 1


counts_disc, _ = np.histogram(data_int, bins=bins_int)
k_disc = len(counts_disc)

def expected_discrete(pmf, edges, n, params):
    exp = []
    for i in range(len(edges)-1):
        lower = int(np.ceil(edges[i]))
        upper = int(np.floor(edges[i+1]))
        if upper < lower:
            p = 0.0
        else:
            vals = np.arange(lower, upper+1)
            p = np.sum(pmf(vals, *params))
        exp.append(n * p)
    return np.array(exp)

# Пуассона (r=1)
exp_pois_raw = expected_discrete(poisson.pmf, bins_int, n, (mean,))
obs_pois, exp_pois, k_pois = merge_small_expected(counts_disc, exp_pois_raw)
chi2_pois = np.sum((obs_pois - exp_pois)**2 / exp_pois)
df_pois = k_pois - 1 - 1

# Биномиальноеное (r=2)
exp_binom_raw = expected_discrete(binom.pmf, bins_int, n, (n_bin, p))
obs_binom, exp_binom, k_binom = merge_small_expected(counts_disc, exp_binom_raw)
chi2_binom = np.sum((obs_binom - exp_binom)**2 / exp_binom)
df_binom = k_binom - 2 - 1

alpha = 0.05

print(f"Нормальное:      chi2 = {chi2_norm:.4f}\t  df = {df_norm}\tchi2_crit = {chi2.ppf(1 - alpha, df_norm):.4f}")
print(f"Равномерное:     chi2 = {chi2_unif:.4f}\t  df = {df_unif}\tchi2_crit = {chi2.ppf(1 - alpha, df_unif):.4f}")
print(f"Биномиальноеное: chi2 = {chi2_binom:.4f}\t  df = {df_binom}\tchi2_crit = {chi2.ppf(1 - alpha, df_binom):.4f}")
print(f"Пуассона:        chi2 = {chi2_pois:.4f}\t  df = {df_pois}\tchi2_crit = {chi2.ppf(1 - alpha, df_pois):.4f}")
