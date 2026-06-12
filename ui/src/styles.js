export const dynamic = {
  barFill: (pct, color) => ({
    width: `${pct}%`,
    height: "100%",
    background: color,
    transition: "width 0.4s",
  }),
};
