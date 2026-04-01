# shared/colors.py
COLORS = {
    "bg":           "#1a1b26",
    "panel":        "#16213e",
    "card":         "#1e2030",
    "border":       "#2a2d3e",
    "border_light": "#3b4261",
    "accent":       "#7aa2f7",
    "success":      "#9ece6a",
    "danger":       "#f7768e",
    "highlight":    "#e0af68",
    "text":         "#c0caf5",
    "text_dim":     "#a9b1d6",
    "text_muted":   "#565f89",
}

CAT_SVG = b"""<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">
  <ellipse cx="18" cy="26" rx="9" ry="7" fill="#a9b1d6"/>
  <circle cx="18" cy="16" r="8" fill="#a9b1d6"/>
  <polygon points="10,11 8,4 15,9" fill="#a9b1d6"/>
  <polygon points="11,10 9,5 14,9" fill="#f7768e" opacity="0.7"/>
  <polygon points="26,11 28,4 21,9" fill="#a9b1d6"/>
  <polygon points="25,10 27,5 22,9" fill="#f7768e" opacity="0.7"/>
  <ellipse cx="15" cy="16" rx="1.8" ry="2.2" fill="#1a1b26"/>
  <circle cx="15.5" cy="15.3" r="0.6" fill="#fff"/>
  <ellipse cx="21" cy="16" rx="1.8" ry="2.2" fill="#1a1b26"/>
  <circle cx="21.5" cy="15.3" r="0.6" fill="#fff"/>
  <polygon points="18,19 16.8,20.5 19.2,20.5" fill="#f7768e"/>
  <path d="M16.8,20.5 Q18,22 19.2,20.5" stroke="#c0caf5" stroke-width="0.6" fill="none"/>
  <line x1="10" y1="19.5" x2="16" y2="20" stroke="#c0caf5" stroke-width="0.5" opacity="0.7"/>
  <line x1="10" y1="21" x2="16" y2="20.8" stroke="#c0caf5" stroke-width="0.5" opacity="0.7"/>
  <line x1="26" y1="19.5" x2="20" y2="20" stroke="#c0caf5" stroke-width="0.5" opacity="0.7"/>
  <line x1="26" y1="21" x2="20" y2="20.8" stroke="#c0caf5" stroke-width="0.5" opacity="0.7"/>
  <path d="M27,28 Q33,24 31,20 Q30,17 28,19" stroke="#a9b1d6" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <ellipse cx="14" cy="32" rx="3" ry="1.8" fill="#a9b1d6"/>
  <ellipse cx="22" cy="32" rx="3" ry="1.8" fill="#a9b1d6"/>
</svg>"""
