**Drone Simulation & Mission Planning App: **


1. Project Objectives & Features
	The main goal of this project is to build a Full Stack web app that simulates real drones and allows users to create, plan and replay drone missions with both singular and multiple drones/fleets. Listed below are the planned features of the app as of now: 
Create simulated environments
Launch autonomous drone missions
Stream Telemetry and Video in real time
Run AI-based detection/path-planning algorithms
Monitor missions from a web dashboard
Replay and Analyze completed missions
Scale to multiple drones/simulations simultaneously

	The system can be broken down into several microservices that each handle a different role regarding the core features of the app. First is the frontend, powered by React/Next.js, handling services such as drone telemetry visualization, live map rendering, mission replay UI, analytics panels and simulation controls. Connecting the Frontend to the Backend is the RESTful API and Websocket layer for both live and consistent updates. The backend is primarily written in Java Spring Boot, handling important functions such as Authentication, Simulation lifecycle, Mission management, REST APIs, Websocket connections and Mission persistence. 

**2. Tech Stack**
High Level Overview:

<img width="486" height="288" alt="Screenshot 2026-05-30 at 7 04 01 PM" src="https://github.com/user-attachments/assets/3b522fb2-e39c-4493-9ef3-1faf8854761c" />


**3. System Design & Use Flow**
1. User enters the Platform
Frontend
Tech Stack: Next js, Tailwind CSS
User flow: 
User opens platform in their browser(Vercel deployment link)
Frontend loads authentication state, dashboard data, mission history, active drone sessions
If user not logged in → error state page		
Authentication UI:
Handles login, signup, session state
Communicates with Java Spring Boot backend

Mission Dashboard:
Displays: active drones, telemetry, maps, AI detections, battery data, mission progress
Receives live Websocket telemetry streams
Mission Planning UI:
Users can place waypoints, create routes, configure drones, choose environments
Sends REST API requests to backend
Replay System UI:
Allows users to replay completed missions, view historical telemetry, and view AI detections over time

2) Frontend sends request to Backend
Why Spring Boot?
Spring Boot is the core backend component of the system that manages authentication, logic, orchestration, service coordination and API aggregation
Separates data and requests from the Kafka, Redis, Simulation and AI layers
Example Request Flow: 

<img width="412" height="137" alt="Screenshot 2026-05-30 at 7 05 06 PM" src="https://github.com/user-attachments/assets/566064db-9e35-4c77-9a6a-24694d796bc4" />


Spring Boot flow steps:
Validate Request
Checks if the user is authenticated
Valid mission and permissions
Check if the drone exists
Add Mission to Database
Mission status becomes INITIALIZING(has not started yet)
Publish Event
Backend publishes the event to Kafka

**3) Kafka Event System**
Purpose for Kafka: Kafka acts as a distributed event bus, telemetry pipeline and an asynchronous communication layer
Kafka creates a Publisher/Consumer system where the backend creates and publishes and event for the Simulation layer to then consume the event
This allows the following benefits:
Scalability 
Fault Isolation
Asynchronous Processing
Services to be independent
Example Topics:
Mission Events:
Contains mission start, pause, terminate and reroute commands
Telemetry:
Contains important metrics such as GPS, velocity, drone orientation, altitude, battery info
AI-Detections:
Contains object detections, obstacle warnings, threat alerts




4) Simulation Engine starts
Developed in C++, serves as the performance-critical portion of the app
C++ allows for low latency, multi-threading, efficient memory usage, deterministic simulation timing 
The Simulation is responsible for simulating 1) Physics 2) Waypoint Navigation 3) Environment 4) Sensor Emulation 
Physics:
Calculates acceleration, velocity, drag, momentum, turning dynamics
Updates drone position every simulation tick
Waypoint Navigation:
Reads the mission route
Calculates direction vectors, movement towards targets, path corrections
Environment:
Responsible for simulating terrain, buildings, obstacles, weather, wind, sensor noise
Sensor Emulation:
Generates GPS data, IMU data, Camera Frames, Lidar Scans, Altitude Readings
Internal Simulation Loop:

<img width="230" height="120" alt="Screenshot 2026-05-30 at 7 05 39 PM" src="https://github.com/user-attachments/assets/4affd12e-2d5e-4287-be9a-eb75cae39771" />




5) Telemetry Generation:
What Happens: 
Every simulation tick generates telemetry data

The Simulation Engine then publishes that data to Kafka and Redis
Kafka: 
Stores the event stream and the ordered telemetry history
Used for replay, analytics, asynchronous processing, event sourcing
Redis:
Stores the latest real-time state
Used for ultra-fast and efficient access, Websocket fanout, active drone state

6) Redis Real-Time Layer
Redis acts as a real-time cache, shared-state manager and Publisher/Subscriber(Pub/Sub) System
Reading the Database repeatedly would slow down processing times and the Frontend requires low latency and near-instant updates
Spring Boot reads Redis and pushes the updates to the frontend
Current drone state: latest position, velocity, battery, orientation


<img width="272" height="172" alt="Screenshot 2026-05-30 at 7 05 58 PM" src="https://github.com/user-attachments/assets/ce269d3a-2d8e-4067-8b12-9fc10768faa7" />



7) Websocket Telemetry Streaming:
Websockets are more efficient than REST APIs for real-time updates, since REST APIs are request-response
Telemetry requires continuous streaming, low latency and push-based updates
Flow:

<img width="418" height="143" alt="Screenshot 2026-05-30 at 7 06 34 PM" src="https://github.com/user-attachments/assets/835bd53a-4deb-4e2a-a5ea-f77c27bfbfbb" />

  
UI Updates:
Map Markers, Drone positions, Battery Indicators, Alerts
Does this without having to refresh the page


8) AI/Computer Vision Pipeline
The AI layer is implemented with FastAPI, separated from the Java Spring Boot backend; this is done because AI workloads are GPU-intensive, asynchronous and independent
Allows ML dependencies to be isolated, GPU scalability, and non-blocking of backend operations
System Pipeline:

<img width="429" height="178" alt="Screenshot 2026-05-30 at 7 06 52 PM" src="https://github.com/user-attachments/assets/9f5d744d-7645-4005-952d-cffe2d4a7a31" />


Frontend Visualization:
Visualizes detection boxes, alerts, warnings, route suggestions onto the live-mission view

9) PostgreSQL Persistence Layer
Postgres is used to store durable long-term data
Stored Data:
User Data - accounts, authentication info
Missions - Routes, Mission configurations, Mission history
Telemetry History - historical drone states, replay data
AI Logs - detections, threat events, route recommendations
Replay System - pulls: Historical telemetry, detection events → reconstructs mission

10) Replay System Flow
User opens Replay
Frontend requests GET /missions/{id}/replay
Backend queries for telemetry history and AI detections
Frontend replays drone movement, detections, mission events 



4. Scalability
11) Multi-Drone Scaling:
Mission Controller: Spring Boot orchestrates multiple simulation workers
Each worker runs a separate drone simulation
Distributed Telemetry:
All drones publish to a telemetry-stream event
Frontend aggregates fleet-wide telemetry
Fleet Dashboard:
Swarm Status
Drone Health
Mission Coordination

12) Kubernetes Scaling
Kubernetes allows for horizontal scaling, distributed workers and service orchestration 
As the system grows, having one machine becomes insufficient 
