# =====================================================================
# Flipkart Sales Dashboard (DARK THEME) - Power BI Python visual
# Paste this whole script into a Power BI "Python visual" script editor.
# Power BI supplies the data as a pandas DataFrame named `dataset`.
#
# Fields to drag into the visual's Values well (same 12 as before,
# all numeric columns set to "Don't summarize", use the Σ columns):
#   product_id, category, brand, seller, seller_city, price,
#   discount_percent, final_price, units_sold, rating, delivery_days,
#   listing_date
# =====================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap, to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.ticker import FuncFormatter, MaxNLocator

df = dataset.copy()  # noqa: F821  (`dataset` is provided by Power BI)

# ---------- 1. Prepare data ----------
df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce")
df["revenue"] = df["final_price"] * df["units_sold"]
df["discount_given"] = (df["price"] - df["final_price"]) * df["units_sold"]

# ---------- 2. Theme ----------
BG, CARD, CARD_EDGE = "#0A0F1F", "#121A33", "#25325F"
TEXT, MUTED, GRID = "#E5E7EB", "#8B97B5", "#1E2A4D"
PURPLE, INDIGO, BLUE, CYAN = "#7C3AED", "#6366F1", "#3B82F6", "#22D3EE"
GREEN, AMBER, PINK = "#34D399", "#FBBF24", "#F472B6"
PALETTE = ["#7C3AED", "#3B82F6", "#22D3EE", "#34D399",
           "#FBBF24", "#F472B6", "#A78BFA", "#60A5FA"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": TEXT,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
})


def money(v):
    a = abs(v)
    if a >= 1e12:
        return f"₹{v/1e12:.2f}T"
    if a >= 1e9:
        return f"₹{v/1e9:.1f}B"
    if a >= 1e6:
        return f"₹{v/1e6:.1f}M"
    if a >= 1e3:
        return f"₹{v/1e3:.1f}K"
    return f"₹{v:,.0f}"


def short(v):
    a = abs(v)
    if a >= 1e9:
        return f"{v/1e9:.1f}B"
    if a >= 1e6:
        return f"{v/1e6:.1f}M"
    if a >= 1e3:
        return f"{v/1e3:.1f}K"
    return f"{v:,.0f}"


money_axis = FuncFormatter(lambda v, _: money(v))

# ---------- 3. Canvas (1 unit = 1 inch, so rounded corners stay round) ----------
W, H = 20, 11.25
fig = plt.figure(figsize=(W, H), facecolor=BG)
bg = fig.add_axes([0, 0, 1, 1])
bg.set_xlim(0, W)
bg.set_ylim(0, H)
bg.axis("off")


def add_ax(x, y, w, h):
    ax = fig.add_axes([x / W, y / H, w / W, h / H])
    ax.set_facecolor("none")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0, labelsize=9)
    return ax


def card(x, y, w, h, title, subtitle=None):
    bg.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0,rounding_size=0.22",
        facecolor=CARD, edgecolor=CARD_EDGE, linewidth=1, zorder=1))
    bg.text(x + 0.32, y + h - 0.40, title, fontsize=14, fontweight="bold",
            color=TEXT, va="center", zorder=3)
    if subtitle:
        bg.text(x + 0.32, y + h - 0.72, subtitle, fontsize=9.5,
                color=MUTED, va="center", zorder=3)


def gradient_tile(x, y, w, h, c1, c2):
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0,rounding_size=0.2",
        facecolor="none", edgecolor="none", zorder=2)
    bg.add_patch(patch)
    xs = np.linspace(0, 1, 300)[None, :]
    ys = np.linspace(0, 1, 80)[:, None]
    grad = 0.75 * xs + 0.25 * (1 - ys)
    cmap = LinearSegmentedColormap.from_list("g", [c1, c2])
    im = bg.imshow(grad, extent=[x, x + w, y, y + h], cmap=cmap,
                   aspect="auto", origin="lower", zorder=2)
    im.set_clip_path(patch)
    # soft glossy circle in the corner
    gloss = Circle((x + w - 0.25, y + h - 0.1), 0.95, color="white",
                   alpha=0.09, zorder=2.5)
    bg.add_patch(gloss)
    gloss.set_clip_path(patch)


# ---------- 4. Header ----------
bg.text(0.5, 10.72, "Flipkart Sales Dashboard", fontsize=27,
        fontweight="bold", color="white", va="center")
bg.text(0.52, 10.30, "Product catalogue performance  |  estimated revenue = final price × units sold",
        fontsize=10.5, color=MUTED, va="center")

d_min, d_max = df["listing_date"].min(), df["listing_date"].max()
span = f"{d_min.year} – {d_max.year}" if pd.notna(d_min) else "n/a"
chips = [f"{df['product_id'].nunique():,} listings", f"Listed {span}",
         f"{df['category'].nunique()} categories"]
cx = 19.5
for label in reversed(chips):
    t = bg.text(cx, 10.62, label, fontsize=10.5, color=TEXT, ha="right", va="center",
                bbox=dict(boxstyle="round,pad=0.5,rounding_size=0.9",
                          fc="#17213F", ec=CARD_EDGE, lw=1))
    cx -= 0.078 * len(label) + 0.85

# ---------- 5. KPI tiles (2 rows x 4, like the reference) ----------
kpis = [
    ("Total Revenue", money(df["revenue"].sum())),
    ("Units Sold", short(df["units_sold"].sum())),
    ("Total Products", f"{df['product_id'].nunique():,}"),
    ("Avg Rating", f"{df['rating'].mean():.2f} / 5"),
    ("Avg Price", money(df["final_price"].mean())),
    ("Avg Discount", f"{df['discount_percent'].mean():.1f}%"),
    ("Discount Given", money(df["discount_given"].sum())),
    ("Avg Delivery", f"{df['delivery_days'].mean():.1f} days"),
]
tile_colors = [("#6D28D9", "#4F46E5"), ("#1E40AF", "#0B66C3"),
               ("#0369A1", "#06B6D4"), ("#047857", "#34D399")]
tw, th, tg = 2.7, 1.2, 0.2
for i, (label, value) in enumerate(kpis):
    r, c = divmod(i, 4)
    x = 0.5 + c * (tw + tg)
    y = 8.75 - r * (th + 0.15)
    gradient_tile(x, y, tw, th, *tile_colors[c])
    bg.text(x + 0.28, y + th - 0.32, label, fontsize=11.5, color="white",
            alpha=0.85, va="center", zorder=4)
    bg.text(x + 0.28, y + 0.40, value, fontsize=26, fontweight="bold",
            color="white", va="center", zorder=4)
bg.set_xlim(0, W)
bg.set_ylim(0, H)

# ---------- 6. Card A: revenue trend by listing month ----------
card(0.5, 3.95, 11.4, 3.25, "Revenue trend by listing month",
     "Monthly estimated revenue vs number of products listed")
m = df.dropna(subset=["listing_date"]).copy()
m["month"] = m["listing_date"].dt.to_period("M").dt.to_timestamp()
monthly = m.groupby("month").agg(rev=("revenue", "sum"), listed=("product_id", "count"))
if len(monthly) > 1 and d_max.day < d_max.days_in_month:
    monthly = monthly.iloc[:-1]  # drop the partial last month

ax = add_ax(1.3, 4.3, 10.1, 2.25)
ax.plot(monthly.index, monthly["rev"], color=BLUE, lw=2.4)
ax.fill_between(monthly.index, monthly["rev"], color=BLUE, alpha=0.16)
ax.set_ylim(0, monthly["rev"].max() * 1.3)
ax.yaxis.set_major_formatter(money_axis)
ax.yaxis.set_major_locator(MaxNLocator(4))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.grid(axis="y", color=GRID, lw=1)
ax.set_axisbelow(True)
ax2 = ax.twinx()
ax2.plot(monthly.index, monthly["listed"], color=CYAN, lw=2)
ax2.set_ylim(0, monthly["listed"].max() * 2.8)
ax2.yaxis.set_major_locator(MaxNLocator(4))
ax2.tick_params(length=0, labelsize=9)
for s in ("top", "left", "bottom"):
    ax2.spines[s].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.set_facecolor("none")
ax.legend([Line2D([0], [0], color=BLUE, lw=3), Line2D([0], [0], color=CYAN, lw=3)],
          ["Revenue", "Products listed"], loc="lower right",
          bbox_to_anchor=(1.0, 1.03), ncol=2, frameon=False,
          labelcolor=TEXT, fontsize=10)

# ---------- 7. Card B: discount impact ----------
card(0.5, 0.4, 11.4, 3.35, "Discount impact",
     "Higher discount does not lift units sold, it only cuts revenue per product")
g = df.groupby("discount_percent").agg(
    units=("units_sold", "mean"), rpp=("revenue", "mean")).reset_index()
x = np.arange(len(g))
ax = add_ax(1.3, 0.8, 10.1, 2.05)
ax.bar(x, g["units"], width=0.58, color=INDIGO, alpha=0.9)
ax.set_ylim(0, g["units"].max() * 2.5)
ax.set_xticks(x)
ax.set_xticklabels([f"{int(v)}%" for v in g["discount_percent"]], fontsize=10.5, color=TEXT)
ax.set_yticks([])
for xi, v in zip(x, g["units"]):
    ax.text(xi, v * 0.5, f"{v:,.0f}", ha="center", va="center",
            fontsize=10, color="white", fontweight="bold")
ax2 = ax.twinx()
ax2.plot(x, g["rpp"], color=AMBER, lw=2.8, marker="o", markersize=8,
         markeredgecolor=CARD, markeredgewidth=2)
ax2.set_ylim(-g["rpp"].max() * 0.5, g["rpp"].max() * 1.25)
ax2.set_yticks([])
for s in ("top", "left", "bottom", "right"):
    ax2.spines[s].set_visible(False)
ax2.set_facecolor("none")
for xi, v in zip(x, g["rpp"]):
    ax2.text(xi, v + g["rpp"].max() * 0.07, money(v), ha="center",
             fontsize=9.5, color=AMBER, fontweight="bold")
ax.legend([Line2D([0], [0], color=INDIGO, lw=8), Line2D([0], [0], color=AMBER, lw=3)],
          ["Avg units sold per product", "Avg revenue per product"],
          loc="lower right", bbox_to_anchor=(1.0, 1.03), ncol=2,
          frameon=False, labelcolor=TEXT, fontsize=10)


# ---------- 8. Donut + bar helpers ----------
def donut(x, y, w, h, title, series, palette, subtitle):
    card(x, y, w, h, title, subtitle)
    series = series.sort_values(ascending=False)
    total = series.sum()
    ax = add_ax(x + 0.3, y + 1.35, w - 0.6, h - 2.25)
    ax.pie(series.values, colors=palette[:len(series)], startangle=90,
           counterclock=False,
           wedgeprops=dict(width=0.36, edgecolor=CARD, linewidth=2.5))
    ax.text(0, 0.08, money(total), ha="center", va="center", fontsize=14,
            fontweight="bold", color=TEXT)
    ax.text(0, -0.17, "total revenue", ha="center", va="center",
            fontsize=8.5, color=MUTED)
    labels = [f"{k}  {v / total * 100:.1f}%" for k, v in series.items()]
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=c,
                      markersize=8) for c in palette[:len(series)]]
    ax.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.02),
              ncol=2, frameon=False, labelcolor=TEXT, fontsize=8.5,
              columnspacing=1.0, handletextpad=0.2, labelspacing=0.55)


def hbar(x, y, w, h, title, series, color, subtitle):
    card(x, y, w, h, title, subtitle)
    series = series.sort_values()
    ax = add_ax(x + 1.5, y + 0.3, w - 1.5 - 0.25, h - 1.2)
    n = len(series)
    cols = [to_rgba(color, 0.45 + 0.55 * i / max(n - 1, 1)) for i in range(n)]
    bars = ax.barh(series.index, series.values, color=cols, height=0.62)
    ax.set_xlim(0, series.max() * 1.5)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    ax.tick_params(axis="y", labelsize=9.5, colors=TEXT)
    for b in bars:
        ax.text(b.get_width(), b.get_y() + b.get_height() / 2,
                "  " + money(b.get_width()), va="center", fontsize=9, color=TEXT)


cat = df.groupby("category")["revenue"].sum()
city = df.groupby("seller_city")["revenue"].sum()
brand = df.groupby("brand")["revenue"].sum().sort_values(ascending=False).head(10)
seller = df.groupby("seller")["revenue"].sum()

# ---------- 9. Right-hand cards ----------
donut(12.1, 5.2, 3.65, 4.75, "Revenue by category", cat, PALETTE, "Share of total revenue")
donut(15.85, 5.2, 3.65, 4.75, "Revenue by seller city", city, PALETTE[::-1], "Share of total revenue")
hbar(12.1, 0.4, 3.65, 4.6, "Top 10 brands", brand, CYAN, "By estimated revenue")
hbar(15.85, 0.4, 3.65, 4.6, "Revenue by seller", seller, PURPLE, "By estimated revenue")

bg.text(0.5, 0.17, "Estimated revenue = final price × units sold   •   time axis = product listing date   •   "
        "last partial month excluded from the trend line",
        fontsize=8.5, color=MUTED, va="center")

plt.show()
