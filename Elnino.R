install.packages(c(
  "tidyverse",
  "lubridate",
  "readxl",
  "forecast",
  "tseries",
  "urca",
  "lmtest",
  "sandwich",
  "corrplot",
  "ggplot2",
  "car",
  "PerformanceAnalytics"
))

library(readxl)

data <- read_excel("D:\\Elnino\\dataset\\Dataset.xlsx")

str(data)
summary(data)
colSums(is.na(data))
sum(duplicated(data))

data$Date <- as.Date(data$Date)
str(data)

library(ggplot2)

ggplot(data, aes(x = Date, y = ONI)) +
  geom_line(color = "blue", linewidth = 1) +
  labs(
    title = "Oceanic Niño Index (ONI) Over Time",
    x = "Year",
    y = "ONI"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(x = Date, y = CRUDE_BRENT)) +
  geom_line(color = "blue", linewidth = 1) +
  labs(
    title = "Crude Oil(Brent) Over Time",
    x = "Year",
    y = "Crude Oil(Brent)"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(x = Date, y = USD_INR)) +
  geom_line(color = "blue", linewidth = 1) +
  labs(
    title = "Exchange Rate Over Time",
    x = "Year",
    y = "USD_INR"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(x = Date, y = `food price`)) +
  geom_line(color = "blue", linewidth = 1) +
  labs(
    title = "Food price Over Time",
    x = "Year",
    y = "Food price"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(x = Date, y = `fuel price`)) +
  geom_line(color = "blue", linewidth = 1) +
  labs(
    title = "Fuel price Over Time",
    x = "Year",
    y = "Fuel price"
  ) +
  theme_minimal(base_size = 14)

library(ggplot2)

ggplot(data, aes(x = ONI)) +
  geom_histogram(bins = 20, fill = "steelblue", color = "black") +
  labs(
    title = "Histogram of Oceanic Niño Index (ONI)",
    x = "ONI",
    y = "Frequency"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(x = CRUDE_BRENT)) +
  geom_histogram(bins = 20, fill = "steelblue", color = "black") +
  labs(
    title = "Histogram of Crude Oil Brent",
    x = "Crude Oil (Brent)",
    y = "Frequency"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(x = USD_INR)) +
  geom_histogram(bins = 20, fill = "steelblue", color = "black") +
  labs(
    title = "Histogram of Exchange Rate",
    x = "Exchange Rate",
    y = "Frequency"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(x = `food price`)) +
  geom_histogram(bins = 20, fill = "steelblue", color = "black") +
  labs(
    title = "Histogram of Food Price",
    x = "Food Price",
    y = "Frequency"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(x =  `fuel price`)) +
  geom_histogram(bins = 20, fill = "steelblue", color = "black") +
  labs(
    title = "Histogram of Fuel Price",
    x = "Fuel Price",
    y = "Frequency"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(y = USD_INR)) +
  geom_boxplot(fill = "steelblue", color = "black") +
  labs(
    title = "Boxplot of Exchange Rate",
    y = "Exchange Rate"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(y = CRUDE_BRENT)) +
  geom_boxplot(fill = "steelblue", color = "black") +
  labs(
    title = "Boxplot of Crude Oil(Brent)",
    y = "Crude Oil(Brent)"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(y = `fuel price`)) +
  geom_boxplot(fill = "steelblue", color = "black") +
  labs(
    title = "Boxplot of Fuel Price",
    y = "Fuel price"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(y = `food price`)) +
  geom_boxplot(fill = "steelblue", color = "black") +
  labs(
    title = "Boxplot of Food Price",
    y = "Food price"
  ) +
  theme_minimal(base_size = 14)

ggplot(data, aes(y = ONI)) +
  geom_boxplot(fill = "steelblue", color = "black") +
  labs(
    title = "Boxplot of ONI",
    y = "Oceanic Nino Index"
  ) +
  theme_minimal(base_size = 14)

cor_matrix <- cor(
  data[, c("ONI",
           "CRUDE_BRENT",
           "USD_INR",
           "food price",
           "fuel price")],
  use="complete.obs"
)
cor_matrix

library(corrplot)
corrplot(cor_matrix,
         method="color",
         type="upper",
         addCoef.col="black",
         tl.col="black",
         tl.srt=45)

ggplot(data, aes(ONI, `food price`))+
  geom_point()+
  geom_smooth(method="lm")

ggplot(data, aes(ONI, `fuel price`))+
  geom_point()+
  geom_smooth(method="lm")

ggplot(data, aes(ONI, USD_INR))+
  geom_point()+
  geom_smooth(method="lm")

ggplot(data, aes(ONI, CRUDE_BRENT))+
  geom_point()+
  geom_smooth(method="lm")

cor.test(data$`food price`, data$ONI)

cor.test(data$`food price`, data$`fuel price`)

cor.test(data$`food price`, data$CRUDE_BRENT)

cor.test(data$`food price`, data$USD_INR)

cor.test(data$`food price`,
         data$ONI,
         method="spearman")

cor.test(data$`fuel price`,
         data$ONI,
         method="spearman")

cor.test(data$USD_INR,
         data$ONI,
         method="spearman")

cor.test(data$CRUDE_BRENT,
         data$ONI,
         method="spearman")

library(tidyverse)
data <- data %>%
  mutate(
    ONI_Lag1 = lag(ONI, 1),
    ONI_Lag2 = lag(ONI, 2),
    ONI_Lag3 = lag(ONI, 3),
    ONI_Lag6 = lag(ONI, 6)
  )

cor(data$`food price`, data$ONI_Lag1, use="complete.obs")
cor(data$`food price`, data$ONI_Lag2, use="complete.obs")
cor(data$`food price`, data$ONI_Lag3, use="complete.obs")
cor(data$`food price`, data$ONI_Lag6, use="complete.obs")


lag_results <- data.frame(
  Lag=c("0","1","2","3","6"),
  Correlation=c(
    cor(data$`food price`,data$ONI,use="complete.obs"),
    cor(data$`food price`,data$ONI_Lag1,use="complete.obs"),
    cor(data$`food price`,data$ONI_Lag2,use="complete.obs"),
    cor(data$`food price`,data$ONI_Lag3,use="complete.obs"),
    cor(data$`food price`,data$ONI_Lag6,use="complete.obs")
  )
)

lag_results

library(tseries)

adf.test(data$`food price`)
adf.test(data$ONI)
adf.test(data$CRUDE_BRENT)
adf.test(data$USD_INR)
adf.test(data$`fuel price`)

data$Food_diff  <- c(NA, diff(data$`food price`))
data$Crude_diff <- c(NA, diff(data$CRUDE_BRENT))
data$Fuel_diff  <- c(NA, diff(data$`fuel price`))

adf.test(na.omit(data$Food_diff))
adf.test(na.omit(data$Crude_diff))
adf.test(na.omit(data$Fuel_diff))

model1 <- lm(
  Food_diff ~ ONI + Fuel_diff + Crude_diff + USD_INR,
  data = data
)

summary(model1)

model2 <- lm(
  Food_diff ~ ONI_Lag2 + Fuel_diff + Crude_diff + USD_INR,
  data = data
)

summary(model2)


data <- data %>%
  mutate(
    ONI_Lag1 = lag(ONI,1),
    ONI_Lag2 = lag(ONI,2),
    ONI_Lag3 = lag(ONI,3),
    ONI_Lag6 = lag(ONI,6)
  )

model_lag3 <- lm(
  Food_diff ~ ONI_Lag3 + Fuel_diff + Crude_diff + USD_INR,
  data=data
)

summary(model_lag3)

model_lag6 <- lm(
  Food_diff ~ ONI_Lag6 + Fuel_diff + Crude_diff + USD_INR,
  data=data
)

summary(model_lag6)

library(car)
vif(model1)

library(lmtest)
bptest(model1)

dwtest(model1)

shapiro.test(residuals(model1))

library(sandwich)
library(lmtest)

coeftest(model1, vcov = vcovHC(model1, type = "HC1"))

par(mfrow=c(2,2))
plot(model1)

model0 <- lm(Food_diff ~ ONI, data = data)

model1 <- lm(Food_diff ~ ONI + Fuel_diff, data = data)

model2 <- lm(Food_diff ~ ONI + Fuel_diff + Crude_diff, data = data)
model0 <- lm(Food_diff ~ ONI, data = data)

model1 <- lm(Food_diff ~ ONI + Fuel_diff, data = data)

model2 <- lm(Food_diff ~ ONI + Fuel_diff + Crude_diff, data = data)

model3 <- lm(Food_diff ~ ONI + Fuel_diff + Crude_diff + USD_INR,
             data = data)
model0 <- lm(Food_diff ~ ONI, data = data)

model1 <- lm(Food_diff ~ ONI + Fuel_diff, data = data)

model2 <- lm(Food_diff ~ ONI + Fuel_diff + Crude_diff, data = data)

model3 <- lm(Food_diff ~ ONI + Fuel_diff + Crude_diff + USD_INR,
             data = data)
model3 <- lm(Food_diff ~ ONI + Fuel_diff + Crude_diff + USD_INR,
             data = data)

AIC(model0, model1, model2, model3)

BIC(model0, model1, model2, model3)

summary(model0)
summary(model1)
summary(model2)
summary(model3)

install.packages("Metrics")

library(Metrics)

rmse0 <- rmse(model.response(model.frame(model0)),
              fitted(model0))

rmse1 <- rmse(model.response(model.frame(model1)),
              fitted(model1))

rmse2 <- rmse(model.response(model.frame(model2)),
              fitted(model2))

rmse3 <- rmse(model.response(model.frame(model3)),
              fitted(model3))

mae0 <- mae(model.response(model.frame(model0)),
            fitted(model0))

mae1 <- mae(model.response(model.frame(model1)),
            fitted(model1))

mae2 <- mae(model.response(model.frame(model2)),
            fitted(model2))

mae3 <- mae(model.response(model.frame(model3)),
            fitted(model3))

comparison <- data.frame(
  Model = c("ONI",
            "ONI + Fuel",
            "ONI + Fuel + Crude",
            "ONI + Fuel + Crude + USD"),
  Adj_R2 = c(summary(model0)$adj.r.squared,
             summary(model1)$adj.r.squared,
             summary(model2)$adj.r.squared,
             summary(model3)$adj.r.squared),
  AIC = c(AIC(model0),
          AIC(model1),
          AIC(model2),
          AIC(model3)),
  RMSE = c(rmse0,
           rmse1,
           rmse2,
           rmse3),
  MAE = c(mae0,
          mae1,
          mae2,
          mae3)
)

comparison

library(Metrics)

model_data <- na.omit(
  data[, c("Food_diff",
           "ONI",
           "Fuel_diff",
           "Crude_diff",
           "USD_INR")]
)

ccf(data$ONI,
    data$`food price`,
    lag.max = 12,
    main = "Cross Correlation between ONI and Food Price")

food_ts <- ts(data$`food price`,
              start = c(2012,7),
              frequency = 12)

plot(decompose(food_ts))