# ==============================================================================
# 第一部分：环境准备与数据清洗
# ==============================================================================

# install.packages(c("readr", "dplyr", "tidyLPA", "ggplot2", "nnet", "tidyr"))

library(readr)
library(dplyr)
library(tidyLPA)
library(ggplot2)
library(nnet)
library(tidyr)

df <- read_csv("Behavior_Master_Cleaned_Params_Complete.csv")

df_scaled <- df %>%
  mutate(
    z_alpha = scale(FS_alpha)[, 1],
    z_beta = scale(FS_beta)[, 1],
    log_lambda = log(FS_lambda),
    z_lambda = scale(log_lambda)[, 1]
  )

# ==============================================================================
# 第二部分：潜在剖面分析 (LPA) 提取计算表型
# ==============================================================================

set.seed(2026)
lpa_models <- df_scaled %>%
  select(z_alpha, z_beta, z_lambda) %>%
  estimate_profiles(1:4)

print(get_fit(lpa_models))

lpa_4_model <- estimate_profiles(df_scaled %>% select(z_alpha, z_beta, z_lambda), 4)
df_result <- get_data(lpa_4_model)

df_final <- bind_cols(df, Class = as.factor(df_result$Class))

summary_stats <- df_final %>%
  group_by(Class) %>%
  summarise(
    mean_alpha = mean(FS_alpha),
    mean_beta = mean(FS_beta),
    mean_lambda = mean(FS_lambda),
    count = n(),
    .groups = "drop"
  )
print(summary_stats)

df_final <- df %>%
  mutate(
    Class_4 = as.factor(get_data(lpa_4_model)$Class)
  )

write_csv(df_final, "Behavior_Master_Cleaned_4Classes_Final.csv")
print("4 分类标签已成功写入：Behavior_Master_Cleaned_4Classes_Final.csv")

# ==============================================================================
# 第三部分：年龄轨迹建模与可视化 (四分类版)
# ==============================================================================

model_age_4 <- multinom(Class_4 ~ age, data = df_final)
summary(model_age_4)

age_seq <- seq(min(df_final$age, na.rm = TRUE), max(df_final$age, na.rm = TRUE), length.out = 100)
pred_data <- data.frame(age = age_seq)

pred_probs <- predict(model_age_4, newdata = pred_data, type = "probs")
pred_df <- cbind(pred_data, as.data.frame(pred_probs))

pred_long <- pred_df %>%
  pivot_longer(cols = -age, names_to = "Phenotype", values_to = "Probability")

p_trajectory <- ggplot(pred_long, aes(x = age, y = Probability, fill = Phenotype)) +
  geom_area(alpha = 0.85, color = "white", linewidth = 0.5) +
  scale_fill_manual(
    values = c("2" = "#B0B8B4", "1" = "#4C72B0", "3" = "#55A868", "4" = "#C44E52"),
    labels = c(
      "1" = "表型 1: 规范内化-高噪音型 (N=1078)",
      "2" = "表型 2: 其他组 (N=10)",
      "3" = "表型 3: 理性公平型 (N=79)",
      "4" = "表型 4: 理性竞争型 (N=116)"
    )
  ) +
  labs(
    title = "儿童青少年不平等厌恶计算表型的发育演替",
    x = "年龄",
    y = "表型占比概率",
    fill = "计算发育表型"
  ) +
  theme_minimal() +
  theme(
    text = element_text(size = 14, family = "sans"),
    plot.title = element_text(face = "bold", hjust = 0.5),
    plot.subtitle = element_text(hjust = 0.5, color = "grey40"),
    legend.position = "bottom",
    legend.direction = "vertical"
  ) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1))

print(p_trajectory)

# ggsave("Phenotype_Trajectory_4Classes.pdf", plot = p_trajectory, width = 8, height = 7, dpi = 300)
