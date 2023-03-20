def how_many_calories_in_this_meal(meal_description: str) -> int:
    # A dictionary mapping meal descriptions to their calorie counts.
    meal_calories = {
        "A Large Big Mac and large fries": 1130,
        "Grilled chicken sandwich and salad": 320,
        "Double cheeseburger and medium fries": 890,
        "Vegetarian hummus and veggie wrap": 470,
        # Add more meal descriptions and their calorie counts as needed.
    }
    # Get the calorie count for the given meal description from the dictionary.
    return meal_calories.get(meal_description, 0)
