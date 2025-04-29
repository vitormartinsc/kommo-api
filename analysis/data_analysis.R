library(tidyverse)
library(ggplot2)

setwd("C:/Users/vitor/kommo-api/analysis")

# Ler e processar os dados
df <- read_csv('leads_database.csv') %>% 
  rename(value = 2) %>% 
  distinct(lead_id, .keep_all = TRUE) %>% 
  mutate(value = if_else(is.na(value), 'Meta', value))

# Filtrar os dados para Google e Meta
df_filtrado <- df %>% 
  filter(value %in% c("Google", "Meta")) %>% 
  group_by(value, status) %>% 
  summarise(n = n(), .groups = "drop")

# Gráfico para Google
grafico_google <- ggplot(df_filtrado %>% filter(value == "Google"), aes(x = status, y = n)) +
  geom_bar(stat = "identity", fill = "#1f77b4") + # Azul claro
  geom_text(aes(label = n), vjust = -0.5, size = 4) + # Adiciona os números acima das barras
  labs(
    title = "Distribuição de Leads (Google)",
    x = "Status",
    y = "Quantidade de Leads"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),
    axis.text.x = element_text(angle = 45, hjust = 1)
  )

# Gráfico para Meta
grafico_meta <- ggplot(df_filtrado %>% filter(value == "Meta"), aes(x = status, y = n)) +
  geom_bar(stat = "identity", fill = "#08306b") + # Azul escuro
  geom_text(aes(label = n), vjust = -0.5, size = 4) + # Adiciona os números acima das barras
  labs(
    title = "Distribuição de Leads (Meta)",
    x = "Status",
    y = "Quantidade de Leads"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),
    axis.text.x = element_text(angle = 45, hjust = 1)
  )

# Exibir os gráficos
print(grafico_google)
print(grafico_meta)


