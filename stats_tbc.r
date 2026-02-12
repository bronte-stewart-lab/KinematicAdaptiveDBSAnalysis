library(lme4)
library(lmerTest)
library(emmeans)
library(effectsize)
library(dplyr)
library(tidyr)

raw_data <- read.csv("data/MergedTBCMetrics.csv")

filtered_events <- c('baseline', 'olDBS', 'iolDBSI', 'KaDBSI')
raw_filtered <- raw_data %>% filter(stringvisit %in% filtered_events)

event_name_mapping <- c(
    'baseline' = 'OFF',
    'olDBS' = 'cDBS',
    'KaDBSI' = 'KaDBS',
    'iolDBSI' = 'iDBS'
)

ellipses <- raw_filtered %>%
  transmute(
    patient_num = patient_num,
    Condition = event_name_mapping[stringvisit],
    Task = "Ellipses",
    mean_freezing = Emean_freezing,
    arrhythmicity = Earrhythmicity_new,
    mean_shankav = Emean_shankav
  )

figure8 <- raw_filtered %>%
  transmute(
    patient_num = patient_num,
    Condition = event_name_mapping[stringvisit],
    Task = "Figure8",
    mean_freezing = eigmean_freezing,
    arrhythmicity = eigarrhythmicity_new,
    mean_shankav = eigmean_shankav
  )

filtered_data <- bind_rows(ellipses, figure8)
filtered_data$Condition <- factor(filtered_data$Condition, levels = c("OFF", "cDBS", "KaDBS", "iDBS"))
filtered_data$Task <- factor(filtered_data$Task)
filtered_data$patient_num <- factor(filtered_data$patient_num)

outcome_vars <- c("mean_freezing", "arrhythmicity", "mean_shankav")

run_analysis <- function(outcome_var) {
  tryCatch({
    cat("\n\n===", outcome_var, "===\n")

    formula <- as.formula(paste(outcome_var, "~ Condition + Task + (1|patient_num)"))
    model <- lmer(formula, data = filtered_data)

    anova_result <- anova(model)
    eta_sq <- effectsize::eta_squared(model, partial = TRUE)
    emm <- emmeans(model, "Condition")

    contrasts <- contrast(emm, method = "trt.vs.ctrl", ref = "OFF", adjust = "sidak")

    cat("\nmodel summary:\n")
    print(summary(model))
    cat("\nANOVA:\n")
    print(anova_result)
    cat("\npartial eta squared:\n")
    print(eta_sq)
    cat("\nestimated marginal means:\n")
    print(emm)
    cat("\npost-hoc vs OFF (sidak):\n")
    print(contrasts)
  }, error = function(e) {
    cat("\nerror:", conditionMessage(e), "\n")
  })
}

for (var in outcome_vars) {
  run_analysis(var)
}

cat("\nsample sizes per condition:\n")
print(table(filtered_data$Condition))
cat("\nn points per patient/condition:\n")
print(filtered_data %>% group_by(patient_num, Condition) %>% summarise(n = n(), .groups = "drop") %>% spread(Condition, n))