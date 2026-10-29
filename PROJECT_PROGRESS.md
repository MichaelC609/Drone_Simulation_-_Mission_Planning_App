# Project Progress

**Status date:** October 28, 2026

## Summary

The project is currently at an early backend-prototype stage. The repository contains a Python drone-simulation core with typed drone state and command models, a command queue, command handlers, a fixed-step simulation engine, and asynchronous runner/context scaffolding. Unit tests are present for these core components.

The broader full-stack mission-planning platform described in the README is still a target architecture, not the current implementation. The repository does not yet contain the described web frontend, Spring Boot services, C++ simulation service, or Kafka/Redis/PostgreSQL integrations.

## How the current components work together

The current implementation is a set of Python modules for one drone. Its intended runtime path is:

1. **Models define the data.** `DroneState` contains the drone's position, velocity, battery, heading, status, flight mode, and timestamp. Typed command models pair each command type with the payload it needs.
2. **State manager owns the live state.** It creates the initial state, keeps a previous-state snapshot, and applies partial updates by merging them into the current state. Updates are validated when the merged data is rebuilt as a `DroneState`.
3. **Commands wait in the queue.** `CommandQueue` holds commands in FIFO order until the simulation engine is ready to process them.
4. **Context assembles the simulation.** `SimulationContext` receives the state manager, queue, and handler registry; creates the physics engine and handlers; registers handlers for takeoff, landing, and set-velocity; then constructs the engine and runner.
5. **Runner drives repeated ticks.** When started, `SimulationRunner` calls the engine's `tick()` method and waits for the configured time step (currently 0.05 seconds) before the next tick. Stopping cancels the background task.
6. **Engine dispatches commands.** On a tick, `SimulationEngine` dequeues a command if it does not already have an active one, finds the handler for that command type, and executes it. Commands such as takeoff or landing can remain active across multiple ticks until their handler reports completion.
7. **Handlers update the state.** Takeoff changes altitude, status, and battery; landing lowers altitude, changes status, drains battery, and resets velocity when complete; set-velocity writes the requested velocity into state. State changes go through the state manager.
8. **Physics advances movement.** For ticks that are not executing takeoff or landing, the engine calls `PhysicsEngine.update()`. The physics engine is intended to move an active drone according to its velocity and the fixed time step, keeping altitude at or above zero.

The command flow and state/physics flow are therefore joined at the engine: handlers and physics both update the same state manager, while the runner supplies the repeated timing that makes commands and motion progress over time.

### Component responsibilities and implementation status

| Component | Responsibility | Current connection/status |
|---|---|---|
| Drone models | Typed state, command, and payload structures; validate values such as battery percentage, heading, altitude, and speeds. | Used by state management and simulation handlers. |
| State manager | Own the current state, retain a previous snapshot, merge partial updates, and refresh timestamps. | Shared by the engine, handlers, and physics layer. |
| Command queue | Preserve command order and provide enqueue/dequeue operations. | Read by the simulation engine; it does not itself execute commands. |
| Command validator | Check whether a command is allowed for the current drone status. | A validator class exists, but it is not currently called by the queue, simulation context, or another command-submission path in the source tree. Validation is therefore not yet enforced end-to-end. |
| Handler registry | Map command types to handler implementations and report missing or duplicate registrations. | Populated by `SimulationContext`; queried by the engine during command execution. |
| Command handlers | Implement the state transitions and completion conditions for supported commands. | Takeoff, landing, and set-velocity are registered. A heading command model exists, but no heading handler is registered. |
| Physics engine | Advance an active drone's position using its velocity and the time step. | Called by the engine except on takeoff and landing ticks. Current velocity field names need alignment: the model defines `vx`/`vy`/`vz`, while physics reads `x`/`y`/`z`. |
| Simulation engine | Coordinate command dequeueing, handler execution, physics updates, and simulation time. | The central per-tick coordinator, composed by `SimulationContext`. |
| Simulation context | Construct and connect the objects required for a simulation. | Registers supported handlers and creates the engine and runner. |
| Simulation runner | Run engine ticks asynchronously and support task cancellation. | Provides the repeated loop; it does not currently expose an API endpoint or telemetry stream. |
| API and telemetry modules | Intended entry points and real-time data delivery surfaces. | Directories/modules are present, but no implemented REST or WebSocket flow currently connects clients to the simulation. |

### Intended end-to-end flow versus current implementation

At present, the implemented flow starts inside the backend: application code or a test creates the state manager, queue, registry, and context; commands are placed on the queue; the runner advances ticks; and handlers/physics update the in-memory state. The repository does not yet provide a complete client-facing command-submission flow, so the validator is not wired into that path and no UI receives the resulting state.

The README describes a future product flow in which a user plans a mission in a web dashboard, sends it to backend APIs, and receives live telemetry over WebSockets. That future flow would require the currently missing frontend, API integration, telemetry publication, and durable mission services. Kafka, Redis, PostgreSQL, AI processing, fleet orchestration, and cloud deployment are architectural goals rather than components currently connected to this Python simulation.

## Work completed

### Drone state and command models

- Added Pydantic models for drone position, velocity, status, flight mode, and timestamped state.
- Added validation for battery percentage and heading ranges.
- Added typed commands and payload models for takeoff, landing, velocity, and heading changes.
- Added validation for takeoff altitude and speed, landing speed, target heading, and turn rate.

### Simulation core

- Implemented a FIFO command queue and a handler registry.
- Added a simulation engine that advances in fixed time steps and executes queued commands through their registered handlers.
- Implemented takeoff and landing handlers, including altitude changes, battery drain, status updates, and velocity reset after landing.
- Implemented a set-velocity handler.
- Added basic position updates based on velocity and the simulation time step.
- Added a command-state validator class for rejecting unsupported commands and commands invalid for the drone's current status; it is not yet wired into the command submission flow.

### Runner and composition

- Added a simulation context that wires together the state manager, command queue, handlers, physics engine, and simulation engine.
- Added an asynchronous runner that ticks the engine on a background task and supports stopping and cleanup.

### Tests

Tests are present for drone models and commands, state management, command queue, handler registry, takeoff and landing handlers, simulation-engine behavior, simulation context, and runner lifecycle. Test files are located under `backend/tests/`.

**Verification note:** This document records the test coverage visible in the repository; the test suite was not run as part of this documentation update.

## Current scope and known gaps

- The implemented work is focused on a single simulated drone and its local state/command lifecycle.
- Although a heading command model exists, the current simulation context does not register a heading handler, and the command validator does not accept heading commands yet.
- The physics layer currently accesses velocity as `x`/`y`/`z`, while the velocity model defines `vx`/`vy`/`vz`; this mismatch needs correction and a focused test before relying on movement updates.
- The repository's current implementation is Python. The frontend and distributed services described in the README are not present in the current source tree.
- Mission planning and persistence, authentication, web dashboard, REST endpoints, live WebSocket telemetry, video, AI/computer vision, event streaming, caching, database storage, multi-drone orchestration, and deployment/scaling infrastructure remain future work.
- The next useful milestone is to establish a runnable application/API entry point and verify the core simulation with an end-to-end command-to-state flow before expanding into mission planning and user-facing features.

## Recent implementation milestones
Recent commits show the following sequence of work:
1. Established the simulation context and asynchronous runner, with initial unit tests.
2. Added and tested the handler registry and refactored command execution in the simulation tick.
3. Implemented the set-velocity handler and basic position physics.
4. Updated landing behavior to settle the drone and reset velocity, and added the associated dependency wiring.
5. Added validation of commands before they enter the command queue.

