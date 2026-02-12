library(lme4)
library(lmerTest)
library(emmeans)
library(effectsize)
library(dplyr)

raw_data <- read.csv("data/MergedSIPMetrics.csv")

filtered_events <- c('baseline', 'olDBS', 'iolDBSI', 'KaDBSI')
filtered_data <- raw_data %>% filter(stringvisit %in% filtered_events)

event_name_mapping <- c(
    'baseline' = 'OFF',
    'olDBS' = 'cDBS',
    'KaDBSI' = 'KaDBS',
    'iolDBSI' = 'iDBS'
)

filtered_data$Condition <- event_name_mapping[filtered_data$stringvisit]
filtered_data$Condition <- factor(filtered_data$Condition, levels = c("OFF", "cDBS", "KaDBS", "iDBS"))
filtered_data$patient_num <- factor(filtered_data$patient_num)

for(i in 1:nrow(filtered_data)) {
  if(filtered_data$patient_num[i] == "RCS10") {
    filtered_data$freezes[i] = filtered_data$Percent_Freezing_HD[i]
    filtered_data$full_arrhythm[i] = filtered_data$Average_Arrhythmicity_HD[i]
  }
}

outcome_vars <- c("freezes", "full_arrhythm", "mean_shank_av")

run_analysis <- function(outcome_var) {
  tryCatch({
    cat("\n\n===", outcome_var, "===\n")

    formula <- as.formula(paste(outcome_var, "~ Condition + (1|patient_num)"))
    model <- lmer(formula, data = filtered_data)

    anova_result <- anova(model)
    eta_sq <- effectsize::eta_squared(model, partial = TRUE)
    emm <- emmeans(model, "Condition")

    contrasts <- contrast(emm, method = "trt.vs.ctrl", ref = "OFF", adjust = "sidak")

    cat("\nmodel Summary:\n")
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