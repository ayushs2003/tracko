import json
import heapq
import math

# Load the JSON file
with open("routes_v3.json", "r") as file:
    bus_data = json.load(file)

# Haversine formula to calculate distance (in meters)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) **2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c  # Distance in meters

# Extract all stops into a dictionary
all_stops = {}
bus_routes = {}

for route in bus_data:
    route_name = route["Route"]
    bus_routes[route_name] = []

    for stop in route["StopsAt"]:
        stop_name = stop["name"]
        lat, lon = stop["lat"], stop["lon"]

        all_stops[stop_name] = (lat, lon)
        bus_routes[route_name].append(stop_name)

# Build Graph: { "Stop": [(Neighbor, Distance, Mode, Bus Name)] }
graph = {}

for route, stops in bus_routes.items():
    for i in range(len(stops) - 1):
        stop1, stop2 = stops[i], stops[i + 1]
        lat1, lon1 = all_stops[stop1]
        lat2, lon2 = all_stops[stop2]

        distance = haversine(lat1, lon1, lat2, lon2)

        if stop1 not in graph:
            graph[stop1] = []
        if stop2 not in graph:
            graph[stop2] = []

        # Add bus travel edges with bus name
        graph[stop1].append((stop2, distance, "bus", route))
        graph[stop2].append((stop1, distance, "bus", route))

# **Optimized Pathfinding Algorithm (Minimize Transfers First)**
def find_best_route(source, destination):
    pq = [(0, 0, source, [], None)]  # (bus_changes, cost, current_stop, path, current_bus)
    visited = {}

    while pq:
        bus_changes, cost, current_stop, path, current_bus = heapq.heappop(pq)

        if current_stop in visited and visited[current_stop] <= (bus_changes, cost):
            continue
        visited[current_stop] = (bus_changes, cost)

        path = path + [(current_stop, current_bus)]

        if current_stop == destination:
            return path, cost

        for neighbor, distance, mode, bus in graph.get(current_stop, []):
            # **Prioritize fewer bus changes first, then consider distance**
            new_bus_changes = bus_changes + (1 if bus != current_bus and current_bus is not None else 0)
            heapq.heappush(pq, (new_bus_changes, cost + distance, neighbor, path, bus))

    return None, float("inf")

# Function to print the route details
def print_route(path):
    if not path:
        print("No route found.")
        return

    print("\nRoute Details:")
    last_bus = None

    for i in range(len(path)):
        stop, bus = path[i]

        if i == 0:
            print(f"Start at: {stop}")

        elif bus != last_bus:
            if last_bus is not None:
                print(f"Change bus at: {path[i-1][0]}")
            print(f"Take Bus {bus} to: {stop}")

        last_bus = bus

    print(f"Arrived at: {path[-1][0]}")
    print("✅ Route Completed!")

# Get user input for source and destination
source = input("Enter Source Stop: ")
destination = input("Enter Destination Stop: ")

best_route, total_distance = find_best_route(source, destination)

if best_route:
    print_route(best_route)
    print(f"\nTotal Distance: {total_distance:.2f} meters")
else:
    print("No route found.")
