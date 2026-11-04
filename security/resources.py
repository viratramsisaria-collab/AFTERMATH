
"""Resource inventory, reservation and operating-cost controls."""

from security.models import SecurityResource


# ─────────────────────────────────────────────
# DEFAULT RESOURCE INVENTORY
# ─────────────────────────────────────────────

DEFAULT_RESOURCES = (

    (
        "RES-MED",
        "Medical Supply Kits",
        "medical",
        500,
    ),

    (
        "RES-FIR",
        "Fire Suppression Kits",
        "fire",
        250,
    ),

    (
        "RES-RES",
        "Search and Rescue Kits",
        "rescue",
        180,
    ),

    (
        "RES-ENG",
        "Infrastructure Repair Kits",
        "engineering",
        120,
    ),

    (
        "RES-EVC",
        "Evacuation Support Kits",
        "evacuation",
        300,
    ),

)


# ─────────────────────────────────────────────
# INITIALIZATION
# ─────────────────────────────────────────────

def initialize_resources(state):

    if state.resources:
        return state.resources

    for (
        resource_id,
        name,
        category,
        quantity,
    ) in DEFAULT_RESOURCES:

        resource = SecurityResource(

            id=resource_id,

            name=name,

            category=category,

            quantity=quantity,

            available_quantity=quantity,

        )

        state.resources.append(resource)

    return state.resources


# ─────────────────────────────────────────────
# RESOURCE LOOKUP
# ─────────────────────────────────────────────

def get_resource(
    state,
    resource_id: str,
):

    resource = next(
        (
            item
            for item in state.resources
            if item.id == resource_id
        ),
        None,
    )

    if resource is None:
        raise ValueError(
            f"Unknown security resource: {resource_id}"
        )

    return resource


# ─────────────────────────────────────────────
# RESOURCE RESERVATION
# ─────────────────────────────────────────────

def reserve_resource(
    state,
    resource_id: str,
    quantity: int,
):

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity < 1
    ):
        raise ValueError(
            "Resource quantity must be a positive integer."
        )

    resource = get_resource(
        state,
        resource_id,
    )

    if resource.available_quantity < quantity:
        raise ValueError(
            f"Insufficient {resource.name} available."
        )

    resource.available_quantity -= quantity

    return resource


# ─────────────────────────────────────────────
# RESOURCE RELEASE
# ─────────────────────────────────────────────

def release_resource(
    state,
    resource_id: str,
    quantity: int,
):

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity < 1
    ):
        raise ValueError(
            "Resource quantity must be a positive integer."
        )

    resource = get_resource(
        state,
        resource_id,
    )

    resource.available_quantity = min(
        resource.quantity,
        resource.available_quantity + quantity,
    )

    return resource


# ─────────────────────────────────────────────
# RESOURCE SUMMARY
# ─────────────────────────────────────────────

def resource_summary(state):

    return [

        {
            "id": resource.id,

            "name": resource.name,

            "category": resource.category,

            "quantity": resource.quantity,

            "available": resource.available_quantity,

            "deployed": (
                resource.quantity
                - resource.available_quantity
            ),

        }

        for resource in state.resources

    ]
