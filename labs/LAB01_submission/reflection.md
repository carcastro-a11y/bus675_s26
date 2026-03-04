# Reflection: OOP Design Decisions

Write 2-3 paragraphs reflecting on your object-oriented design. Some questions to consider:

- Why did you structure your classes the way you did?
- What inheritance relationships did you use and why?
- What was challenging about managing multiple interacting objects?
- If you had more time, what would you refactor or add?
- How does this experience connect to working with OOP in analytics/ML codebases?

---

# Reflection: OOP Design Decisions

## Class Structure and Inheritance Hierarchy

I structured the game around a clear inheritance hierarchy centered on the `Character` base class, which made sense because both the player and all enemies share common attributes like health, strength, defense, and the ability to attack. By creating `Player` and `Enemy` as subclasses of `Character`, I could avoid duplicating code for core mechanics like taking damage, healing, and applying infections. The `Enemy` class further branches into three specific types like, `Minion`, `Elite`, and `Boss` each with preset stats and behaviors. This design pattern mirrors real-world scenarios where you have general entities with specialized variations. I also created separate classes for `Weapon`, `Location`, and `Combat` to encapsulate their respective responsibilities, following the Single Responsibility Principle. The `Game` class serves as a controller that manages the overall game state, navigation, and user interactions. This separation made the code more maintainable.

## Challenges with Interacting Objects and State Management

The most challenging aspect was managing the complex relationships between multiple interacting objects, specifically how the `Player` navigates through `Location` objects that contain `Enemy` and `Weapon` instances, while the `Game` class orchestrates everything. For example, implementing the location traversal system required careful state tracking: I needed to distinguish between being "at an entrance" versus "inside a location's interior rooms," which affected what commands were available and whether items should be displayed. Managing this required the `in_location` boolean flag and `active_location_entrance` pointer, which was all new to me. Another challenge was the combat system: transitioning between states (player turn → enemy turn → combat end) while keeping inventory, weapons, and enemy references synchronized required meticulous state management. If I had more time, I would refactor the navigation system into a dedicated `Navigator` class to handle the complexity of directional movement and location connections, and I'd implement an event system (like callbacks or signals) so that defeating an enemy could automatically trigger loot drops without the `Game` class needing to know those low-level details. This all around kind of reminded me of the old Pokemon games where you had a chance to flee, attack, or use an item which helped me brain storm the combat system in this game.

## Connections to Analytics and ML Codebases

This experience directly parallels ML pipelines, where interconnected objects like `DataLoader`, `Model`, and `Preprocessor` need to communicate and share state. Just as I used inheritance to manage different enemy types, ML frameworks use it for model architectures. The key lesson is that as complexity grows, clear interfaces and state management are essential, I learned this when debugging why items weren't displaying or enemies weren't respawning. In production ML codebases, this means proper dependency injection, logging, and testing, since a bug in one component silently corrupts downstream results. 

---
