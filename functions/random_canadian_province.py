import random

def random_canadian_province():
    """Returns the name of a random province or territory in Canada."""
    provinces_and_territories = [
        'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 
        'Newfoundland and Labrador', 'Northwest Territories', 'Nova Scotia', 
        'Nunavut', 'Ontario', 'Prince Edward Island', 'Quebec', 'Saskatchewan', 
        'Yukon'
    ]

    return random.choice(provinces_and_territories)
