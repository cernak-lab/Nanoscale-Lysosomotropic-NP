# dotplot_two_color_SORT_BY_NES_GROUP_ABOVE_SIZE.R

library(ggplot2)
library(readr)
library(dplyr)
library(scales)  # number_format

df <- read_csv("dot plot_LA vs LEE_all.csv", show_col_types = FALSE) |>
  mutate(
    across(c(pval, padj, ES, NES, size), ~ readr::parse_number(as.character(.x))),
    `-log10(padj)` = -log10(padj),
    group2 = if_else(group == "Metabolism", "Metabolism", "Other")
  ) |>
  filter(is.finite(`-log10(padj)`)) |>
  # ---- ORDER BY NES DESC (largest first) ----
arrange(desc(NES)) |>
  # y-axis two-line labels: pathway + NES below, keep order by NES
  mutate(
    y_label = sprintf("%s\nNES: %.2f", pathway, NES),
    y_label = factor(y_label, levels = y_label)
  )

# coolwarm endpoints
col_metab <- "#B40426"
col_other <- "#A8A8A8"
two_cols  <- c("Metabolism" = col_metab, "Other" = col_other)

label_col <- "grey25"

p <- ggplot(df, aes(x = `-log10(padj)`, y = y_label)) +
  # leader lines
  geom_segment(
    aes(x = 0, xend = `-log10(padj)`, y = y_label, yend = y_label, color = group2),
    linewidth = 0.6, alpha = 0.4, show.legend = FALSE
  ) +
  # points
  geom_point(
    aes(size = size, color = group2),
    alpha = 0.9, shape = 16, stroke = 0.6
  ) +
  # size labels to the right of dots
  geom_text(
    aes(label = size),
    nudge_x = 0.35, hjust = 0, color = "black", size = 3
  ) +
  # ---- LEGENDS: Group on top (order=1), Size below (order=2) ----
scale_color_manual(
  values = two_cols,
  name   = "Group",
  guide  = guide_legend(order = 1, override.aes = list(size = 5))
) +
  scale_size_continuous(
    name    = "Size",
    range   = c(2, 10),
    breaks  = c(75, 100, 125, 150, 175),  # 5 keys
    labels  = number_format(accuracy = 1),
    guide   = guide_legend(order = 2, override.aes = list(colour = "black", alpha = 0.9))
  ) +
  # x and y scales
  scale_x_continuous(breaks = 0:5) +
  scale_y_discrete(limits = rev(levels(df$y_label))) +  # largest NES at top
  labs(x = "-log10(padj)", y = NULL, title = "GSEA Enrichment Analysis_LA_vs_LEE") +
  theme_minimal(base_family = "Arial") +
  theme(
    text = element_text(family = "Arial"),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    axis.text.y = element_text(size = 10, colour = label_col, lineheight = 0.95),
    axis.text.x = element_text(size = 10, colour = "gray20"),
    plot.title  = element_text(size = 16, hjust = 0, colour = "gray10"),
    legend.box = "vertical",
    legend.spacing.y = unit(4, "pt"),
    legend.position = c(1.02, 0.05),
    legend.justification = c(0, 0),
    plot.margin = margin(t = 5, r = 90, b = 5, l = 5)
  ) +
  coord_cartesian(xlim = c(0, 5.4), clip = "off")

print(p)
ggsave("GSEA_dotplot_two_color-lines-LAvsLEE_ALL_SORT_BY_NES_GroupAbove-2.png", p, width = 8, height = 11, dpi = 300)
#top10 width = 8, height = 7
