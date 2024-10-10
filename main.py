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
    def update(self, world: 'World', dt: timedelta) -> None:
        raise NotImplementedError

class World:
    def __init__(self) -> None:
        self.entities: List[Entity] = []
        self.systems: List[System] = []

    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def add_system(self, system: System) -> None:
        self.systems.append(system)

    def update(self, dt: timedelta) -> None:
        """Responsible for updating the state of the world and its entities. It typically iterates over all systems and calls their update methods.

        In the context of an Entity-Component-System (ECS) framework, the update method is used to advance the simulation by a certain amount of time. By passing a timedelta object, you are specifying that the simulation should advance by 1 second.
        """
        print(f"Updating world by {dt.total_seconds()} seconds")
        for system in self.systems:
            system.update(self, dt)

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

# Systems
class IncrementNumberSystem(System):
    def update(self, world: World, dt: timedelta) -> None:
        for entity in world.entities:
            component = entity.get_component(NumberComponent)
            if isinstance(component, NumberComponent):
                component.number += 1

class IncrementDaySystem(System):
    def __init__(self) -> None:
        self.accumulated_time = timedelta(0)

    def update(self, world: World, dt: timedelta) -> None:
        """how could dt be used e.g. so that days only increment every 2 seconds"""
        self.accumulated_time += dt
        if self.accumulated_time >= timedelta(seconds=2):
            for entity in world.entities:
                component = entity.get_component(DayComponent)
                if isinstance(component, DayComponent):
                    component.increment_day()
            self.accumulated_time -= timedelta(seconds=2)  # Reset the accumulated time

# Example Program
if __name__ == "__main__":
    world = World()

    # Create entities
    entity1 = Entity()
    entity1.add_component(NumberComponent(0))
    entity1.add_component(DayComponent("Monday"))

    entity2 = Entity()
    entity2.add_component(NumberComponent(10))
    entity2.add_component(DayComponent("Wednesday"))

    # Add entities to the world
    world.add_entity(entity1)
    world.add_entity(entity2)

    # Add systems to the world
    world.add_system(IncrementNumberSystem())
    world.add_system(IncrementDaySystem())

    # Run the systems a few times
for _ in range(5):
    world.update(timedelta(seconds=1))
    
    number_component1 = entity1.get_component(NumberComponent)
    day_component1 = entity1.get_component(DayComponent)
    number_component2 = entity2.get_component(NumberComponent)
    day_component2 = entity2.get_component(DayComponent)
    
    if isinstance(number_component1, NumberComponent) and isinstance(day_component1, DayComponent):
        print(f"Entity 1: Number = {number_component1.number}, Day = {day_component1.day}")
    
    if isinstance(number_component2, NumberComponent) and isinstance(day_component2, DayComponent):
        print(f"Entity 2: Number = {number_component2.number}, Day = {day_component2.day}")
    
    print("---")
