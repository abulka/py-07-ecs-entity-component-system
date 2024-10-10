import asyncio
import aiohttp
from typing import Type, Dict, List, Optional
from datetime import timedelta

# ECS Framework

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
        print(f"Added component {type(component).__name__} to entity {self.id}")

    def get_component(self, component_type: Type[Component]) -> Optional[Component]:
        return self.components.get(component_type)

class System:
    async def update(self, world: 'World', dt: timedelta) -> None:
        raise NotImplementedError

class World:
    def __init__(self) -> None:
        self.entities: List[Entity] = []
        self.systems: List[System] = []

    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def add_system(self, system: System) -> None:
        self.systems.append(system)

    async def update(self, dt: timedelta) -> None:
        print(f"Updating world by {dt.total_seconds()} seconds")
        await asyncio.gather(*[system.update(self, dt) for system in self.systems])

# Components
class NumberComponent(Component):
    def __init__(self, number: int) -> None:
        self.number: int = number

class DayComponent(Component):
    def __init__(self, day: str) -> None:
        self.day: str = day
        self.days_of_week: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def increment_day(self) -> None:
        current_index = self.days_of_week.index(self.day)
        self.day = self.days_of_week[(current_index + 1) % 7]

class TimePollingComponent(Component):
    def __init__(self) -> None:
        self.current_time: Optional[str] = None

# Systems
class IncrementNumberSystem(System):
    async def update(self, world: World, dt: timedelta) -> None:
        for entity in world.entities:
            component = entity.get_component(NumberComponent)
            if isinstance(component, NumberComponent):
                component.number += 1

class IncrementDaySystem(System):
    def __init__(self) -> None:
        self.accumulated_time = timedelta(0)

    async def update(self, world: World, dt: timedelta) -> None:
        self.accumulated_time += dt
        if self.accumulated_time >= timedelta(seconds=2):
            for entity in world.entities:
                component = entity.get_component(DayComponent)
                if isinstance(component, DayComponent):
                    component.increment_day()
            self.accumulated_time -= timedelta(seconds=2)

class TimePollingSystem(System):
    """This implementation now takes advantage of Python's asynchronous
    capabilities, allowing for non-blocking I/O operations when fetching the
    current time from the API. The TimePollingSystem runs concurrently with
    other systems, demonstrating the power of async programming in this ECS
    framework."""
    async def update(self, world: World, dt: timedelta) -> None:
        async with aiohttp.ClientSession() as session:
            for entity in world.entities:
                component = entity.get_component(TimePollingComponent)
                if isinstance(component, TimePollingComponent):
                    try:
                        async with session.get("http://worldtimeapi.org/api/timezone/Australia/Melbourne") as response:
                            if response.status == 200:
                                data = await response.json()
                                component.current_time = data.get('datetime')
                    except aiohttp.ClientError as e:
                        print(f"Error polling time: {e}")

# Example Program
async def main():
    world = World()

    # Create entities
    entity1 = Entity()
    entity1.add_component(NumberComponent(0))
    entity1.add_component(DayComponent("Monday"))
    entity1.add_component(TimePollingComponent())

    entity2 = Entity()
    entity2.add_component(NumberComponent(10))
    entity2.add_component(DayComponent("Wednesday"))

    # Add entities to the world
    world.add_entity(entity1)
    world.add_entity(entity2)

    # Add systems to the world
    world.add_system(IncrementNumberSystem())
    world.add_system(IncrementDaySystem())
    world.add_system(TimePollingSystem())

    # Run the systems a few times
    for _ in range(5):
        await world.update(timedelta(seconds=1))
        
        number_component1 = entity1.get_component(NumberComponent)
        day_component1 = entity1.get_component(DayComponent)
        time_component1 = entity1.get_component(TimePollingComponent)
        number_component2 = entity2.get_component(NumberComponent)
        day_component2 = entity2.get_component(DayComponent)
        
        if isinstance(number_component1, NumberComponent) and isinstance(day_component1, DayComponent) and isinstance(time_component1, TimePollingComponent):
            print(f"Entity 1: Number = {number_component1.number}, Day = {day_component1.day}, Time = {time_component1.current_time}")
        
        if isinstance(number_component2, NumberComponent) and isinstance(day_component2, DayComponent):
            print(f"Entity 2: Number = {number_component2.number}, Day = {day_component2.day}")
        
        print("---")
        # await asyncio.sleep(1)  # Add a delay to avoid hammering the API

if __name__ == "__main__":
    asyncio.run(main())
