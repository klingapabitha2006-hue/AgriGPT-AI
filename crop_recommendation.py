# ---------------------------------------
# CROP RECOMMENDATION MODULE
# Shebixion AI
# ---------------------------------------


def recommend_crop(soil, season, water):
    """
    Basic crop recommendation based on
    soil type, season and water availability.
    """

    soil = str(soil).lower().strip()
    season = str(season).lower().strip()
    water = str(water).lower().strip()

    # ---------------------------------------
    # CLAY SOIL
    # ---------------------------------------

    if soil in ["clay", "clay soil", "clay-loam", "clay loam"]:

        if water in ["high", "good", "available"]:

            crop = "Rice"

            reason = (
                "Clay or clay-loam soil can retain water "
                "and is suitable for rice cultivation."
            )

        else:

            crop = "Millet"

            reason = (
                "Millets can be suitable when water "
                "availability is limited."
            )

    # ---------------------------------------
    # SANDY SOIL
    # ---------------------------------------

    elif soil in ["sandy", "sandy soil"]:

        if water in ["low", "limited"]:

            crop = "Groundnut"

            reason = (
                "Groundnut can perform well in lighter soils "
                "with suitable water management."
            )

        else:

            crop = "Vegetables"

            reason = (
                "Sandy soil can support several vegetable crops "
                "with proper irrigation and nutrient management."
            )

    # ---------------------------------------
    # LOAMY SOIL
    # ---------------------------------------

    elif soil in ["loamy", "loam", "loamy soil"]:

        crop = "Maize"

        reason = (
            "Loamy soil is generally suitable for many crops, "
            "including maize, when nutrients and water are "
            "managed properly."
        )

    # ---------------------------------------
    # DEFAULT
    # ---------------------------------------

    else:

        crop = "Rice"

        reason = (
            "Rice is a common crop choice when suitable "
            "water and soil conditions are available."
        )

    # ---------------------------------------
    # SEASON ADJUSTMENT
    # ---------------------------------------

    if (
        season in ["kharif", "monsoon"]
        and water in ["high", "good", "available"]
    ):

        crop = "Rice"

        reason = (
            "The monsoon season and good water availability "
            "can support rice cultivation."
        )

    # ---------------------------------------
    # RETURN RESULT
    # ---------------------------------------

    return {
        "recommended_crop": crop,
        "reason": reason,
        "soil": soil,
        "season": season,
        "water_availability": water
    }