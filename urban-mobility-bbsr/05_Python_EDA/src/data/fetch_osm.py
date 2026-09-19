import os
from pathlib import Path
import osmnx as ox
import geopandas as gpd

# Resolve project root (urban-mobility-bbsr)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "03_Data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

PLACE_NAME = "Bhubaneswar, Odisha, India"


def fetch_road_network():
    print(f"Fetching drivable road network graph for '{PLACE_NAME}'...", flush=True)
    try:
        G = ox.graph_from_place(PLACE_NAME, network_type="drive")
        graphml_path = RAW_DATA_DIR / "bhubaneswar_road_network.graphml"
        ox.save_graphml(G, filepath=graphml_path)
        print(f"Saved road network graph to {graphml_path}", flush=True)

        # Convert to GeoDataFrames and save as GeoPackage
        nodes, edges = ox.graph_to_gdfs(G)
        gpkg_path = RAW_DATA_DIR / "bhubaneswar_roads.gpkg"

        # Save layers
        edges.to_file(gpkg_path, layer="edges", driver="GPKG")
        nodes.to_file(gpkg_path, layer="nodes", driver="GPKG")
        print(f"Saved road network edges ({len(edges)}) and nodes ({len(nodes)}) to {gpkg_path}", flush=True)
        return len(edges)
    except Exception as e:
        print(f"Error fetching road network: {e}", flush=True)
        return 0


def fetch_bus_stops():
    print(f"Fetching OSM-tagged bus stops for '{PLACE_NAME}'...", flush=True)
    bus_stop_tags = {"highway": "bus_stop"}
    try:
        bus_stops = ox.features_from_place(PLACE_NAME, bus_stop_tags)
        if bus_stops.empty:
            print("No bus stops found matching highway=bus_stop.", flush=True)
            bus_stops = gpd.GeoDataFrame()
    except Exception as e:
        print(f"Error or no features found for bus stops: {e}", flush=True)
        bus_stops = gpd.GeoDataFrame()

    out_path = RAW_DATA_DIR / "bhubaneswar_bus_stops_osm.gpkg"
    if not bus_stops.empty:
        bus_stops.to_file(out_path, driver="GPKG")
        print(f"Saved {len(bus_stops)} bus stops to {out_path}", flush=True)
    else:
        print(f"No bus stop records saved to {out_path}", flush=True)
    
    return len(bus_stops)


def fetch_pois():
    print(f"Fetching key POIs for '{PLACE_NAME}'...", flush=True)
    poi_tags = {
        "amenity": ["hospital", "college", "university", "marketplace", "bus_station"],
        "shop": ["mall"],
        "railway": ["station"],
    }
    try:
        pois = ox.features_from_place(PLACE_NAME, poi_tags)
        if pois.empty:
            print("No POIs found matching target tags.", flush=True)
            pois = gpd.GeoDataFrame()
    except Exception as e:
        print(f"Error or no features found for POIs: {e}", flush=True)
        pois = gpd.GeoDataFrame()

    out_path = RAW_DATA_DIR / "bhubaneswar_pois.gpkg"
    if not pois.empty:
        pois.to_file(out_path, driver="GPKG")
        print(f"Saved {len(pois)} POIs to {out_path}", flush=True)
    else:
        print(f"No POI records saved to {out_path}", flush=True)

    return len(pois)


def main():
    print("=== OpenStreetMap Data Extraction for Bhubaneswar ===", flush=True)
    road_count = fetch_road_network()
    bus_stop_count = fetch_bus_stops()
    poi_count = fetch_pois()

    print("\n--- Data Extraction Summary ---", flush=True)
    print(f"Roads: {road_count}", flush=True)
    print(f"OSM-tagged bus stops: {bus_stop_count}", flush=True)
    print(f"POIs: {poi_count}", flush=True)
    print("Extraction complete.", flush=True)


if __name__ == "__main__":
    main()
