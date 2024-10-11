import asyncio
import random
from typing import Type, Dict, List, Optional, Coroutine
from datetime import datetime, timedelta
import time

import aiohttp

class Component:
    pass

class Entity:
    _id_counter: int = 0

    def __init__(self) -> None:
        self.id: int = Entity._id_counter
        Entity._id_counter += 1
        self.components: Dict[Type[Component], Component] = {}

    def add_component(self, component: Component) -> None:
        self.components[type(component)] = component

    def get_component(self, component_type: Type[Component]) -> Optional[Component]:
        return self.components.get(component_type)

class System:
    is_long_running: bool = False

    async def update(self, world: 'World', dt: timedelta) -> None:
        raise NotImplementedError

class World:
    def __init__(self) -> None:
        self.entities: List[Entity] = []
        self.systems: List[System] = []
        self.long_running_tasks: Dict[System, asyncio.Task] = {}

    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def add_system(self, system: System) -> None:
        self.systems.append(system)

    async def update(self, dt: timedelta) -> None:
        # Update fast systems synchronously
        fast_updates = [system.update(self, dt) for system in self.systems if not system.is_long_running]
        await asyncio.gather(*fast_updates)

        # Handle long-running systems
        for system in self.systems:
            if system.is_long_running:
                if system not in self.long_running_tasks or self.long_running_tasks[system].done():
                    self.long_running_tasks[system] = asyncio.create_task(system.update(self, dt))

        # Check for completed long-running tasks
        completed_tasks = [system for system, task in self.long_running_tasks.items() if task.done()]
        for system in completed_tasks:
            task = self.long_running_tasks.pop(system)
            try:
                await task # Await to handle exceptions and (potentially) retrieve results
            except Exception as e:
                print(f"Long-running task for system {system.__class__.__name__} failed: {e}")

# Example components
class PositionComponent(Component):
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class VelocityComponent(Component):
    def __init__(self, vx: float, vy: float):
        self.vx = vx
        self.vy = vy

class TimeComponent(Component):
    def __init__(self):
        self.current_time: Optional[datetime] = None
        self.last_update: float = 0

class NumberCountingComponent(Component):
    def __init__(self, number: int):
        self.number = number

class DayCountingComponent(Component):
    def __init__(self, day: str):
        self.day = day
        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.counter = 0

    def increment_day(self):
        self.counter += 1
        if self.counter % 2 == 0:
            current_index = self.days_of_week.index(self.day)
            self.day = self.days_of_week[(current_index + 1) % 7]

# Example systems
class MovementSystem(System):
    async def update(self, world: World, dt: timedelta) -> None:
        for entity in world.entities:
            pos = entity.get_component(PositionComponent)
            vel = entity.get_component(VelocityComponent)
            if isinstance(pos, PositionComponent) and isinstance(vel, VelocityComponent):
                pos.x += vel.vx * dt.total_seconds()
                pos.y += vel.vy * dt.total_seconds()

# class TimePollingSystem(System):
#     """Doesn't do a real internet call, just simulates a long-running task. Also does a sleep. Also only runs every 5 seconds."""
#     is_long_running = True

#     async def update(self, world: World, dt: timedelta) -> None:
#         current_time = time.time()
#         for entity in world.entities:
#             time_comp = entity.get_component(TimeComponent)
            
#             if isinstance(time_comp, TimeComponent) and current_time - time_comp.last_update >= 5:
#                 await self.fetch_time(time_comp)

#     async def fetch_time(self, time_component: TimeComponent) -> None:
#         # Simulate a long-running API call
#         await asyncio.sleep(2)
#         time_component.current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
#         time_component.last_update = time.time() # could convert the epoch time (float) to a datetime object date_time = datetime.fromtimestamp(epoch_time)

class TimeInternetPollingSystem(System):
    """This implementation now takes advantage of Python's asynchronous
    capabilities, allowing for non-blocking I/O operations when fetching the
    current time from the API. The TimePollingSystem runs concurrently with
    other systems, demonstrating the power of async programming in this ECS
    framework.
    
    Setting is_long_running to True indicates that this system will run probably
    longer than a single frame, and will be managed by the World class via the 
    long_running_tasks dictionary and won't block the main game loop.
    """
    is_long_running = True

    async def update(self, world: World, dt: timedelta) -> None:
        async with aiohttp.ClientSession() as session:
            for entity in world.entities:
                component = entity.get_component(TimeComponent)
                if isinstance(component, TimeComponent):
                    await self.fetch_time(component)

    async def fetch_time(self, time_component: TimeComponent) -> None:
        # Sleep for a random number of milliseconds between 0.3 and 1.5 milliseconds
        sleep_time = random.uniform(1.5, 2.5)
        await asyncio.sleep(sleep_time)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://worldtimeapi.org/api/timezone/Australia/Melbourne") as response:
                    if response.status == 200:
                        data = await response.json()
                        # Parse the datetime string into a datetime object
                        datetime_str = data.get('datetime')
                        time_component.current_time = datetime.fromisoformat(datetime_str)

        except aiohttp.ClientError as e:
            print(f"Error polling time: {e}")
        
class CountingSystem(System):
    async def update(self, world: World, dt: timedelta) -> None:
        for entity in world.entities:
            num_comp = entity.get_component(NumberCountingComponent)
            if isinstance(num_comp, NumberCountingComponent):
                num_comp.number += 1

            day_comp = entity.get_component(DayCountingComponent)
            if isinstance(day_comp, DayCountingComponent):
                day_comp.increment_day()

async def game_loop(world: World, duration: float):
    start_time = time.time()
    last_time = start_time
    frame_count = 0
    while time.time() - start_time < duration:
        current_time = time.time()
        dt = timedelta(seconds=current_time - last_time)
        await world.update(dt)
        last_time = current_time
        frame_count += 1

        # Print entity states
        for entity in world.entities:
            pos = entity.get_component(PositionComponent)
            time_comp = entity.get_component(TimeComponent)
            number_comp = entity.get_component(NumberCountingComponent)
            day_comp = entity.get_component(DayCountingComponent)

            output = [f"Entity {entity.id}:"]
            if isinstance(pos, PositionComponent):
                output.append(f"Position = ({pos.x:.2f}, {pos.y:.2f})")
            if isinstance(number_comp, NumberCountingComponent):
                output.append(f"Number = {number_comp.number}")
            if isinstance(day_comp, DayCountingComponent):
                output.append(f"Day = {day_comp.day}")
            if isinstance(time_comp, TimeComponent):
                if time_comp.current_time is not None:
                    formatted_time = time_comp.current_time.strftime("%Hh %Mm %Ss %fms")
                else:
                    formatted_time = "None (yet)"
                output.append(f"Time = {formatted_time}")
            print(", ".join(output))
        print("---")

        await asyncio.sleep(0.5)  # Simulate frame rate

    print(f"Simulation completed. Average FPS: {frame_count / duration:.2f}")

async def main():
    world = World()

    # Create entities
    entity1 = Entity()
    entity1.add_component(PositionComponent(0, 0))
    entity1.add_component(VelocityComponent(1, 1))
    world.add_entity(entity1)

    entity2 = Entity()
    entity2.add_component(PositionComponent(10, 10))
    entity2.add_component(VelocityComponent(-1, -1))
    world.add_entity(entity2)

    entity3 = Entity()
    entity3.add_component(NumberCountingComponent(0))
    entity3.add_component(DayCountingComponent("Monday"))
    entity3.add_component(TimeComponent())
    world.add_entity(entity3)

    # Add systems
    world.add_system(MovementSystem())
    # world.add_system(TimePollingSystem())
    world.add_system(TimeInternetPollingSystem())
    world.add_system(CountingSystem())

    print("Starting game loop...")
    await game_loop(world, duration=5)

if __name__ == "__main__":
    asyncio.run(main())