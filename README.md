# ECS - Entity Component System - Experimentation

This is a simple project to experiment with the ECS pattern in Python.

## ECS

The ECS pattern is a way to structure your code in a way that separates the data from the logic. This is done by creating entities that are composed of components. The components are just data, and the entities are just a collection of components. The systems are the logic that operates on the entities.

## Running the code

To run the code, you need to have Python 3 installed. You can run the code by executing the following command:

```bash
uv run main.py
```

# Architecture

You're right, and I apologize for not addressing the broader architectural issue in my previous response. Let's design a more general solution that accommodates both fast and long-running systems within the ECS architecture.

This updated ECS architecture addresses the issue of mixing fast and long-running systems. Here are the key changes and features:

1. Added an `is_long_running` flag to the `System` class, defaulting to `False`.

2. Modified the `World.update` method to handle both fast and long-running systems:
   - Fast systems are updated synchronously using `asyncio.gather`.
   - Long-running systems are managed as background tasks using `asyncio.create_task`.

3. Long-running tasks are stored in a dictionary, allowing them to continue across multiple frames.

4. Completed long-running tasks are checked and cleaned up in each update cycle.

5. The `TimePollingSystem` is now implemented as a long-running system, simulating an API call with a 2-second delay.

6. The `game_loop` function now runs for 15 seconds to demonstrate the behavior of both fast and long-running systems.

This architecture allows for a mix of fast and long-running systems within the ECS framework:

- Fast systems (like `MovementSystem`) update every frame.
- Long-running systems (like `TimePollingSystem`) run in the background and don't block the main game loop.
- Long-running tasks that complete are processed in subsequent frames.

To use this architecture:

1. For fast systems, implement them as normal, inheriting from `System`.
2. For long-running systems, set `is_long_running = True` in the class definition.
3. Implement the `update` method for all systems, using `await` for any asynchronous operations.

This solution provides a general framework for handling both types of systems efficiently within the ECS architecture, maintaining good performance for game-like systems while accommodating occasional long-running tasks.

# Example Output

```
Starting game loop...
Entity 0:, Position = (0.00, 0.00)
Entity 1:, Position = (10.00, 10.00)
Entity 2:, Number = 1, Day = Monday, Time = None (yet), Fake Time = None (yet)
---
Entity 0:, Position = (0.50, 0.50)
Entity 1:, Position = (9.50, 9.50)
Entity 2:, Number = 2, Day = Tuesday, Time = None (yet), Fake Time = None (yet)
---
Entity 0:, Position = (1.00, 1.00)
Entity 1:, Position = (9.00, 9.00)
Entity 2:, Number = 3, Day = Tuesday, Time = None (yet), Fake Time = 32s
---
Entity 0:, Position = (1.50, 1.50)
Entity 1:, Position = (8.50, 8.50)
Entity 2:, Number = 4, Day = Wednesday, Time = 32s, Fake Time = 32s
---
Entity 0:, Position = (2.01, 2.01)
Entity 1:, Position = (7.99, 7.99)
Entity 2:, Number = 5, Day = Wednesday, Time = 32s, Fake Time = 32s
---
Entity 0:, Position = (2.51, 2.51)
Entity 1:, Position = (7.49, 7.49)
Entity 2:, Number = 6, Day = Thursday, Time = 33s, Fake Time = 32s
---
Entity 0:, Position = (3.01, 3.01)
Entity 1:, Position = (6.99, 6.99)
Entity 2:, Number = 7, Day = Thursday, Time = 33s, Fake Time = 32s
---
Entity 0:, Position = (3.51, 3.51)
Entity 1:, Position = (6.49, 6.49)
Entity 2:, Number = 8, Day = Friday, Time = 33s, Fake Time = 32s
---
Entity 0:, Position = (4.01, 4.01)
Entity 1:, Position = (5.99, 5.99)
Entity 2:, Number = 9, Day = Friday, Time = 33s, Fake Time = 35s
---
Entity 0:, Position = (4.51, 4.51)
Entity 1:, Position = (5.49, 5.49)
Entity 2:, Number = 10, Day = Saturday, Time = 35s, Fake Time = 35s
---
Simulation completed. Average FPS: 2.00
```

