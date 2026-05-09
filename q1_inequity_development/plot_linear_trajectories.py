import warnings

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")


file_master = "Behavior_Master_Cleaned_Params_Complete.csv"
df = pd.read_csv(file_master)
col_alpha = next((c for c in df.columns if "alpha" in c.lower()), None)
col_beta = next((c for c in df.columns if "beta" in c.lower()), None)

print("\n正在绘制 Linear 线性发育轨迹图...")
sns.set_theme(style="ticks", context="talk", font_scale=0.9)
color_di = "#dd8452"
color_ai = "#55a868"

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle(
    "Linear Developmental Trajectories of Inequity Parameters",
    fontsize=18,
    fontweight="bold",
    y=1.05,
)

sns.regplot(
    data=df,
    x="age",
    y=col_alpha,
    ax=axes[0],
    ci=95,
    scatter_kws={"alpha": 0.3, "s": 30, "color": color_di, "edgecolor": "w"},
    line_kws={"color": "#b55d2c", "linewidth": 4},
)
axes[0].set_title("Disadvantageous Inequity (α)\nRange: [0, 10]", fontweight="bold", pad=15)
axes[0].set_xlabel("Age (Years)", fontweight="bold")
axes[0].set_ylabel("Parameter α Value", fontweight="bold")
axes[0].set_ylim(-0.5, 10.5)

sns.regplot(
    data=df,
    x="age",
    y=col_beta,
    ax=axes[1],
    ci=95,
    scatter_kws={"alpha": 0.3, "s": 30, "color": color_ai, "edgecolor": "w"},
    line_kws={"color": "#3a7a4a", "linewidth": 4},
)
axes[1].set_title("Advantageous Inequity (β)\nRange: [-5, 5]", fontweight="bold", pad=15)
axes[1].set_xlabel("Age (Years)", fontweight="bold")
axes[1].set_ylabel("Parameter β Value", fontweight="bold")

sns.despine(trim=True)
plt.tight_layout()

out_file = "Fig1D_New_FS_Params_Linear.png"
plt.savefig(out_file, dpi=300, bbox_inches="tight")
plt.close()

print(f"线性大图已生成：{out_file}")
