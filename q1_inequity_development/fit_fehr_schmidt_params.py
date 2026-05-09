import itertools
import warnings

import numpy as np
import pandas as pd
from scipy.optimize import minimize

warnings.filterwarnings("ignore")


# ================= 1. 路径配置 =================
long_data_path = "Pure_Behavior_Long_For_Modeling.csv"
master_data_path = "Behavior_Ratings_Age.csv"


# ================= 2. 核心算法 =================
def fehr_schmidt_nll(params, x_self, x_other, choice):
    alpha, beta, lam = params
    u_accept = x_self - alpha * np.maximum(x_other - x_self, 0) - beta * np.maximum(x_self - x_other, 0)
    u_reject = 0

    delta_u = np.clip(u_accept - u_reject, -100, 100)
    p_accept = 1 / (1 + np.exp(-lam * delta_u))
    p_accept = np.clip(p_accept, 1e-10, 1 - 1e-10)

    ll = choice * np.log(p_accept) + (1 - choice) * np.log(1 - p_accept)
    return -np.sum(ll)


# ================= 3. 多起点大样本参数拟合 =================
print("启动高级多起点 Fehr-Schmidt 参数拟合...")
df_long = pd.read_csv(long_data_path)

# 构建初始值网格 (3 x 3 x 2 = 18个起点，跳出局部最优陷阱)
alphas_init = [0.1, 2.0, 5.0]
betas_init = [0.0, 2.0, 4.0]
lams_init = [0.5, 2.0]
grid_guesses = list(itertools.product(alphas_init, betas_init, lams_init))

bounds = [(0, 10), (-5, 5), (0.001, 10)]

results = []
sub_groups = df_long.groupby("sub")
total_subs = len(sub_groups)

for i, (sub, group) in enumerate(sub_groups, 1):
    x_s = group["x_self"].values
    x_o = group["x_other"].values
    c = group["choice"].values
    n_trials = len(c)

    best_nll = np.inf
    best_params = [np.nan, np.nan, np.nan]
    is_success = False

    for init_g in grid_guesses:
        res = minimize(
            fehr_schmidt_nll,
            init_g,
            args=(x_s, x_o, c),
            method="L-BFGS-B",
            bounds=bounds,
        )
        if res.success and res.fun < best_nll:
            best_nll = res.fun
            best_params = res.x
            is_success = True

    nll_null = -n_trials * np.log(0.5)
    pseudo_r2 = 1 - (best_nll / nll_null) if nll_null != 0 else np.nan

    tol = 1e-3
    alpha_stuck = np.isclose(best_params[0], 0, atol=tol) or np.isclose(best_params[0], 10, atol=tol)
    beta_stuck = np.isclose(best_params[1], -5, atol=tol) or np.isclose(best_params[1], 5, atol=tol)

    results.append(
        {
            "sub": sub,
            "FS_alpha": best_params[0],
            "FS_beta": best_params[1],
            "FS_lambda": best_params[2],
            "Pseudo_R2": pseudo_r2,
            "Alpha_Stuck": alpha_stuck,
            "Beta_Stuck": beta_stuck,
            "Model_Success": is_success,
        }
    )

    if i % 50 == 0:
        print(f"   已完成 {i} / {total_subs} 人...")

df_params = pd.DataFrame(results)


# ================= 4. 严格清洗与融合 =================
print("\n正在执行严苛的数据清洗与融合...")
df_master = pd.read_csv(master_data_path)

df_final = pd.merge(df_master, df_params, on="sub", how="inner")

df_final.loc[~df_final["Model_Success"], ["FS_alpha", "FS_beta", "FS_lambda"]] = np.nan
df_final.loc[df_final["Alpha_Stuck"] | df_final["Beta_Stuck"], ["FS_alpha", "FS_beta", "FS_lambda"]] = np.nan
df_final.loc[df_final["Pseudo_R2"] < 0.05, ["FS_alpha", "FS_beta", "FS_lambda"]] = np.nan

df_final = df_final.dropna(subset=["FS_alpha", "FS_beta", "FS_lambda"]).reset_index(drop=True)

out_path = "Behavior_Master_Cleaned_Params_Complete.csv"
df_final.to_csv(out_path, index=False)

valid_n = len(df_final)
drop_n = len(df_params) - valid_n
drop_rate = (drop_n / len(df_params)) * 100

print("终极建模清洗完毕！")
print(f"   - 原始总被试数: {len(df_params)} 人")
print(f"   - 剔除劣质被试: {drop_n} 人 (占总人数的 {drop_rate:.1f}%)")
print(f"   - 最终保留【三参数均高质量】被试数: {valid_n} 人")
print(f"黄金数据已保存至: {out_path}")
