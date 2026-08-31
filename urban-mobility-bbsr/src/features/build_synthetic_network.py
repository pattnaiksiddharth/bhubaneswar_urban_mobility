"""
build_synthetic_network.py

Purpose
-------
Bhubaneswar's real Mo Bus (Ama Bus) GTFS data is not publicly downloadable
(only 30 bus stops are tagged in OSM, against ~35 real routes and hundreds
of real stops). This script builds a DEFENSIBLE SYNTHETIC stop/route/demand
layer on top of the REAL road network and REAL POI data pulled via osmnx,
so the rest of the analysis (spatial EDA, forecasting) has something
realistic to work with.

This is documented as a modeling assumption, not presented as real CRUT data.

Inputs (expected in data/raw/, produced by fetch_osm.py):
    - bhubaneswar_roads.gpkg        (layers: 'nodes', 'edges')
    - bhubaneswar_pois.gpkg
    - bhubaneswar_bus_stops_osm.gpkg

Outputs (written to data/processed/):
    - synthetic_stops.geojson        one row per synthetic stop
    - synthetic_routes.geojson       one row per route (as LineString along real roads)
    - stop_demand_weights.csv        stop_id, base_weight, poi_breakdown
"""

import geopandas as gpd
import osmnx as ox
import networkx as nx
import pandas as pd
from shapely.geometry import Point
from sklearn.cluster import DBSCAN
import numpy as np

RAW_DIR = "data/raw"
PROC_DIR = "data/processed"

# ---------------------------------------------------------------------------
# STEP 0: Config — trip-generation weights per POI type (subjective, documented)
# ---------------------------------------------------------------------------
POI_WEIGHTS = {
    "hospital": 8,
    "university": 7,
    "college": 6,
    "mall": 5,
    "marketplace": 4,
    "bus_station": 9,
    "station": 9,   # railway station
}

# Hour-of-day multipliers by POI-dominant type (rough, documented assumption)
# index 0-23
HOSPITAL_CURVE = np.clip(np.sin(np.linspace(0, np.pi, 24)) + 0.6, 0.3, None)
COLLEGE_CURVE = np.zeros(24)
COLLEGE_CURVE[7:10] = 1.4
COLLEGE_CURVE[14:17] = 1.3
COLLEGE_CURVE[10:14] = 0.6
COLLEGE_CURVE[COLLEGE_CURVE == 0] = 0.2
MALL_CURVE = np.zeros(24)
MALL_CURVE[11:14] = 0.8
MALL_CURVE[17:21] = 1.5
MALL_CURVE[MALL_CURVE == 0] = 0.2
HUB_CURVE = np.clip(np.sin(np.linspace(0, 2 * np.pi, 24)) + 1.2, 0.4, None)

CURVE_MAP = {
    "hospital": HOSPITAL_CURVE,
    "university": COLLEGE_CURVE,
    "college": COLLEGE_CURVE,
    "mall": MALL_CURVE,
    "marketplace": MALL_CURVE,
    "bus_station": HUB_CURVE,
    "station": HUB_CURVE,
}


def load_data():
    edges = gpd.read_file(f"{RAW_DIR}/bhubaneswar_roads.gpkg", layer="edges")
    nodes = gpd.read_file(f"{RAW_DIR}/bhubaneswar_roads.gpkg", layer="nodes")
    pois = gpd.read_file(f"{RAW_DIR}/bhubaneswar_pois.gpkg")
    return edges, nodes, pois


def classify_poi_type(row):
    """Map raw OSM tags to our simplified POI_WEIGHTS categories."""
    for col in ["amenity", "shop", "railway"]:
        if col in row and pd.notna(row[col]):
            val = str(row[col]).lower()
            if val in POI_WEIGHTS:
                return val
    return None


def cluster_pois_to_zones(pois, eps_m=400, min_samples=1):
    """
    Cluster nearby POIs into 'demand zones' using DBSCAN on projected
    coordinates (meters), so we don't place a stop next to every single POI.
    """
    pois = pois.to_crs(epsg=32644)  # UTM zone for Odisha, meters
    pois["poi_type"] = pois.apply(classify_poi_type, axis=1)
    pois = pois[pois["poi_type"].notna()].copy()
    pois["weight"] = pois["poi_type"].map(POI_WEIGHTS)

    coords = np.array([[geom.centroid.x, geom.centroid.y] for geom in pois.geometry])
    db = DBSCAN(eps=eps_m, min_samples=min_samples).fit(coords)
    pois["cluster_id"] = db.labels_

    # Determine dominant POI type per cluster based on highest cumulative weight
    cluster_dominant = (
        pois.groupby(["cluster_id", "poi_type"])["weight"]
        .sum()
        .reset_index()
        .sort_values(["cluster_id", "weight"], ascending=[True, False])
        .drop_duplicates(subset=["cluster_id"])
        .set_index("cluster_id")["poi_type"]
    )

    zones = pois.dissolve(by="cluster_id", aggfunc={"weight": "sum"})
    zones["dominant_type"] = zones.index.map(cluster_dominant)
    zones["centroid"] = zones.geometry.centroid
    zones = zones.set_geometry("centroid").set_crs(epsg=32644).to_crs(epsg=4326)
    zones = zones.reset_index()
    return zones, pois.to_crs(epsg=4326)


def snap_zones_to_nearest_node(zones, nodes, G):
    """Snap each demand zone centroid to nearest real road graph node."""
    stop_records = []
    for i, row in zones.iterrows():
        lon, lat = row.centroid.x, row.centroid.y
        nearest_node = ox.distance.nearest_nodes(G, lon, lat)
        node_row = nodes.loc[nodes["osmid"] == nearest_node]
        if node_row.empty:
            continue
        stop_records.append({
            "stop_id": f"SYN{i:03d}",
            "node_id": nearest_node,
            "lat": node_row.iloc[0].geometry.y,
            "lon": node_row.iloc[0].geometry.x,
            "base_weight": row["weight"],
            "dominant_type": row.get("dominant_type", "hospital"),
        })
    return gpd.GeoDataFrame(
        stop_records,
        geometry=[Point(r["lon"], r["lat"]) for r in stop_records],
        crs="EPSG:4326",
    )


def build_routes_from_hub(G, stops_gdf, hub_query="Baramunda, Bhubaneswar, Odisha, India"):
    """
    Route each synthetic stop back to the real hub (Baramunda ISBT) via
    shortest path on the real road network, giving realistic route shapes.
    """
    try:
        hub_lat, hub_lon = ox.geocoder.geocode(hub_query)
        print(f"  Geocoded hub '{hub_query}' -> ({hub_lat:.4f}, {hub_lon:.4f})", flush=True)
    except Exception as e:
        print(f"  Geocoding failed for '{hub_query}': {e}. Using Baramunda ISBT default coordinates.", flush=True)
        hub_lat, hub_lon = 20.2798, 85.7876

    hub_node = ox.distance.nearest_nodes(G, hub_lon, hub_lat)

    routes = []
    for _, stop in stops_gdf.iterrows():
        try:
            path = nx.shortest_path(G, hub_node, stop["node_id"], weight="length")
            line = ox.routing.route_to_gdf(G, path)
            routes.append({
                "route_id": f"R_{stop['stop_id']}",
                "stop_id": stop["stop_id"],
                "geometry": line.unary_union,
            })
        except (nx.NetworkXNoPath, ValueError, Exception):
            continue
    return gpd.GeoDataFrame(routes, crs="EPSG:4326")


def compute_hourly_demand(stops_with_types):
    """
    Produce a stop x hour demand matrix using base_weight * hour curve
    for the dominant POI type near that stop.
    """
    records = []
    for _, row in stops_with_types.iterrows():
        curve = CURVE_MAP.get(row.get("dominant_type", "hospital"), HOSPITAL_CURVE)
        for hour in range(24):
            records.append({
                "stop_id": row["stop_id"],
                "hour": hour,
                "demand_proxy": round(row["base_weight"] * curve[hour], 2),
            })
    return pd.DataFrame(records)


def main():
    print("Loading road network, nodes, and POIs...", flush=True)
    edges, nodes, pois = load_data()
    G = ox.graph_from_gdfs(nodes.set_index("osmid"), edges.set_index(["u", "v", "key"]))

    print("Clustering POIs into demand zones...", flush=True)
    zones, pois_typed = cluster_pois_to_zones(pois)
    print(f"  -> {len(zones)} demand zones from {len(pois_typed)} classified POIs", flush=True)

    print("Snapping zones to road network nodes (synthetic stops)...", flush=True)
    stops = snap_zones_to_nearest_node(zones, nodes, G)
    print(f"  -> {len(stops)} synthetic stops created", flush=True)

    print("Building routes from Baramunda ISBT hub to each stop...", flush=True)
    routes = build_routes_from_hub(G, stops)
    print(f"  -> {len(routes)} routes built", flush=True)

    print("Computing hourly demand proxy per stop...", flush=True)
    demand_df = compute_hourly_demand(stops)

    print("Saving outputs...", flush=True)
    stops.to_file(f"{PROC_DIR}/synthetic_stops.geojson", driver="GeoJSON")
    routes.to_file(f"{PROC_DIR}/synthetic_routes.geojson", driver="GeoJSON")
    demand_df.to_csv(f"{PROC_DIR}/stop_demand_weights.csv", index=False)

    print("Done. Files written to data/processed/", flush=True)


if __name__ == "__main__":
    main()