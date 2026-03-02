# ============================================================
# RNA-seq DE + GSEA + Volcanoes + IC50/equipotent + GO/KEGG + Comparisons
# (with SYMBOL-direction resolution to avoid Up/Down double-counting)
# Now: GSEA uses fgseaMultilevel + saved ranks for exact reproducibility
# ============================================================

# =========================
# [0] USER SETTINGS
# =========================
INPUT_FILE <- "rsem.merged.tsv"  # <-- your TSV path/name

# Doses used in experiment (µM)
DOSE_DMSO <- 0
DOSE_LEE  <- 10
DOSE_LA   <- 1.5

# Measured IC50s (µM)
IC50_LEE <- 11.5
IC50_LA  <- 1.72

# Equipotent comparison point (1 = 1×IC50)
TARGET_MULTIC50 <- 1

# Pre-filter thresholds
MIN_COUNT   <- 10
MIN_SAMPLES <- 3

# Volcano thresholds + plotting
PADJ_THRESH <- 0.05
LFC_THRESH  <- 1.0     # ← you asked to use 0.9
VOLC_XLIM   <- 4

# Optional: genes to always try to label on volcanoes
GENES_HILITE <- c("GPNMB","SLC38A4","ELOVL2","STEAP4","NNT","PGLYRP2")

# =========================
# [1] PACKAGES
# =========================
if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")

pkgs_cran <- c("tidyverse","ggplot2","ggrepel","readr","pheatmap","msigdbr")
pkgs_bioc <- c("DESeq2","fgsea","apeglm","ashr","clusterProfiler","org.Hs.eg.db","enrichplot")

for (p in pkgs_cran) if (!requireNamespace(p, quietly=TRUE)) install.packages(p, quiet=TRUE)
to_install <- pkgs_bioc[!sapply(pkgs_bioc, requireNamespace, quietly=TRUE)]
if (length(to_install)) BiocManager::install(to_install, ask=FALSE, update=TRUE)

suppressPackageStartupMessages({
  library(tidyverse); library(readr); library(ggplot2); library(ggrepel)
  library(DESeq2); library(pheatmap); library(msigdbr); library(fgsea)
  library(clusterProfiler); library(org.Hs.eg.db); library(enrichplot)
})

# =========================
# [2] HELPERS
# =========================

## 2.1 DE shrinkage (apeglm -> ashr -> raw fallback)
shrink_safe <- function(dds, contrast=NULL, coef=NULL) {
  if (!is.null(contrast)) {
    res <- results(dds, contrast = contrast)
  } else if (!is.null(coef)) {
    res <- results(dds, name = coef)
  } else stop("Provide contrast= or coef=")
  out <- try({
    if (!is.null(contrast)) lfcShrink(dds, contrast=contrast, type="apeglm")
    else lfcShrink(dds, coef=coef, type="apeglm")
  }, silent=TRUE)
  if (inherits(out,"try-error")) {
    out <- try({
      if (!is.null(contrast)) lfcShrink(dds, contrast=contrast, type="ashr")
      else lfcShrink(dds, coef=coef, type="ashr")
    }, silent=TRUE)
  }
  if (inherits(out,"try-error")) {
    message("Shrinkage failed; returning unshrunk results().")
    out <- res
  }
  out
}

## 2.2 (kept for potential fallbacks elsewhere) Robust GSEA wrapper
gsea_from_res <- function(res_obj, gene_map, collection="H") {
  res_df <- as.data.frame(res_obj)
  if ("stat" %in% names(res_df) && any(is.finite(res_df$stat))) {
    ranks <- res_df$stat; names(ranks) <- rownames(res_df)
  } else if ("pvalue" %in% names(res_df) && any(is.finite(res_df$pvalue))) {
    sval  <- sign(res_df$log2FoldChange) * (-log10(pmax(res_df$pvalue, 1e-300)))
    ranks <- sval; names(ranks) <- rownames(res_df)
  } else {
    ranks <- res_df$log2FoldChange; names(ranks) <- rownames(res_df)
  }
  ranks <- ranks[is.finite(ranks)]
  id2sym <- gene_map$external_gene_name; names(id2sym) <- gene_map$gene_id
  sym_names <- id2sym[names(ranks)]
  keep <- !is.na(sym_names) & sym_names != ""
  ranks <- ranks[keep]; sym_names <- sym_names[keep]
  agg <- tapply(ranks, sym_names, function(x) mean(x, na.rm=TRUE))
  ranks_sym <- sort(as.numeric(agg), decreasing=TRUE); names(ranks_sym) <- names(agg)
  msig <- msigdbr(species="Homo sapiens", collection=collection)
  pathways <- split(msig$gene_symbol, msig$gs_name)
  fgsea(pathways=pathways, stats=ranks_sym, minSize=15, maxSize=500) |>
    dplyr::arrange(padj)
}
gsea_tidy <- function(fg) {
  as.data.frame(fg) |>
    dplyr::mutate(leadingEdge = vapply(leadingEdge, function(x) paste(x, collapse=";"), character(1))) |>
    dplyr::arrange(padj)
}

## 2.3 Save the exact ranks used for GSEA (for audit/repro)
save_ranks <- function(res_obj, gene_map, out_file){
  res_df <- as.data.frame(res_obj)
  
  # Priority: Wald stat -> signed -log10(p) -> log2FC
  ranks <- if ("stat" %in% names(res_df) && any(is.finite(res_df$stat))) {
    res_df$stat
  } else if ("pvalue" %in% names(res_df) && any(is.finite(res_df$pvalue))) {
    sign(res_df$log2FoldChange) * (-log10(pmax(res_df$pvalue, 1e-300)))
  } else {
    res_df$log2FoldChange
  }
  names(ranks) <- rownames(res_df)
  ranks <- ranks[is.finite(ranks)]
  
  # Map to SYMBOL and collapse duplicates by mean
  id2sym <- gene_map$external_gene_name; names(id2sym) <- gene_map$gene_id
  sym <- id2sym[names(ranks)]
  keep <- !is.na(sym) & sym != ""
  agg <- tapply(ranks[keep], sym[keep], function(x) mean(x, na.rm = TRUE))
  ranks_sym <- sort(as.numeric(agg), decreasing = TRUE)
  names(ranks_sym) <- names(agg)
  
  # Write out for auditing
  write.csv(data.frame(symbol = names(ranks_sym), rank = ranks_sym),
            out_file, row.names = FALSE)
  invisible(ranks_sym)
}

## 2.4 One-liner to get Hallmark pathways (H)
get_hallmark_pathways <- function(){
  msig <- msigdbr(species = "Homo sapiens", collection = "H")
  split(msig$gene_symbol, msig$gs_name)
}

## 2.5 DE results -> symbols + significance categories
categorize_results <- function(res_obj, gene_map, padj_thr=0.05, lfc_thr=1.0) {
  df <- as.data.frame(res_obj)
  df$gene_id <- rownames(df)
  sym_map <- gene_map$external_gene_name; names(sym_map) <- gene_map$gene_id
  df$symbol <- sym_map[df$gene_id]
  df$label  <- ifelse(is.na(df$symbol) | df$symbol=="", df$gene_id, df$symbol)
  df$neglog10padj <- -log10(df$padj)
  df$Sig <- "NS"
  df$Sig[df$padj < padj_thr & df$log2FoldChange >=  lfc_thr] <- "Up"
  df$Sig[df$padj < padj_thr & df$log2FoldChange <= -lfc_thr] <- "Down"
  df$Sig <- factor(df$Sig, levels=c("Down","NS","Up"))
  df
}

## 2.6 Volcano plot
volcano_plot <- function(df, title, padj_thr, lfc_thr, label_top_n=15, label_genes=NULL, xlim_abs=4) {
  df_plot <- df %>% filter(!(abs(log2FoldChange) > xlim_abs & Sig == "NS"))
  lab_set <- character(0)
  if (!is.null(label_genes) && length(label_genes)) lab_set <- unique(c(lab_set, intersect(label_genes, df_plot$label)))
  sig_df <- df_plot[df_plot$Sig != "NS" & is.finite(df_plot$neglog10padj), ]
  if (nrow(sig_df) > 0 && label_top_n > 0) {
    top_df <- sig_df[order(sig_df$padj, -abs(sig_df$log2FoldChange)), ]
    lab_set <- unique(c(lab_set, head(top_df$label, label_top_n)))
  }
  df_plot$to_label <- df_plot$label %in% lab_set
  ggplot(df_plot, aes(x=log2FoldChange, y=neglog10padj, color=Sig)) +
    geom_point(alpha=0.65, size=1.6, na.rm=TRUE) +
    scale_color_manual(values=c(Down="#2b6cb0", NS="gray70", Up="#e53e3e")) +
    geom_hline(yintercept=-log10(padj_thr), linetype="dashed", linewidth=0.4) +
    geom_vline(xintercept=c(-lfc_thr, lfc_thr), linetype="dotted", linewidth=0.4) +
    coord_cartesian(xlim=c(-xlim_abs, xlim_abs)) +
    ggrepel::geom_text_repel(
      data=subset(df_plot, to_label),
      aes(label=label),
      max.overlaps=100, size=3, min.segment.length=0,
      box.padding=0.25, point.padding=0.15, seed=1
    ) +
    labs(title=title,
         subtitle=paste0("Red=Up, Blue=Down, Gray=NS | padj<", padj_thr,
                         ", |log2FC|>=", lfc_thr, " | x-range ±", xlim_abs),
         x="log2 fold-change", y="-log10(FDR)", color="") +
    theme_minimal(base_size=12) + theme(legend.position="top")
}

## 2.7 ORA with GSEA fallback (unchanged)
run_enrichment_with_fallback <- function(entrez_vec, prefix, universe_entrez,
                                         res_obj = NULL, gene_map = NULL,
                                         qcut = 0.25, top_show = 20) {
  if (length(entrez_vec) >= 5) {
    ego <- enrichGO(gene=entrez_vec, OrgDb=org.Hs.eg.db, ont="BP",
                    universe=universe_entrez, pAdjustMethod="BH",
                    qvalueCutoff=qcut, readable=TRUE)
    if (!is.null(ego) && nrow(ego) > 0) {
      ego_s <- tryCatch(simplify(ego, cutoff=0.5, by="p.adjust", select_fun=min), error=function(e) ego)
      write.csv(as.data.frame(ego),   paste0("GO_BP_", prefix, ".csv"), row.names=FALSE)
      write.csv(as.data.frame(ego_s), paste0("GO_BP_", prefix, "_SIMPLIFIED.csv"), row.names=FALSE)
      if (nrow(ego_s) > 0) {
        p_go <- dotplot(ego_s, showCategory=min(top_show, nrow(ego_s))) + ggtitle(paste0("GO BP: ", prefix))
        ggsave(paste0("GO_BP_", prefix, "_dotplot.png"), p_go, width=7, height=6, dpi=160)
        try({
          p_cnet <- cnetplot(ego_s, showCategory=min(8, nrow(ego_s)), foldChange=NULL)
          ggsave(paste0("GO_BP_", prefix, "_cnet.png"), p_cnet, width=8, height=6, dpi=160)
        }, silent=TRUE)
      }
    }
    ekegg <- enrichKEGG(gene=entrez_vec, organism="hsa",
                        universe=universe_entrez, pAdjustMethod="BH",
                        qvalueCutoff=qcut)
    if (!is.null(ekegg) && nrow(ekegg) > 0) {
      ekegg_read <- tryCatch(setReadable(ekegg, OrgDb=org.Hs.eg.db, keyType="ENTREZID"),
                             error=function(e) ekegg)
      write.csv(as.data.frame(ekegg_read), paste0("KEGG_", prefix, ".csv"), row.names=FALSE)
      p_kegg <- dotplot(ekegg_read, showCategory=min(top_show, nrow(ekegg_read))) + ggtitle(paste0("KEGG: ", prefix))
      ggsave(paste0("KEGG_", prefix, "_dotplot.png"), p_kegg, width=7, height=6, dpi=160)
      try({
        p_cnetk <- cnetplot(ekegg_read, showCategory=min(8, nrow(ekegg_read)), foldChange=NULL)
        ggsave(paste0("KEGG_", prefix, "_cnet.png"), p_cnetk, width=8, height=6, dpi=160)
      }, silent=TRUE)
    }
    invisible(list(method="ORA", n=length(entrez_vec)))
  } else {
    message(prefix, ": not enough genes (n<5); attempting GSEA fallback.")
    if (is.null(res_obj) || is.null(gene_map)) {
      message("  No res_obj/gene_map provided; skipping fallback GSEA.")
      return(invisible(list(method="SKIP", n=length(entrez_vec))))
    }
    fg <- gsea_from_res(res_obj, gene_map)
    out_csv <- paste0("FALLBACK_GSEA_", prefix, ".csv")
    write.csv(gsea_tidy(fg), out_csv, row.names=FALSE)
    message("  Wrote fallback GSEA: ", out_csv)
    invisible(list(method="GSEA_fallback", n=length(entrez_vec)))
  }
}

## 2.8 Read/compare enrichment + dashboard (unchanged)
.read_enrich <- function(path) {
  if (!file.exists(path)) return(NULL)
  df <- read.csv(path, stringsAsFactors=FALSE, check.names=FALSE)
  names(df) <- gsub("\\.", "_", names(df))
  if (!"Description" %in% names(df)) df$Description <- df[[1]]
  if ("p.adjust" %in% names(df)) names(df)[names(df)=="p.adjust"] <- "p_adjust"
  df
}
compare_two_enrich <- function(file_A, file_B, label_A, label_B, out_prefix, q_cut=0.25) {
  A <- .read_enrich(file_A); B <- .read_enrich(file_B)
  if (is.null(A) || is.null(B)) {
    message("Missing file: ", ifelse(is.null(A), file_A, ""), " ", ifelse(is.null(B), file_B, ""))
    return(invisible(NULL))
  }
  A_sig <- if ("p_adjust" %in% names(A)) subset(A, is.finite(p_adjust) & p_adjust <= q_cut) else A
  B_sig <- if ("p_adjust" %in% names(B)) subset(B, is.finite(p_adjust) & p_adjust <= q_cut) else B
  terms_A <- unique(A_sig$Description); terms_B <- unique(B_sig$Description)
  only_A <- setdiff(terms_A, terms_B); only_B <- setdiff(terms_B, terms_A); both <- intersect(terms_A, terms_B)
  presence_tbl <- tibble::tibble(
    Category = c(rep(paste0("Only_", label_A), length(only_A)),
                 rep(paste0("Only_", label_B), length(only_B)),
                 rep("Shared", length(both))),
    Term = c(only_A, only_B, both)
  )
  A_keep <- A[, intersect(c("Description","p_adjust","pvalue","GeneRatio","Count"), names(A)), drop=FALSE]
  B_keep <- B[, intersect(c("Description","p_adjust","pvalue","GeneRatio","Count"), names(B)), drop=FALSE]
  names(A_keep) <- paste0(names(A_keep), "_", label_A)
  names(B_keep) <- paste0(names(B_keep), "_", label_B)
  joined <- merge(A_keep, B_keep,
                  by.x=paste0("Description_", label_A),
                  by.y=paste0("Description_", label_B),
                  all=TRUE)
  names(joined)[1] <- "Term"
  if (paste0("p_adjust_", label_A) %in% names(joined)) {
    joined$neglog10q_A <- -log10(pmax(joined[[paste0("p_adjust_", label_A)]], 1e-300))
  } else joined$neglog10q_A <- NA_real_
  if (paste0("p_adjust_", label_B) %in% names(joined)) {
    joined$neglog10q_B <- -log10(pmax(joined[[paste0("p_adjust_", label_B)]], 1e-300))
  } else joined$neglog10q_B <- NA_real_
  joined$Delta_neglog10q <- joined$neglog10q_A - joined$neglog10q_B
  joined <- joined[order(-joined$Delta_neglog10q, joined$Term), ]
  write.csv(presence_tbl, paste0(out_prefix, "_presence.csv"), row.names=FALSE)
  write.csv(joined,      paste0(out_prefix, "_joined.csv"),   row.names=FALSE)
  message("Wrote: ", out_prefix, "_presence.csv and _joined.csv")
  invisible(list(presence=presence_tbl, joined=joined))
}
build_enrichment_dashboard <- function(
    go_up_join   = "COMPARE_GO_UP_LA_vs_LEE_STANDARD_joined.csv",
    go_down_join = "COMPARE_GO_DOWN_LA_vs_LEE_STANDARD_joined.csv",
    kg_up_join   = "COMPARE_KEGG_UP_LA_vs_LEE_STANDARD_joined.csv",
    kg_down_join = "COMPARE_KEGG_DOWN_LA_vs_LEE_STANDARD_joined.csv",
    out_path     = "ENRICHMENT_DASHBOARD_LA_vs_LEE_STANDARD.csv"
) {
  read_or_null <- function(p) if (file.exists(p)) read.csv(p, check.names=FALSE) else NULL
  d_go_up <- read_or_null(go_up_join); d_go_dn <- read_or_null(go_down_join)
  d_kg_up <- read_or_null(kg_up_join); d_kg_dn <- read_or_null(kg_down_join)
  if (all(sapply(list(d_go_up, d_go_dn, d_kg_up, d_kg_dn), is.null))) {
    stop("No joined comparison files found. Run compare_two_enrich() first.")
  }
  add_src <- function(df, src) { if (is.null(df)) return(NULL); df$Source <- src; df }
  d_go_up <- add_src(d_go_up, "GO_BP_UP"); d_go_dn <- add_src(d_go_dn, "GO_BP_DOWN")
  d_kg_up <- add_src(d_kg_up, "KEGG_UP");  d_kg_dn <- add_src(d_kg_dn, "KEGG_DOWN")
  library(dplyr)
  dash <- bind_rows(d_go_up, d_go_dn, d_kg_up, d_kg_dn) %>%
    mutate(
      neglog10q_A = ifelse(is.na(neglog10q_A) & !is.na(`p_adjust_LA_up`), -log10(pmax(`p_adjust_LA_up`, 1e-300)), neglog10q_A),
      neglog10q_B = ifelse(is.na(neglog10q_B) & !is.na(`p_adjust_LEE_up`), -log10(pmax(`p_adjust_LEE_up`,1e-300)), neglog10q_B),
      Delta_neglog10q = ifelse(is.na(Delta_neglog10q), neglog10q_A - neglog10q_B, Delta_neglog10q),
      Favours = case_when(
        is.finite(Delta_neglog10q) & Delta_neglog10q >  1 ~ "LA (strong)",
        is.finite(Delta_neglog10q) & Delta_neglog10q < -1 ~ "LEE (strong)",
        is.finite(Delta_neglog10q) & Delta_neglog10q >= 0 ~ "LA",
        is.finite(Delta_neglog10q) & Delta_neglog10q <  0 ~ "LEE",
        TRUE ~ "NA"
      )
    ) %>%
    arrange(desc(abs(Delta_neglog10q)), Term)
  write.csv(dash, out_path, row.names=FALSE)
  message("Wrote dashboard: ", out_path)
  dash
}

## 2.9 Resolve SYMBOL direction to avoid Up/Down double-counting
resolve_symbol_directions <- function(df, padj_thr=0.05, lfc_thr=1.0) {
  tmp <- df %>%
    dplyr::filter(!is.na(symbol) & symbol != "") %>%
    dplyr::mutate(
      Dir = dplyr::case_when(
        padj < padj_thr & log2FoldChange >=  lfc_thr ~ "Up",
        padj < padj_thr & log2FoldChange <= -lfc_thr ~ "Down",
        TRUE ~ "NS"
      )
    ) %>%
    dplyr::filter(Dir != "NS")
  if (nrow(tmp) == 0) return(tibble::tibble(symbol=character(0), Dir=character(0)))
  tmp %>%
    dplyr::group_by(symbol) %>%
    dplyr::summarise(hasUp=any(Dir=="Up"), hasDown=any(Dir=="Down"), .groups="drop") %>%
    dplyr::mutate(Dir = dplyr::case_when(
      hasUp & !hasDown ~ "Up",
      hasDown & !hasUp ~ "Down",
      hasUp & hasDown  ~ "Ambiguous",
      TRUE ~ "NS"
    )) %>%
    dplyr::select(symbol, Dir)
}
get_sig_symbols_resolved <- function(df, direction=c("Up","Down"),
                                     padj_thr=0.05, lfc_thr=1.0,
                                     policy=c("exclude_ambig","choose_stronger")) {
  direction <- match.arg(direction)
  policy    <- match.arg(policy)
  sym_dir <- resolve_symbol_directions(df, padj_thr, lfc_thr)
  if (policy == "exclude_ambig") {
    return(sym_dir %>% dplyr::filter(Dir==direction) %>% dplyr::pull(symbol) %>%
             unique() %>% stats::na.omit())
  }
  df2 <- df %>% dplyr::filter(!is.na(symbol) & symbol != "")
  med_lfc <- df2 %>%
    dplyr::group_by(symbol) %>%
    dplyr::summarise(
      medUp   = median(log2FoldChange[padj < padj_thr & log2FoldChange >=  lfc_thr], na.rm=TRUE),
      medDown = median(log2FoldChange[padj < padj_thr & log2FoldChange <= -lfc_thr], na.rm=TRUE),
      .groups="drop"
    )
  amb <- sym_dir %>% dplyr::filter(Dir=="Ambiguous") %>% dplyr::left_join(med_lfc, by="symbol")
  amb$chosen <- ifelse(abs(amb$medUp) >= abs(amb$medDown), "Up", "Down")
  keep <- sym_dir %>% dplyr::filter(Dir %in% c("Up","Down")) %>%
    dplyr::bind_rows(amb %>% dplyr::select(symbol, Dir=chosen))
  keep %>% dplyr::filter(Dir==direction) %>% dplyr::pull(symbol) %>%
    unique() %>% stats::na.omit()
}
sym2entrez <- function(symbols) {
  if (length(symbols) == 0) return(character(0))
  out <- clusterProfiler::bitr(unique(stats::na.omit(symbols)),
                               fromType="SYMBOL", toType="ENTREZID", OrgDb=org.Hs.eg.db)
  unique(stats::na.omit(out$ENTREZID))
}

# =========================
# [3] STEP 1 — LOAD & CONSTRUCT
# =========================
df <- readr::read_tsv(INPUT_FILE, guess_max=1e6, show_col_types=FALSE, quote="\"")
names(df) <- trimws(names(df))

sample_cols <- names(df)[grepl("^(DMSO|LEE|LA)_\\d+$", names(df))]
if (!length(sample_cols)) stop("No sample columns matched ^(DMSO|LEE|LA)_\\d+$")

gene_map <- df |>
  dplyr::select(gene_id, external_gene_name) |>
  dplyr::mutate(external_gene_name = dplyr::if_else(is.na(external_gene_name) |
                                                      external_gene_name=="" |
                                                      external_gene_name==".",
                                                    NA_character_, external_gene_name)) |>
  dplyr::distinct(gene_id, .keep_all=TRUE)

counts_mat <- df |> dplyr::select(dplyr::all_of(sample_cols)) |> as.data.frame()
counts_mat[] <- lapply(counts_mat, function(x) as.integer(round(as.numeric(x))))
stopifnot(nrow(counts_mat) == nrow(df))
rownames(counts_mat) <- df$gene_id
if (any(duplicated(rownames(counts_mat)))) {
  counts_mat <- rowsum(counts_mat, group=rownames(counts_mat), reorder=FALSE)
  gene_map   <- gene_map[!duplicated(gene_map$gene_id), ]
}

treatment <- dplyr::case_when(
  grepl("^DMSO_", sample_cols) ~ "DMSO",
  grepl("^LEE_" , sample_cols) ~ "LEE",
  grepl("^LA_"  , sample_cols) ~ "LA",
  TRUE ~ "Other"
)
coldata <- data.frame(
  sample    = sample_cols,
  treatment = factor(treatment, levels=c("DMSO","LEE","LA")),
  batch     = factor("B1")
)
rownames(coldata) <- coldata$sample
counts_mat <- counts_mat[, rownames(coldata)]

cat("Step 1 OK — counts_mat:", nrow(counts_mat), "genes x", ncol(counts_mat), "samples\n")
print(utils::head(coldata))

.sym_map <- gene_map$external_gene_name; names(.sym_map) <- gene_map$gene_id
all_syms <- unique(stats::na.omit(.sym_map[rownames(counts_mat)]))
universe_entrez <- unique(stats::na.omit(clusterProfiler::bitr(
  all_syms, fromType="SYMBOL", toType="ENTREZID", OrgDb=org.Hs.eg.db
)$ENTREZID))

# =========================
# [4] STEP 2 — STANDARD DE + GSEA + VOLCANO (GSEA updated)
# =========================
dds <- DESeqDataSetFromMatrix(countData=counts_mat, colData=coldata, design=~ treatment)
dds <- dds[rowSums(counts(dds) >= MIN_COUNT) >= MIN_SAMPLES, ]
dds <- DESeq(dds)
colData(dds)$treatment <- factor(colData(dds)$treatment, levels=c("DMSO","LEE","LA"))

res_LEE_vs_DMSO <- shrink_safe(dds, contrast=c("treatment","LEE","DMSO"))
res_LA_vs_DMSO  <- shrink_safe(dds, contrast=c("treatment","LA","DMSO"))
res_LA_vs_LEE   <- shrink_safe(dds, contrast=c("treatment","LA","LEE"))

# PCA
vsd <- vst(dds, blind=FALSE)
pdf("PCA_vst_STANDARD.pdf", width=6, height=5); print(plotPCA(vsd, intgroup=c("treatment"))); dev.off()

# ---- GSEA with saved ranks (Hallmarks) ----
set.seed(1)
hallmark_pw <- get_hallmark_pathways()

# LEE vs DMSO
r_LEE  <- save_ranks(res_LEE_vs_DMSO, gene_map, "RANKS_LEE_vs_DMSO.csv")
fg_LEE <- fgseaMultilevel(pathways = hallmark_pw, stats = r_LEE, minSize = 15, maxSize = 500)
write.csv(gsea_tidy(fg_LEE), "GSEA_LEE_vs_DMSO_STANDARD.csv", row.names = FALSE)

# LA vs DMSO
r_LA  <- save_ranks(res_LA_vs_DMSO,  gene_map, "RANKS_LA_vs_DMSO.csv")
fg_LA <- fgseaMultilevel(pathways = hallmark_pw, stats = r_LA, minSize = 15, maxSize = 500)
write.csv(gsea_tidy(fg_LA), "GSEA_LA_vs_DMSO_STANDARD.csv", row.names = FALSE)

# LA vs LEE (standard)
r_LAP   <- save_ranks(res_LA_vs_LEE,   gene_map, "RANKS_LA_vs_LEE.csv")
fg_LA_P <- fgseaMultilevel(pathways = hallmark_pw, stats = r_LAP, minSize = 15, maxSize = 500)
write.csv(gsea_tidy(fg_LA_P), "GSEA_LA_vs_LEE_STANDARD.csv", row.names = FALSE)

# Keep DE CSVs
write.csv(as.data.frame(res_LEE_vs_DMSO), "DE_LEE_vs_DMSO_STANDARD.csv")
write.csv(as.data.frame(res_LA_vs_DMSO),  "DE_LA_vs_DMSO_STANDARD.csv")
write.csv(as.data.frame(res_LA_vs_LEE),   "DE_LA_vs_LEE_STANDARD.csv")

# Volcanoes
df_LEE  <- categorize_results(res_LEE_vs_DMSO, gene_map, PADJ_THRESH, LFC_THRESH)
df_LA   <- categorize_results(res_LA_vs_DMSO,  gene_map, PADJ_THRESH, LFC_THRESH)
df_LA_P <- categorize_results(res_LA_vs_LEE,   gene_map, PADJ_THRESH, LFC_THRESH)

p1 <- volcano_plot(df_LEE,  "LEE vs DMSO", PADJ_THRESH, LFC_THRESH, 15, GENES_HILITE, xlim_abs=VOLC_XLIM)
p2 <- volcano_plot(df_LA,   "LA vs DMSO",  PADJ_THRESH, LFC_THRESH, 15, GENES_HILITE, xlim_abs=VOLC_XLIM)
p3 <- volcano_plot(df_LA_P, "LA vs LEE",   PADJ_THRESH, LFC_THRESH, 15, GENES_HILITE, xlim_abs=VOLC_XLIM)
ggsave("Volcano_LEE_vs_DMSO.png", p1, width=7, height=5.5, dpi=160)
ggsave("Volcano_LA_vs_DMSO.png",  p2, width=7, height=5.5, dpi=160)
ggsave("Volcano_LA_vs_LEE.png",   p3, width=7, height=5.5, dpi=160)
write.csv(df_LEE[, c("gene_id","symbol","log2FoldChange","padj","Sig")], "VolcanoCalls_LEE_vs_DMSO.csv", row.names=FALSE)
write.csv(df_LA[,  c("gene_id","symbol","log2FoldChange","padj","Sig")], "VolcanoCalls_LA_vs_DMSO.csv",  row.names=FALSE)
write.csv(df_LA_P[,c("gene_id","symbol","log2FoldChange","padj","Sig")], "VolcanoCalls_LA_vs_LEE.csv",   row.names=FALSE)
cat("Step 2 OK — standard DE/GSEA/volcano done.\n")

# =========================
# [5] STEP 2 ADD-ON — GO/KEGG (STANDARD; with RESOLVED Up/Down)
# =========================
LEE_up   <- get_sig_symbols_resolved(df_LEE, "Up",   PADJ_THRESH, LFC_THRESH, policy="exclude_ambig")
LEE_dn   <- get_sig_symbols_resolved(df_LEE, "Down", PADJ_THRESH, LFC_THRESH, policy="exclude_ambig")
LA_up    <- get_sig_symbols_resolved(df_LA,  "Up",   PADJ_THRESH, LFC_THRESH, policy="exclude_ambig")
LA_dn    <- get_sig_symbols_resolved(df_LA,  "Down", PADJ_THRESH, LFC_THRESH, policy="exclude_ambig")
LAvP_up  <- get_sig_symbols_resolved(df_LA_P,"Up",   PADJ_THRESH, LFC_THRESH, policy="exclude_ambig")
LAvP_dn  <- get_sig_symbols_resolved(df_LA_P,"Down", PADJ_THRESH, LFC_THRESH, policy="exclude_ambig")

LEE_up_e  <- sym2entrez(LEE_up);   LEE_dn_e  <- sym2entrez(LEE_dn)
LA_up_e   <- sym2entrez(LA_up);    LA_dn_e   <- sym2entrez(LA_dn)
LAvP_up_e <- sym2entrez(LAvP_up);  LAvP_dn_e <- sym2entrez(LAvP_dn)

run_enrichment_with_fallback(LEE_up_e,  "UP_LEE_vs_DMSO_STANDARD",   universe_entrez, res_obj=res_LEE_vs_DMSO, gene_map=gene_map)
run_enrichment_with_fallback(LEE_dn_e,  "DOWN_LEE_vs_DMSO_STANDARD", universe_entrez, res_obj=res_LEE_vs_DMSO, gene_map=gene_map)
run_enrichment_with_fallback(LA_up_e,   "UP_LA_vs_DMSO_STANDARD",    universe_entrez, res_obj=res_LA_vs_DMSO,  gene_map=gene_map)
run_enrichment_with_fallback(LA_dn_e,   "DOWN_LA_vs_DMSO_STANDARD",  universe_entrez, res_obj=res_LA_vs_DMSO,  gene_map=gene_map)
run_enrichment_with_fallback(LAvP_up_e, "UP_LA_vs_LEE_STANDARD",     universe_entrez, res_obj=res_LA_vs_LEE,   gene_map=gene_map)
run_enrichment_with_fallback(LAvP_dn_e, "DOWN_LA_vs_LEE_STANDARD",   universe_entrez, res_obj=res_LA_vs_LEE,   gene_map=gene_map)
cat("Step 2 add-on OK — GO/KEGG for standard contrasts written.\n")

# =========================
# [6] STEP 3 — IC50/EQUIPOTENT (LA vs LEE, auto full-rank)
# =========================
col_ic50 <- as.data.frame(coldata); col_ic50$.rn <- rownames(col_ic50)
col_ic50 <- col_ic50 %>%
  dplyr::transmute(sample=.rn, treatment=as.character(treatment)) %>%
  dplyr::filter(treatment %in% c("LEE","LA")) %>%
  dplyr::mutate(
    dose_uM = dplyr::case_when(grepl("^LEE", sample) ~ DOSE_LEE,
                               grepl("^LA" , sample) ~ DOSE_LA, TRUE ~ NA_real_),
    IC50_uM = dplyr::case_when(treatment=="LEE" ~ IC50_LEE,
                               treatment=="LA"  ~ IC50_LA,  TRUE ~ NA_real_),
    rel_exposure  = dose_uM / IC50_uM,
    logE          = log10(rel_exposure + 1e-6),
    logE_centered = logE - log10(TARGET_MULTIC50)
  )
sel <- col_ic50$sample; stopifnot(all(sel %in% colnames(counts_mat)))
counts_eq <- counts_mat[, sel, drop=FALSE]

coldata_ic50 <- col_ic50
rownames(coldata_ic50) <- coldata_ic50$sample; coldata_ic50$sample <- NULL
coldata_ic50$treatment <- factor(coldata_ic50$treatment, levels=c("LEE","LA"))
coldata_ic50 <- droplevels(coldata_ic50)

sd_overall <- sd(coldata_ic50$logE_centered, na.rm=TRUE)
sd_lee <- sd(coldata_ic50$logE_centered[coldata_ic50$treatment=="LEE"], na.rm=TRUE)
sd_la  <- sd(coldata_ic50$logE_centered[coldata_ic50$treatment=="LA"],  na.rm=TRUE)
eps <- 1e-10
if (sd_lee < eps && sd_la < eps) {
  design_formula <- ~ treatment; model_case <- "A: ~ treatment (equipotent head-to-head)"
} else if ((sd_lee < eps && sd_la >= eps) || (sd_lee >= eps && sd_la < eps)) {
  design_formula <- ~ treatment + logE_centered; model_case <- "B: ~ treatment + logE_centered (common slope)"
} else {
  design_formula <- ~ treatment + logE_centered + treatment:logE_centered
  model_case <- "C: ~ treatment + logE_centered + treatment:logE_centered (interaction)"
}
message("Equipotent model: ", model_case)

dds_ic50 <- DESeqDataSetFromMatrix(countData=counts_eq, colData=coldata_ic50, design=design_formula)
dds_ic50 <- dds_ic50[rowSums(counts(dds_ic50) >= MIN_COUNT) >= MIN_SAMPLES, ]
dds_ic50 <- DESeq(dds_ic50)

if (identical(as.formula(design_formula), ~ treatment)) {
  res_eq  <- shrink_safe(dds_ic50, contrast=c("treatment","LA","LEE")); res_int <- NULL
} else if (identical(as.formula(design_formula), ~ treatment + logE_centered)) {
  res_eq  <- shrink_safe(dds_ic50, coef="treatment_LA_vs_LEE"); res_int <- NULL
} else {
  res_eq  <- shrink_safe(dds_ic50, coef="treatment_LA_vs_LEE")
  res_int <- results(dds_ic50, name="treatmentLA.logE_centered")
}

# ---- Equipotent GSEA with saved ranks ----
set.seed(1)
hallmark_pw <- get_hallmark_pathways()

r_EQ  <- save_ranks(res_eq, gene_map, "RANKS_LA_vs_LEE_EQUIPOTENT.csv")
fg_eq <- fgseaMultilevel(pathways = hallmark_pw, stats = r_EQ, minSize = 15, maxSize = 500)
write.csv(gsea_tidy(fg_eq), "GSEA_LA_vs_LEE_EQUIPOTENT.csv", row.names = FALSE)

if (!is.null(res_int)) {
  r_INT  <- save_ranks(res_int, gene_map, "RANKS_LA_vs_LEE_INTERACTION.csv")
  fg_int <- fgseaMultilevel(pathways = hallmark_pw, stats = r_INT, minSize = 15, maxSize = 500)
  write.csv(as.data.frame(res_int), "DE_LA_vs_LEE_INTERACTION.csv")
  write.csv(gsea_tidy(fg_int),      "GSEA_LA_vs_LEE_INTERACTION.csv", row.names = FALSE)
}

# Volcano + calls (equipotent)
df_eq <- categorize_results(res_eq, gene_map, PADJ_THRESH, LFC_THRESH)
p_eq  <- volcano_plot(df_eq, paste0("LA vs LEE @ ", TARGET_MULTIC50, "×IC50 (equipotent) — ", model_case),
                      PADJ_THRESH, LFC_THRESH, 15, GENES_HILITE, xlim_abs=VOLC_XLIM)
ggsave(paste0("Volcano_LA_vs_LEE_EQUIPOTENT_", TARGET_MULTIC50, "xIC50.png"),
       p_eq, width=7, height=5.5, dpi=160)
write.csv(df_eq[, c("gene_id","symbol","log2FoldChange","padj","Sig")],
          paste0("VolcanoCalls_LA_vs_LEE_EQUIPOTENT_", TARGET_MULTIC50, "xIC50.csv"), row.names=FALSE)
cat("Step 3 OK — equipotent DE/GSEA/volcano done.\n")

# =========================
# [7] STEP 3 ADD-ON — GO/KEGG (EQUIPOTENT LA vs LEE) with RESOLVED sets
# =========================
EQ_up   <- get_sig_symbols_resolved(df_eq, "Up",   PADJ_THRESH, LFC_THRESH, policy="exclude_ambig")
EQ_dn   <- get_sig_symbols_resolved(df_eq, "Down", PADJ_THRESH, LFC_THRESH, policy="exclude_ambig")
EQ_up_e <- sym2entrez(EQ_up);  EQ_dn_e <- sym2entrez(EQ_dn)
run_enrichment_with_fallback(EQ_up_e, "UP_LA_vs_LEE_EQUIPOTENT",
                             universe_entrez, res_obj=res_eq, gene_map=gene_map)
run_enrichment_with_fallback(EQ_dn_e, "DOWN_LA_vs_LEE_EQUIPOTENT",
                             universe_entrez, res_obj=res_eq, gene_map=gene_map)
cat("Step 3 add-on OK — GO/KEGG for equipotent written.\n")

# =========================
# [8] FLEXIBLE GO/KEGG: generate & compare any contrasts (uses RESOLVED sets)
# =========================
.contrast_registry <- list(
  "LEE_vs_DMSO" = list(df=quote(df_LEE),  res=quote(res_LEE_vs_DMSO), tag="STANDARD"),
  "LA_vs_DMSO"  = list(df=quote(df_LA),   res=quote(res_LA_vs_DMSO),  tag="STANDARD"),
  "LA_vs_LEE"   = list(df=quote(df_LA_P), res=quote(res_LA_vs_LEE),   tag="STANDARD"),
  "LA_vs_LEE_EQUIPOTENT" = list(df=quote(df_eq), res=quote(res_eq),   tag="EQUIPOTENT")
)
.get_contrast <- function(name) {
  if (!name %in% names(.contrast_registry)) {
    stop("Unknown contrast '", name, "'. Use one of: ", paste(names(.contrast_registry), collapse=", "))
  }
  reg <- .contrast_registry[[name]]
  list(df=eval(reg$df), res=eval(reg$res), tag=reg$tag)
}
ensure_enrichment_for <- function(contrast_name, qcut=0.25, top_show=20,
                                  policy=c("exclude_ambig","choose_stronger")) {
  policy <- match.arg(policy)
  cx <- .get_contrast(contrast_name)
  df <- cx$df; res <- cx$res; tag <- cx$tag
  up_syms   <- get_sig_symbols_resolved(df, "Up",   PADJ_THRESH, LFC_THRESH, policy=policy)
  down_syms <- get_sig_symbols_resolved(df, "Down", PADJ_THRESH, LFC_THRESH, policy=policy)
  up_e      <- sym2entrez(up_syms); down_e <- sym2entrez(down_syms)
  pref_up   <- paste0("UP_",   contrast_name, "_", tag)
  pref_down <- paste0("DOWN_", contrast_name, "_", tag)
  run_enrichment_with_fallback(up_e,   pref_up,   universe_entrez, res_obj=res, gene_map=gene_map, qcut=qcut, top_show=top_show)
  run_enrichment_with_fallback(down_e, pref_down, universe_entrez, res_obj=res, gene_map=gene_map, qcut=qcut, top_show=top_show)
  invisible(NULL)
}
ensure_enrichment_many <- function(contrast_names, ...) lapply(contrast_names, ensure_enrichment_for, ...)

compare_enrichment_flexible <- function(category=c("GO","KEGG"), direction=c("Up","Down"),
                                        A, B, out_prefix=NULL, q_cut=0.25) {
  category  <- match.arg(category); direction <- match.arg(direction)
  a <- .get_contrast(A); b <- .get_contrast(B)
  ensure_enrichment_for(A); ensure_enrichment_for(B)
  left  <- if (category=="GO") paste0("GO_BP_", toupper(direction), "_", A, "_", a$tag, ".csv")
  else                 paste0("KEGG_",  toupper(direction), "_", A, "_", a$tag, ".csv")
  right <- if (category=="GO") paste0("GO_BP_", toupper(direction), "_", B, "_", b$tag, ".csv")
  else                 paste0("KEGG_",  toupper(direction), "_", B, "_", b$tag, ".csv")
  if (is.null(out_prefix)) out_prefix <- paste0("COMPARE_", category, "_", toupper(direction), "_", A, "_vs_", B)
  compare_two_enrich(left, right, A, B, out_prefix, q_cut=q_cut)
}

# Combined (unsigned) ORA for any contrast (uses all significant symbols)
ensure_enrichment_combined <- function(contrast_name, qcut=0.25, minGSSize=3, maxGSSize=500,
                                       top_show=20, use_universe=TRUE) {
  cx  <- .get_contrast(contrast_name)
  df  <- cx$df; tag <- cx$tag
  uni <- if (use_universe) universe_entrez else NULL
  comb_syms <- unique(stats::na.omit(df$symbol[df$Sig != "NS"]))
  eg        <- sym2entrez(comb_syms)
  message("[COMBINED] ", contrast_name, " — n SYMBOLs=", length(comb_syms),
          ", n ENTREZ=", length(eg), ", universe=", ifelse(is.null(uni),"none", length(uni)))
  if (length(eg) < 5) {
    message("[COMBINED] Not enough genes (n<5); writing empty files.")
    write.csv(data.frame(), paste0("GO_BP_COMBINED_", contrast_name, "_", tag, ".csv"), row.names=FALSE)
    write.csv(data.frame(), paste0("KEGG_COMBINED_",  contrast_name, "_", tag, ".csv"), row.names=FALSE)
    return(invisible(NULL))
  }
  fc_map <- df$log2FoldChange; names(fc_map) <- df$symbol
  fc_map <- fc_map[!is.na(names(fc_map)) & names(fc_map) != ""]
  pref <- paste0("COMBINED_", contrast_name, "_", tag)
  
  # GO BP (external filtering)
  ego_raw <- tryCatch(
    enrichGO(gene = eg, OrgDb = org.Hs.eg.db, keyType = "ENTREZID", ont = "BP",
             universe = uni, pAdjustMethod = "BH",
             pvalueCutoff = 1, qvalueCutoff = 1,
             minGSSize = minGSSize, maxGSSize = maxGSSize, readable = TRUE),
    error = function(e){ message("enrichGO(COMBINED) error: ", e$message); NULL }
  )
  if (!is.null(ego_raw) && nrow(as.data.frame(ego_raw)) > 0) {
    ego_df <- as.data.frame(ego_raw)
    ego_keep <- subset(ego_df, is.finite(p.adjust) & p.adjust <= qcut)
    write.csv(ego_keep, paste0("GO_BP_", pref, ".csv"), row.names=FALSE)
    if (nrow(ego_keep) > 0) {
      ego_keep_obj <- tryCatch(simplify(ego_raw[ego_raw@result$ID %in% ego_keep$ID, ],
                                        cutoff=0.5, by="p.adjust", select_fun=min),
                               error=function(e) ego_raw[ego_raw@result$ID %in% ego_keep$ID, ])
      try({
        p_cnet <- cnetplot(ego_keep_obj, showCategory=min(top_show, nrow(ego_keep)), foldChange=fc_map)
        ggsave(paste0("GO_BP_", pref, "_cnet.png"), p_cnet, width=8, height=6, dpi=160)
        p_emap <- emapplot(ego_keep_obj, showCategory=min(top_show, nrow(ego_keep)))
        ggsave(paste0("GO_BP_", pref, "_emap.png"), p_emap, width=8, height=6, dpi=160)
      }, silent=TRUE)
    }
  } else {
    write.csv(data.frame(), paste0("GO_BP_", pref, ".csv"), row.names=FALSE)
  }
  
  # KEGG (external filtering)
  ekegg_raw <- tryCatch(
    enrichKEGG(gene = eg, organism = "hsa",
               pAdjustMethod = "BH",
               pvalueCutoff = 1,
               minGSSize = minGSSize, maxGSSize = maxGSSize),
    error = function(e){ message("enrichKEKK(COMBINED) error: ", e$message); NULL }
  )
  if (!is.null(ekegg_raw) && nrow(as.data.frame(ekegg_raw)) > 0) {
    ekegg_read <- tryCatch(setReadable(ekegg_raw, OrgDb = org.Hs.eg.db, keyType = "ENTREZID"),
                           error=function(e) ekegg_raw)
    ek_df <- as.data.frame(ekegg_read)
    if (!"p.adjust" %in% names(ek_df) && "p.adjust" %in% names(as.data.frame(ekegg_raw))) {
      ek_df$p.adjust <- as.data.frame(ekegg_raw)$p.adjust
    }
    ek_keep <- subset(ek_df, is.finite(p.adjust) & p.adjust <= qcut)
    write.csv(ek_keep, paste0("KEGG_", pref, ".csv"), row.names=FALSE)
    if (nrow(ek_keep) > 0) {
      keep_ids <- ek_keep$ID
      ek_sub <- ekegg_read; ek_sub@result <- ek_sub@result[ek_sub@result$ID %in% keep_ids, , drop=FALSE]
      try({
        p_cnetk <- cnetplot(ek_sub, showCategory=min(top_show, nrow(ek_keep)), foldChange=fc_map)
        ggsave(paste0("KEGG_", pref, "_cnet.png"), p_cnetk, width=8, height=6, dpi=160)
        p_emapk <- emapplot(ek_sub, showCategory=min(top_show, nrow(ek_keep)))
        ggsave(paste0("KEGG_", pref, "_emap.png"), p_emapk, width=8, height=6, dpi=160)
      }, silent=TRUE)
    }
  } else {
    write.csv(data.frame(), paste0("KEGG_", pref, ".csv"), row.names=FALSE)
  }
  invisible(TRUE)
}

# =========================
# [9] COMPARISONS — LA vs DMSO vs LEE vs DMSO (GO/KEGG; UP/DOWN)
# =========================
cmp_go_up <- compare_two_enrich("GO_BP_UP_LA_vs_DMSO_STANDARD.csv",
                                "GO_BP_UP_LEE_vs_DMSO_STANDARD.csv",
                                "LA_up","LEE_up","COMPARE_GO_UP_LA_vs_LEE_STANDARD", q_cut=0.25)
cmp_go_dn <- compare_two_enrich("GO_BP_DOWN_LA_vs_DMSO_STANDARD.csv",
                                "GO_BP_DOWN_LEE_vs_DMSO_STANDARD.csv",
                                "LA_down","LEE_down","COMPARE_GO_DOWN_LA_vs_LEE_STANDARD", q_cut=0.25)
cmp_kegg_up <- compare_two_enrich("KEGG_UP_LA_vs_DMSO_STANDARD.csv",
                                  "KEGG_UP_LEE_vs_DMSO_STANDARD.csv",
                                  "LA_up","LEE_up","COMPARE_KEGG_UP_LA_vs_LEE_STANDARD", q_cut=0.25)
cmp_kegg_dn <- compare_two_enrich("KEGG_DOWN_LA_vs_DMSO_STANDARD.csv",
                                  "KEGG_DOWN_LEE_vs_DMSO_STANDARD.csv",
                                  "LA_down","LEE_down","COMPARE_KEGG_DOWN_LA_vs_LEE_STANDARD", q_cut=0.25)
cat("Comparisons OK — presence and joined tables written.\n")

# ---------- OPTIONAL: combined (Up ∪ Down) enrichment previews ----------
ensure_enrichment_combined("LEE_vs_DMSO", qcut = 0.5, minGSSize = 3, use_universe = FALSE)
ensure_enrichment_combined("LEE_vs_DMSO", qcut = 0.25, minGSSize = 5, use_universe = TRUE)

