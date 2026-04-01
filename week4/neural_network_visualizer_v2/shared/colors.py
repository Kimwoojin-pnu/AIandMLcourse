# shared/colors.py  — Phosphor Control Room palette
# Inspired by amber/green phosphor CRT displays, elevated with modern neon-noir

COLORS = {
    "bg":           "#080808",   # near-pitch black
    "panel":        "#0D0D10",   # slightly lifted charcoal
    "card":         "#111116",   # card surface
    "border":       "#1C1C28",   # dark purple-tinted border
    "border_light": "#2E2E45",   # lighter border for inputs
    "accent":       "#F5A623",   # warm amber — primary phosphor glow
    "success":      "#00E676",   # electric green — training progress
    "danger":       "#FF3366",   # vivid pink-red — loss/errors
    "info":         "#40C4FF",   # light cyan-blue — val loss
    "highlight":    "#F5A623",   # amber highlight (same as accent)
    "text":         "#E8E8E0",   # warm off-white
    "text_dim":     "#8888A0",   # muted purple-grey
    "text_muted":   "#363648",   # very dim, for grid/chrome
    # Semi-transparent glow colors for painter
    "amber_glow":   "#F5A62360",
    "green_glow":   "#00E67640",
    "danger_glow":  "#FF336640",
}

# Stage colors for Lab3 overfitting
STAGE_COLORS = {
    "Underfit": "#F5A623",   # amber
    "Good Fit": "#00E676",   # green
    "Overfit":  "#FF3366",   # red
}
