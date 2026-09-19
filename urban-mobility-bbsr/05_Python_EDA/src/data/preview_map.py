from pathlib import Path
import matplotlib.pyplot as plt
import osmnx as ox
import geopandas as gpd

# Resolve project root (urban-mobility-bbsr)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "03_Data" / "raw"
INTERIM_DATA_DIR = PROJECT_ROOT / "03_Data" / "interim"
INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)

GRAPH_PATH = RAW_DATA_DIR / "bhubaneswar_road_network.graphml"
BUS_STOPS_PATH = RAW_DATA_DIR / "bhubaneswar_bus_stops_osm.gpkg"
PREVIEW_OUTPUT_PATH = INTERIM_DATA_DIR / "bhubaneswar_network_preview.png"


def create_network_preview():
    print("Loading road network and OSM bus stops...", flush=True)
    
    roads_gpkg = RAW_DATA_DIR / "bhubaneswar_roads.gpkg"
    fig, ax = plt.subplots(figsize=(12, 12))

    if roads_gpkg.exists():
        print(f"Loading road edges from {roads_gpkg}...", flush=True)
        edges = gpd.read_file(roads_gpkg, layer="edges")
        edges.plot(ax=ax, color="#888888", linewidth=0.5, alpha=0.7)
        print(f"Loaded and plotted {len(edges)} road edges.", flush=True)
    elif GRAPH_PATH.exists():
        print(f"Loading road network graph from {GRAPH_PATH}...", flush=True)
        G = ox.load_graphml(GRAPH_PATH)
        fig, ax = ox.plot_graph(
            G,
            bgcolor="white",
            node_size=0,
            edge_color="#888888",
            edge_linewidth=0.5,
            show=False,
            close=False
        )
    else:
        print(f"No road data found at {roads_gpkg} or {GRAPH_PATH}.", flush=True)

    # Load and overlay bus stops
    if BUS_STOPS_PATH.exists():
        bus_stops = gpd.read_file(BUS_STOPS_PATH)
        if not bus_stops.empty:
            bus_stops.plot(
                ax=ax,
                color="red",
                markersize=20,
                alpha=0.9,
                label="OSM Bus Stops",
                zorder=5
            )
            print(f"Plotted {len(bus_stops)} bus stops.", flush=True)
        else:
            print("Bus stops layer is empty.", flush=True)
    else:
        print(f"Bus stops file not found at {BUS_STOPS_PATH}.", flush=True)

    ax.set_title("Bhubaneswar Road Network & OSM Bus Stops", fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper right")
    ax.set_axis_off()

    # Save figure
    fig.savefig(PREVIEW_OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Preview map successfully saved to: {PREVIEW_OUTPUT_PATH}", flush=True)


def main():
    print("=== Generating Bhubaneswar Mobility Network Preview Map ===", flush=True)
    create_network_preview()


if __name__ == "__main__":
    main()
