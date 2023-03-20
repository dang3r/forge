def is_this_a_healthy_meal(meal_description: str) -> bool:
    """Given an example meal description, return True if the meal is healthy, False otherwise.

    Example:
        - A Large Big mac and large fries -> unhealthy

    Args:
        meal_description (str): Description of the meal

    Returns:
        bool: True if the meal is healthy, False otherwise
    """
    # Initialize variables/flags
    has_vegetables = False
    has_fruits = False
    has_protein = False
    has_carbs = False
    has_fat = False

    # Check if the meal contains these components
    for component in ['vegetables', 'fruits', 'protein', 'carbs', 'fat']:
        if component in meal_description.lower():
            if component == 'vegetables':
                has_vegetables = True
            elif component == 'fruits':
                has_fruits = True
            elif component == 'protein':
                has_protein = True
            elif component == 'carbs':
                has_carbs = True
            elif component == 'fat':
                has_fat = True

    # Determine if the meal is healthy or not
    if has_vegetables and has_fruits and has_protein and has_carbs and not has_fat:
        return True
    else:
        return False
