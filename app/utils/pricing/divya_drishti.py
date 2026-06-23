def get_group_vr_price(total_people: int) -> dict:
    """
    Returns price per person and total price for Divya Drishti Group VR Booking.
    Minimum group size: 10 people.
    """
    print("Total People:", total_people)

    if total_people < 10:
        return {
            "error": "Minimum 10 people required for Group VR Booking.",
            "price_per_person": None,
            "total_price": None
        }

    if total_people == 10:
        price = 3000
    elif total_people <= 15:
        price = 4000
    elif total_people <= 20:
        price = 5000
    elif total_people <= 25:
        price = 6000
    elif total_people <= 30:
        price = 7000
    elif total_people <= 35:
        price = 8000
    elif total_people <= 40:
        price = 9000
    elif total_people <= 45:
        price = 10000
    elif total_people <= 50:
        price = 11000
    else:
        return {
            "error": "Group size exceeds maximum of 50 people. Please contact us.",
            "price": None,
            "total_price": None
        }

    return price