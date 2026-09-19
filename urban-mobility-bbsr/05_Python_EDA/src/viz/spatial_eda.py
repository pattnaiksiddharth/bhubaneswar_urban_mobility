"""
spatial_eda.py

Spatial Exploratory Data Analysis (EDA) for Bhubaneswar Urban Mobility Analytics.

Inputs:
    - data/raw/bhubaneswar_roads.gpkg (layers: 'nodes', 'edges')
    - data/processed/synthetic_stops.geojson
    - data/processed/synthetic_routes.geojson
    - data/processed/stop_demand_weights.csv

Outputs:
    - data/processed/high_centrality_nodes.geojson
    - data/processed/stop_demand_summary.csv
    - reports/figures/01_stops_by_demand.png
    - reports/figures/02_high_centrality_nodes.png
    - reports/figures/03_synthetic_routes.png
    - reports/figures/04_demand_by_poi_type.png
    - reports/figures/bhubaneswar_interactive_map.html
"""

from pathlib import Path
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
RAW_DIR = PROJECT_ROOT / "03_Data" / "raw"
PROC_DIR = PROJECT_ROOT / "03_Data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports" / "figures"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def step1_compute_centrality():
    print("--- Step 1: Computing Road Network Centrality ---", flush=True)
    roads_gpkg = RAW_DIR / "bhubaneswar_roads.gpkg"
    edges = gpd.read_file(roads_gpkg, layer="edges")
    nodes = gpd.read_file(roads_gpkg, layer="nodes")

    G = ox.graph_from_gdfs(nodes.set_index("osmid"), edges.set_index(["u", "v", "key"]))
    print(f"Graph loaded with {len(G.nodes)} nodes and {len(G.edges)} edges.", flush=True)

    # Compute betweenness centrality (using k=150 sample for fast performance)
    print("Computing betweenness centrality (k=150 sample)...", flush=True)
    centrality_dict = nx.betweenness_centrality(G, k=150, weight="length", seed=42)

    # Convert to DataFrame and select top 20
    centrality_df = pd.DataFrame(
        list(centrality_dict.items()), columns=["osmid", "centrality_score"]
    ).sort_values("centrality_score", ascending=False)
    top20_df = centrality_df.head(20)

    # Merge with nodes GeoDataFrame to get geometry
    top20_gdf = nodes.merge(top20_df, on="osmid").sort_values("centrality_score", ascending=False)

    out_geojson = PROC_DIR / "high_centrality_nodes.geojson"
    top20_gdf.to_file(out_geojson, driver="GeoJSON")
    print(f"Saved top 20 high-centrality nodes to {out_geojson}", flush=True)
    return top20_gdf, G, edges, nodes


def step2_aggregate_demand():
    print("\n--- Step 2: Aggregating Stop Demand Data ---", flush=True)
    stops_gdf = gpd.read_file(PROC_DIR / "synthetic_stops.geojson")
    demand_df = pd.read_csv(PROC_DIR / "stop_demand_weights.csv")

    daily_demand = (
        demand_df.groupby("stop_id")["demand_proxy"]
        .sum()
        .reset_index()
        .rename(columns={"demand_proxy": "total_daily_demand"})
    )

    summary_df = stops_gdf.merge(daily_demand, on="stop_id")
    summary_df["lat"] = summary_df.geometry.y
    summary_df["lon"] = summary_df.geometry.x

    out_csv = PROC_DIR / "stop_demand_summary.csv"
    cols = ["stop_id", "lat", "lon", "dominant_type", "total_daily_demand"]
    summary_df[cols].to_csv(out_csv, index=False)
    print(f"Saved stop demand summary ({len(summary_df)} stops) to {out_csv}", flush=True)
    return summary_df, stops_gdf


def step3_generate_static_plots(edges, summary_df, top20_gdf):
    print("\n--- Step 3: Generating Static Visualizations ---", flush=True)
    routes_gdf = gpd.read_file(PROC_DIR / "synthetic_routes.geojson")

    # Fig 1: Stops by Demand
    fig, ax = plt.subplots(figsize=(12, 10))
    edges.plot(ax=ax, color="#cccccc", linewidth=0.5, alpha=0.7)
    stops_summary_gdf = gpd.GeoDataFrame(
        summary_df, geometry=gpd.points_from_xy(summary_df.lon, summary_df.lat), crs="EPSG:4326"
    )
    scatter = ax.scatter(
        summary_df.lon,
        summary_df.lat,
        c=summary_df.total_daily_demand,
        s=summary_df.total_daily_demand * 0.4 + 20,
        cmap="YlOrRd",
        alpha=0.85,
        edgecolors="black",
        linewidths=0.5,
    )
    plt.colorbar(scatter, ax=ax, label="Total Daily Demand Proxy")
    ax.set_title("Fig 1: Bhubaneswar Synthetic Stops Sized & Colored by Daily Demand", fontsize=13, fontweight="bold")
    ax.set_axis_off()
    fig1_path = REPORTS_DIR / "01_stops_by_demand.png"
    fig.savefig(fig1_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Fig 1 to {fig1_path}", flush=True)

    # Fig 2: High Centrality Nodes
    fig, ax = plt.subplots(figsize=(12, 10))
    edges.plot(ax=ax, color="#aaaaaa", linewidth=0.5, alpha=0.7)
    top20_gdf.plot(
        ax=ax, color="red", marker="*", markersize=150, zorder=5, label="Top 20 Centrality Nodes"
    )
    ax.set_title("Fig 2: Bhubaneswar Road Network - Top 20 High-Centrality Congestion Nodes", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right")
    ax.set_axis_off()
    fig2_path = REPORTS_DIR / "02_high_centrality_nodes.png"
    fig.savefig(fig2_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Fig 2 to {fig2_path}", flush=True)

    # Fig 3: Synthetic Routes
    fig, ax = plt.subplots(figsize=(12, 10))
    edges.plot(ax=ax, color="#dddddd", linewidth=0.4, alpha=0.6)
    routes_gdf.plot(ax=ax, column="route_id", cmap="tab20", linewidth=1.5, alpha=0.85)
    ax.set_title("Fig 3: Bhubaneswar Synthetic Mo Bus Routes Network", fontsize=13, fontweight="bold")
    ax.set_axis_off()
    fig3_path = REPORTS_DIR / "03_synthetic_routes.png"
    fig.savefig(fig3_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Fig 3 to {fig3_path}", flush=True)

    # Fig 4: Demand by POI Category
    fig, ax = plt.subplots(figsize=(9, 5.5))
    poi_demand = summary_df.groupby("dominant_type")["total_daily_demand"].sum().sort_values(ascending=False)
    bars = ax.bar(poi_demand.index, poi_demand.values, color="#2b5c8f", edgecolor="black", alpha=0.85)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    ax.set_title("Fig 4: Total Daily Simulated Demand by Dominant POI Category", fontsize=12, fontweight="bold")
    ax.set_ylabel("Total Daily Demand Proxy")
    ax.set_xlabel("Dominant POI Category")
    plt.xticks(rotation=15)
    plt.tight_layout()
    fig4_path = REPORTS_DIR / "04_demand_by_poi_type.png"
    fig.savefig(fig4_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Fig 4 to {fig4_path}", flush=True)


def step4_generate_interactive_map(summary_df, top20_gdf):
    print("\n--- Step 4: Generating Interactive Folium Map ---", flush=True)
    center_lat = summary_df["lat"].mean()
    center_lon = summary_df["lon"].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="CartoDB positron")

    # Add stops layer
    stops_group = folium.FeatureGroup(name="Synthetic Bus Stops").add_to(m)
    for _, row in summary_df.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=min(max(row["total_daily_demand"] / 40.0, 4), 16),
            color="#d95f02",
            fill=True,
            fill_color="#7570b3",
            fill_opacity=0.7,
            popup=f"<b>Stop ID:</b> {row['stop_id']}<br>"
                  f"<b>POI Type:</b> {row['dominant_type']}<br>"
                  f"<b>Daily Demand:</b> {row['total_daily_demand']:.1f}",
        ).add_to(stops_group)

    # Add high-centrality nodes layer
    centrality_group = folium.FeatureGroup(name="Top 20 Centrality Nodes").add_to(m)
    for _, row in top20_gdf.iterrows():
        lat = row.geometry.y
        lon = row.geometry.x
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color="red", icon="star", prefix="fa"),
            popup=f"<b>Node OsmID:</b> {row['osmid']}<br>"
                  f"<b>Centrality Score:</b> {row['centrality_score']:.6f}",
        ).add_to(centrality_group)

    folium.LayerControl().add_to(m)
    out_html = REPORTS_DIR / "bhubaneswar_interactive_map.html"
    m.save(str(out_html))
    print(f"Saved Interactive Folium Map to {out_html}", flush=True)


def main():
    print("=== Bhubaneswar Urban Mobility Spatial EDA Pipeline ===")
    top20_gdf, G, edges, nodes = step1_compute_centrality()
    summary_df, stops_gdf = step2_aggregate_demand()
    step3_generate_static_plots(edges, summary_df, top20_gdf)
    step4_generate_interactive_map(summary_df, top20_gdf)
    print("\nSpatial EDA execution complete!")


if __name__ == "__main__":
    main()
