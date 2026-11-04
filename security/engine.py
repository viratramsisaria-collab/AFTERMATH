
"""AFTERMATH Security Command Centre orchestration engine."""

from security.models import (
    UnitType,
    UnitStatus,
    IncidentType,
    IncidentStatus,
    DeploymentStatus,
    SecurityState,
    SecurityUnit,
)

from security.departments import build_departments
from security.resources import initialize_resources
from security.personnel import (
    put_on_maintenance,
    advance_personnel_recovery,
)
from security.deployment import (
    dispatch_units,
    recall_deployment,
    complete_deployment,
    advance_deployments,
)
from security.operations import (
    create_incident as create_security_incident,
    log_operation,
    incident_summary,
    recent_operations,
)
from security.effectiveness import (
    security_performance_report,
)


# ─────────────────────────────────────────────
# UNIT ROSTER
# ─────────────────────────────────────────────

UNIT_BLUEPRINTS = [
    ("POL-01", "Central Police Division", UnitType.POLICE, 42, "central"),
    ("POL-02", "District Patrol Division", UnitType.POLICE, 36, "industrial"),
    ("FIR-01", "Metropolitan Fire Service", UnitType.FIRE, 32, "commercial"),
    ("MED-01", "Emergency Medical Service", UnitType.MEDICAL, 30, "central"),
    ("RES-01", "Urban Search & Rescue", UnitType.RESCUE, 28, "waterfront"),
    ("ENG-01", "Infrastructure Response", UnitType.ENGINEERING, 22, "industrial"),
    ("EVAC-01", "Civil Evacuation Division", UnitType.EVACUATION, 24, "residential"),
]


INCIDENT_BLUEPRINTS = {
    IncidentType.CRIME: {
        "title": "Coordinated criminal activity",
        "description": "Multiple reports indicate an escalating public-safety threat.",
        "units": [UnitType.POLICE],
        "severity": (25, 65),
        "deadline": 3,
    },
    IncidentType.FIRE: {
        "title": "Structural fire emergency",
        "description": "A fire has been reported in an occupied building.",
        "units": [UnitType.FIRE, UnitType.MEDICAL],
        "severity": (35, 85),
        "deadline": 2,
    },
    IncidentType.MEDICAL: {
        "title": "Mass medical emergency",
        "description": "Emergency medical assistance is required in the district.",
        "units": [UnitType.MEDICAL, UnitType.RESCUE],
        "severity": (20, 70),
        "deadline": 2,
    },
    IncidentType.INFRASTRUCTURE: {
        "title": "Critical infrastructure failure",
        "description": "A failure threatens essential city infrastructure.",
        "units": [UnitType.ENGINEERING, UnitType.RESCUE],
        "severity": (30, 80),
        "deadline": 4,
    },
    IncidentType.PUBLIC_DISORDER: {
        "title": "Public disorder alert",
        "description": "A developing disturbance requires a coordinated response.",
        "units": [UnitType.POLICE, UnitType.MEDICAL],
        "severity": (20, 65),
        "deadline": 3,
    },
    IncidentType.DISASTER: {
        "title": "Disaster response operation",
        "description": "Emergency personnel are required for disaster response.",
        "units": [],
        "severity": (30, 90),
        "deadline": 5,
    },
}


class SecurityEngine:
    """Coordinates all security operations for a city."""

    # ─────────────────────────────────────────
    # INITIALIZATION
    # ─────────────────────────────────────────

    def initialize(self, city) -> SecurityState:
        state = city.security

        if state.initialized:
            return state

        if not city.districts:
            raise ValueError(
                "Cannot initialize security without city districts."
            )

        district_ids = {
            district.id
            for district in city.districts
        }

        # Create departments.
        state.departments = build_departments(
            district_ids
        )

        department_by_type = {
            department.unit_type: department
            for department in state.departments
        }

        # Create security units.
        for (
            unit_id,
            name,
            unit_type,
            personnel,
            home_district,
        ) in UNIT_BLUEPRINTS:

            if home_district not in district_ids:
                home_district = city.districts[0].id

            department = department_by_type.get(
                unit_type
            )

            unit = SecurityUnit(
                id=unit_id,
                name=name,
                unit_type=unit_type,
                personnel=personnel,
                available_personnel=personnel,
                home_district_id=home_district,
                department_id=(
                    department.id
                    if department
                    else None
                ),
            )

            state.units.append(unit)

            if department and unit_id not in department.unit_ids:
                department.unit_ids.append(unit_id)

        initialize_resources(state)

        state.initialized = True

        log_operation(
            state,
            city.day,
            "SYSTEM",
            "Security Command Centre initialized.",
            "SUCCESS",
        )

        city.add_event(
            "SECURITY: Security Command Centre initialized."
        )

        return state

    # ─────────────────────────────────────────
    # INCIDENT CREATION
    # ─────────────────────────────────────────

    def create_incident(
        self,
        city,
        incident_type: IncidentType,
        district_id: str,
        severity: float | None = None,
        title: str | None = None,
        description: str | None = None,
        deadline_days: int | None = None,
        population_at_risk: int = 0,
        disaster_id: str | None = None,
    ):
        self.initialize(city)

        blueprint = INCIDENT_BLUEPRINTS.get(
            incident_type
        )

        if blueprint is None:
            raise ValueError(
                "Unsupported incident type."
            )

        if severity is None:
            low, high = blueprint["severity"]
            severity = (low + high) / 2

        incident = create_security_incident(
            city=city,
            title=title or blueprint["title"],
            description=description or blueprint["description"],
            incident_type=incident_type,
            district_id=district_id,
            severity=int(round(severity)), # type: ignore
            population_at_risk=population_at_risk,
            deadline_days=deadline_days or blueprint["deadline"],
            created_by_disaster=disaster_id is not None,
            disaster_id=disaster_id,
        )

        # The incident creation helper stores response requirements
        # as strings. Convert them to the canonical enum values.
        incident.required_response = blueprint["units"]

        return incident

    # ─────────────────────────────────────────
    # STANDARD DISPATCH
    # ─────────────────────────────────────────

    def dispatch(
        self,
        city,
        incident_id: str,
        unit_ids: list[str],
        personnel_allocations: dict[str, int] | None = None,
    ):
        state = self.initialize(city)

        incident = self._get_incident(
            state,
            incident_id,
        )

        selected = [
            self._get_unit(state, unit_id)
            for unit_id in unit_ids
        ]

        supplied_types = {
            unit.unit_type
            for unit in selected
        }

        missing = (
            set(incident.required_response)
            - supplied_types
        )

        if missing:
            raise ValueError(
                "Missing required capabilities: "
                + ", ".join(
                    sorted(item.value for item in missing)
                )
            )

        deployment = dispatch_units(
            city=city,
            incident=incident,
            units=selected,
            allocations=personnel_allocations,
            arrival_days=self._travel_days(
                city,
                selected[0].home_district_id,
                incident.district_id,
            ),
            daily_cost_per_person=180 / 1,
        )

        if city.budget < deployment.daily_cost:
            recall_deployment(state, deployment)
            state.deployments.remove(deployment)
            raise ValueError(
                "Insufficient city budget for deployment."
            )

        log_operation(
            state,
            city.day,
            "DEPLOYMENT",
            f"{deployment.id}: {deployment.personnel} personnel "
            f"dispatched to {incident.title}.",
        )

        return deployment

    # ─────────────────────────────────────────
    # DISASTER RESPONSE DISPATCH
    # ─────────────────────────────────────────

    def dispatch_disaster_response(
        self,
        city,
        disaster,
        objective_id: str,
        unit_ids: list[str],
        personnel_allocations: dict[str, int] | None = None,
    ):
        state = self.initialize(city)

        if disaster.status.value not in {
            "active",
            "detected",
        }:
            raise ValueError(
                "Disaster is not accepting response deployments."
            )

        objective = next(
            (
                item
                for item in disaster.objectives
                if item.id == objective_id
            ),
            None,
        )

        if objective is None:
            raise ValueError(
                "Disaster objective not found."
            )

        if objective.is_completed:
            raise ValueError(
                "Disaster objective is already completed."
            )

        target_district = (
            objective.target_district_id
            or (
                disaster.affected_district_ids[0]
                if disaster.affected_district_ids
                else None
            )
        )

        if target_district is None:
            raise ValueError(
                "Disaster has no assigned response district."
            )

        selected = [
            self._get_unit(state, unit_id)
            for unit_id in unit_ids
        ]

        if not selected:
            raise ValueError(
                "Select at least one security unit."
            )

        from security.personnel import validate_allocations

        allocations = validate_allocations(
            selected,
            personnel_allocations,
        )

        personnel = sum(allocations.values())
        daily_cost = personnel * 220

        if city.budget < daily_cost:
            raise ValueError(
                "Insufficient budget for disaster deployment."
            )

        travel_days = self._travel_days(
            city,
            selected[0].home_district_id,
            target_district,
        )

        # A disaster deployment uses the same deployment model.
        from security.models import SecurityDeployment

        state.deployment_sequence += 1

        deployment_id = (
            f"DEP-{state.deployment_sequence:05d}"
        )

        from security.personnel import allocate_personnel

        deployment = SecurityDeployment(
            id=deployment_id,
            unit_ids=[unit.id for unit in selected],
            personnel_allocations=allocations,
            disaster_id=disaster.id,
            objective_id=objective_id,
            district_id=target_district,
            personnel=personnel,
            dispatched_day=city.day,
            arrival_day=city.day + travel_days,
            remaining_days=travel_days,
            daily_cost=daily_cost,
        )

        allocated = []

        try:
            for unit in selected:
                allocate_personnel(
                    unit,
                    allocations[unit.id],
                    deployment.id,
                )
                allocated.append(unit)

            state.deployments.append(deployment)
            state.total_deployments += 1

        except Exception:
            for unit in allocated:
                amount = allocations[unit.id]

                unit.available_personnel = min(
                    unit.personnel,
                    unit.available_personnel + amount,
                )

                if deployment.id in unit.active_deployments:
                    unit.active_deployments.remove(
                        deployment.id
                    )

                if not unit.active_deployments:
                    unit.status = UnitStatus.AVAILABLE

            raise

        log_operation(
            state,
            city.day,
            "DISASTER RESPONSE",
            f"{deployment.id}: {personnel} personnel assigned "
            f"to {disaster.title} / {objective.title}.",
        )

        return deployment

    # ─────────────────────────────────────────
    # RECALL AND MAINTENANCE
    # ─────────────────────────────────────────

    def recall(
        self,
        city,
        deployment_id: str,
    ):
        state = self.initialize(city)

        deployment = self._get_deployment(
            state,
            deployment_id,
        )

        result = recall_deployment(
            state,
            deployment,
        )

        log_operation(
            state,
            city.day,
            "RECALL",
            f"{deployment.id} recalled by command.",
        )

        return result

    def set_maintenance(
        self,
        city,
        unit_id: str,
        duration_days: int,
    ):
        state = self.initialize(city)

        unit = self._get_unit(
            state,
            unit_id,
        )

        put_on_maintenance(
            city,
            unit,
            duration_days,
        )

        log_operation(
            state,
            city.day,
            "MAINTENANCE",
            f"{unit.name} entered maintenance for "
            f"{duration_days} days.",
        )

        return unit

    # ─────────────────────────────────────────
    # DAILY SIMULATION
    # ─────────────────────────────────────────

    def advance_day(
        self,
        city,
        disasters: list | None = None,
    ) -> list[dict]:
        """Advance security operations by one simulation day.

        The simulation engine must increment city.day before
        calling this method.
        """

        state = self.initialize(city)

        reports = []

        self._generate_scheduled_incident(city)

        # Advance travel and operational costs.
        for deployment in list(state.deployments):

            if deployment.status in {
                DeploymentStatus.COMPLETED,
                DeploymentStatus.FAILED,
                DeploymentStatus.RECALLED,
            }:
                continue

            if city.budget < deployment.daily_cost:
                deployment.status = DeploymentStatus.FAILED
                deployment.failure_reason = (
                    "Insufficient operating funds."
                )

                from security.personnel import release_personnel

                release_personnel(
                    state,
                    deployment,
                )

                state.failed_operations += 1

                log_operation(
                    state,
                    city.day,
                    "FAILURE",
                    f"{deployment.id} failed: insufficient operating funds.",
                    "CRITICAL",
                )

                continue

            city.budget -= deployment.daily_cost

            deployment.total_cost += deployment.daily_cost

            state.total_operational_cost += deployment.daily_cost

            if deployment.remaining_days > 0:
                deployment.remaining_days -= 1

                deployment.status = (
                    DeploymentStatus.EN_ROUTE
                )

                if deployment.remaining_days == 0:
                    deployment.status = (
                        DeploymentStatus.ON_SCENE
                    )

                    log_operation(
                        state,
                        city.day,
                        "ARRIVAL",
                        f"{deployment.id} arrived in "
                        f"{deployment.district_id}.",
                    )

                reports.append({
                    "deployment_id": deployment.id,
                    "status": deployment.status.value,
                })

                continue

            if deployment.incident_id:
                self._advance_incident_deployment(
                    city,
                    deployment,
                )

            elif deployment.disaster_id:
                self._advance_disaster_deployment(
                    city,
                    deployment,
                    disasters or [],
                )

            reports.append({
                "deployment_id": deployment.id,
                "status": deployment.status.value,
                "progress": deployment.progress,
            })

        self._check_incident_deadlines(city)

        advance_personnel_recovery(city)

        return reports

    # ─────────────────────────────────────────
    # INCIDENT PROGRESS
    # ─────────────────────────────────────────

    def _advance_incident_deployment(
        self,
        city,
        deployment,
    ):
        state = city.security

        incident = self._get_incident(
            state,
            deployment.incident_id,
        )

        units = [
            self._get_unit(state, unit_id)
            for unit_id in deployment.unit_ids
        ]

        readiness = (
            sum(unit.readiness for unit in units)
            / len(units)
        )

        equipment = (
            sum(unit.equipment_rating for unit in units)
            / len(units)
        )

        progress = min(
            42.0,
            12.0
            + deployment.personnel * 0.12
            + readiness * 0.08
            + equipment * 0.05,
        )

        incident.response_progress = min(
            100.0,
            incident.response_progress + progress,
        )

        deployment.progress = incident.response_progress

        if incident.response_progress >= 100:
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_day = city.day

            complete_deployment(
                state,
                deployment,
            )

            state.successful_operations += 1

            city.metrics.safety = min(
                100,
                city.metrics.safety
                + incident.severity * 0.06,
            )

            city.metrics.public_wellbeing = min(
                100,
                city.metrics.public_wellbeing + 1.0,
            )

            district = self._get_district(
                city,
                incident.district_id,
            )

            district.safety = min(
                100,
                district.safety + 2,
            )

            log_operation(
                state,
                city.day,
                "RESOLVED",
                f"{incident.title} successfully resolved.",
                "SUCCESS",
            )

    # ─────────────────────────────────────────
    # DISASTER PROGRESS
    # ─────────────────────────────────────────

    def _advance_disaster_deployment(
        self,
        city,
        deployment,
        disasters,
    ):
        state = city.security

        disaster = next(
            (
                item
                for item in disasters
                if item.id == deployment.disaster_id
            ),
            None,
        )

        if disaster is None:
            deployment.status = DeploymentStatus.FAILED
            deployment.failure_reason = (
                "Linked disaster could not be found."
            )

            from security.personnel import release_personnel

            release_personnel(
                state,
                deployment,
            )

            state.failed_operations += 1

            log_operation(
                state,
                city.day,
                "FAILURE",
                f"{deployment.id}: linked disaster could not be found.",
                "CRITICAL",
            )

            return

        from disasters.response import DisasterResponseEngine

        units = [
            self._get_unit(state, unit_id)
            for unit_id in deployment.unit_ids
        ]

        readiness = (
            sum(unit.readiness for unit in units)
            / len(units)
        )

        equipment = (
            sum(unit.equipment_rating for unit in units)
            / len(units)
        )

        progress = min(
            40.0,
            10.0
            + deployment.personnel * 0.10
            + readiness * 0.07
            + equipment * 0.05,
        )

        try:
            result = DisasterResponseEngine().apply_progress(
                disaster=disaster,
                objective_id=deployment.objective_id,
                progress=progress,
                current_day=city.day,
            )

        except (ValueError, RuntimeError) as exc:
            deployment.status = DeploymentStatus.FAILED
            deployment.failure_reason = str(exc)

            from security.personnel import release_personnel

            release_personnel(
                state,
                deployment,
            )

            state.failed_operations += 1

            log_operation(
                state,
                city.day,
                "DISASTER RESPONSE",
                f"{deployment.id} failed: {exc}",
                "WARNING",
            )

            return

        deployment.progress = result.current_progress

        if result.objective_completed:
            complete_deployment(
                state,
                deployment,
            )

            state.successful_operations += 1

            log_operation(
                state,
                city.day,
                "DISASTER RESPONSE",
                f"{deployment.id} completed objective "
                f"{deployment.objective_id}.",
                "SUCCESS",
            )

        else:
            deployment.status = DeploymentStatus.ON_SCENE

            log_operation(
                state,
                city.day,
                "DISASTER RESPONSE",
                f"{deployment.id} advanced objective "
                f"{deployment.objective_id} to "
                f"{result.current_progress:.1f}%.",
            )

        if result.disaster_contained:
            log_operation(
                state,
                city.day,
                "DISASTER CONTAINED",
                f"{disaster.title} has been successfully contained.",
                "SUCCESS",
            )

    # ─────────────────────────────────────────
    # INCIDENT DEADLINES
    # ─────────────────────────────────────────

    def _check_incident_deadlines(self, city):
        state = city.security

        for incident in state.incidents:

            if incident.status not in {
                IncidentStatus.DETECTED,
                IncidentStatus.ACTIVE,
            }:
                continue

            if city.day <= incident.deadline_day:
                continue

            incident.status = IncidentStatus.FAILED

            state.failed_operations += 1

            city.metrics.safety = max(
                0,
                city.metrics.safety
                - incident.severity * 0.08,
            )

            city.metrics.public_wellbeing = max(
                0,
                city.metrics.public_wellbeing
                - incident.severity * 0.04,
            )

            district = self._get_district(
                city,
                incident.district_id,
            )

            district.safety = max(
                0,
                district.safety - 4,
            )

            district.stress = min(
                100,
                district.stress + 5,
            )

            for deployment in state.deployments:

                if (
                    deployment.incident_id == incident.id
                    and deployment.status in {
                        DeploymentStatus.DISPATCHED,
                        DeploymentStatus.EN_ROUTE,
                        DeploymentStatus.ON_SCENE,
                    }
                ):

                    deployment.status = DeploymentStatus.FAILED

                    deployment.failure_reason = (
                        "Incident response deadline exceeded."
                    )

                    from security.personnel import release_personnel

                    release_personnel(
                        state,
                        deployment,
                    )

            log_operation(
                state,
                city.day,
                "FAILED",
                f"Response deadline missed: {incident.title}.",
                "CRITICAL",
            )

    # ─────────────────────────────────────────
    # SCHEDULED INCIDENT GENERATION
    # ─────────────────────────────────────────

    def _generate_scheduled_incident(self, city):
        state = city.security

        if city.day < state.next_incident_day:
            return

        if state.active_incidents >= 3:
            state.next_incident_day = city.day + 3
            return

        if not city.districts:
            return

        incident_types = list(IncidentType)[:-1]

        incident_type = incident_types[
            (city.seed + state.incident_sequence)
            % len(incident_types)
        ]

        district = min(
            city.districts,
            key=lambda item: (
                item.safety,
                item.id,
            ),
        )

        blueprint = INCIDENT_BLUEPRINTS[incident_type]

        low, high = blueprint["severity"]

        severity = low + (
            city.seed * 7
            + state.incident_sequence * 13
        ) % (high - low + 1)

        self.create_incident(
            city,
            incident_type,
            district.id,
            severity=float(severity),
            population_at_risk=round(
                district.population
                * severity
                / 100
                * 0.08
            ),
        )

        state.next_incident_day = city.day + 7

    # ─────────────────────────────────────────
    # REPORTING
    # ─────────────────────────────────────────

    def get_dashboard(self, city):
        state = self.initialize(city)

        return {
            "personnel": {
                "total": state.total_personnel,
                "available": state.available_personnel,
                "deployed": (
                    state.total_personnel
                    - state.available_personnel
                ),
            },
            "incidents": incident_summary(state),
            "performance": security_performance_report(state),
            "active_deployments": [
                deployment.model_dump(mode="json")
                for deployment in state.deployments
                if deployment.status in {
                    DeploymentStatus.DISPATCHED,
                    DeploymentStatus.EN_ROUTE,
                    DeploymentStatus.ON_SCENE,
                }
            ],
            "recent_operations": [
                entry.model_dump(mode="json")
                for entry in recent_operations(state)
            ],
            "resources": [
                resource.model_dump(mode="json")
                for resource in state.resources
            ],
        }

    # ─────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────

    @staticmethod
    def _get_unit(state, unit_id):
        unit = next(
            (
                item
                for item in state.units
                if item.id == unit_id
            ),
            None,
        )

        if unit is None:
            raise ValueError(
                f"Unknown security unit: {unit_id}."
            )

        return unit

    @staticmethod
    def _get_incident(state, incident_id):
        incident = next(
            (
                item
                for item in state.incidents
                if item.id == incident_id
            ),
            None,
        )

        if incident is None:
            raise ValueError(
                f"Unknown security incident: {incident_id}."
            )

        return incident

    @staticmethod
    def _get_deployment(state, deployment_id):
        deployment = next(
            (
                item
                for item in state.deployments
                if item.id == deployment_id
            ),
            None,
        )

        if deployment is None:
            raise ValueError(
                f"Unknown security deployment: {deployment_id}."
            )

        return deployment

    @staticmethod
    def _get_district(city, district_id):
        district = next(
            (
                item
                for item in city.districts
                if item.id == district_id
            ),
            None,
        )

        if district is None:
            raise ValueError(
                f"Unknown district: {district_id}."
            )

        return district

    @staticmethod
    def _travel_days(
        city,
        source_id,
        target_id,
    ):
        source = next(
            (
                item
                for item in city.districts
                if item.id == source_id
            ),
            None,
        )

        target = next(
            (
                item
                for item in city.districts
                if item.id == target_id
            ),
            None,
        )

        if source is None or target is None:
            return 1

        distance = (
            abs(source.center_lat - target.center_lat)
            + abs(source.center_lon - target.center_lon)
        )

        return min(
            2,
            round(distance * 10),
        )
