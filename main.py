import asyncio
from typing import Type, Dict, List, Optional, Coroutine
from datetime import timedelta, datetime
import aiohttp
import time

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
    async def update(self, world: 'World', dt: timedelta) -> None:
        raise NotImplementedError

class World:
    def __init__(self) -> None:
        self.entities: List[Entity] = []
        self.systems: List[System] = []
        self.long_running_tasks: Dict[int, asyncio.Task] = {}

    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def add_system(self, system: System) -> None:
        self.systems.append(system)

    def add_long_running_task(self, entity_id: int, coro: Coroutine) -> None:
        if entity_id not in self.long_running_tasks or self.long_running_tasks[entity_id].done():
            self.long_running_tasks[entity_id] = asyncio.create_task(coro)

    async def update(self, dt: timedelta) -> None:
        await asyncio.gather(*[system.update(self, dt) for system in self.systems])

        completed_tasks = [entity_id for entity_id, task in self.long_running_tasks.items() if task.done()]
        for entity_id in completed_tasks:
            task = self.long_running_tasks.pop(entity_id)
            try:
                await task
            except Exception as e:
                print(f"Long-running task for entity {entity_id} failed: {e}")

class NumberComponent(Component):
    def __init__(self, number: int):
        self.number = number

class DayComponent(Component):
    def __init__(self, day: str):
        self.day = day
        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def increment_day(self):
        current_index = self.days_of_week.index(self.day)
        self.day = self.days_of_week[(current_index + 1) % 7]

class TimePollingComponent(Component):
    def __init__(self):
        self.current_time: Optional[str] = None
        self.last_update: float = 0

class MovementSystem(System):
    async def update(self, world: World, dt: timedelta) -> None:
        for entity in world.entities:
            number_comp = entity.get_component(NumberComponent)
            if isinstance(number_comp, NumberComponent):
                number_comp.number += 1

class DayIncrementSystem(System):
    async def update(self, world: World, dt: timedelta) -> None:
        for entity in world.entities:
            day_comp = entity.get_component(DayComponent)
            if isinstance(day_comp, DayComponent):
                day_comp.increment_day()

class TimePollingSystem(System):
    async def update(self, world: World, dt: timedelta) -> None:
        current_time = time.time()
        for entity in world.entities:
            time_component = entity.get_component(TimePollingComponent)
            if isinstance(time_component, TimePollingComponent):
                if current_time - time_component.last_update >= 5:
                    world.add_long_running_task(entity.id, self.fetch_time(time_component))

    async def fetch_time(self, time_component: TimePollingComponent) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://worldtimeapi.org/api/timezone/Australia/Melbourne") as response:
                    await asyncio.sleep(1)  # Artificially delay the HTTP call by 1 second
                    if response.status == 200:
                        data = await response.json()
                        time_component.current_time = data.get('datetime')
                        time_component.last_update = time.time()
                    else:
                        print(f"Failed to fetch time. Status code: {response.status}")
        except Exception as e:
            print(f"Failed to fetch time: {e}")

async def game_loop(world: World, duration: float):
    start_time = time.time()
    last_time = start_time
    frame_count = 0
    while time.time() - start_time < duration:
        print(f"Frame {frame_count}, Time Left: {duration - (time.time() - start_time):.2f}")
        current_time = time.time()
        dt = timedelta(seconds=current_time - last_time)
        await world.update(dt)
        last_time = current_time
        frame_count += 1

        # Print essential output
        for entity in world.entities:
            number_comp = entity.get_component(NumberComponent)
            day_comp = entity.get_component(DayComponent)
            time_comp = entity.get_component(TimePollingComponent)
            
            output = f"Entity {entity.id}: "
            if isinstance(number_comp, NumberComponent):
                output += f"Number = {number_comp.number}, "
            if isinstance(day_comp, DayComponent):
                output += f"Day = {day_comp.day}, "
            if isinstance(time_comp, TimePollingComponent):
                output += f"Time = {time_comp.current_time}"
            
            print(output.rstrip(', '))
        
        print("---")

        await asyncio.sleep(0.01)  # Introduce a small delay to simulate a realistic frame rate

    elapsed_time = time.time() - start_time
    print(f"Simulation completed. Average FPS: {frame_count / elapsed_time:.2f}")

async def main():
    world = World()

    # Create entities
    entity1 = Entity()
    entity1.add_component(NumberComponent(0))
    entity1.add_component(DayComponent("Monday"))
    entity1.add_component(TimePollingComponent())
    world.add_entity(entity1)

    entity2 = Entity()
    entity2.add_component(NumberComponent(10))
    entity2.add_component(DayComponent("Wednesday"))
    world.add_entity(entity2)

    # Add systems
    world.add_system(MovementSystem())
    world.add_system(DayIncrementSystem())
    world.add_system(TimePollingSystem())

    print("Starting game loop...")
    await game_loop(world, duration=1)  # Run for 1 second

if __name__ == "__main__":
    asyncio.run(main())