"""
Cognitive Event Calculus for Title 18 Temporal Obligation Reasoning
====================================================================

This module extends temporal deontic logic with event-based reasoning:
- Discrete events and their temporal ordering
- Causal relationships between events and obligation states
- Event preconditions and postconditions
- Automatic detection of when obligations are triggered, due, and breached

Events relevant to Section 18 demolition:
- DemolitionApproved(property, date): Section 18 Phase II approved
- IntakeSubmitted(household, property, date): Household submits intake packet
- IntakeReceived(property_manager, household, date): PM receives intake packet
- IntakeForwarded(property_manager, pha, household, date): PM forwards intake to PHA
- CounselingDue(pha, household, deadline): HACC counseling must begin
- CounselingProvided(pha, household, date): HACC actually provided counseling
- HQSAnalysisDue(pha, property, deadline): HQS analysis must complete
- HQSAnalysisCompleted(pha, property, date): HQS analysis actually completed
- RelocationOffered(pha, household, property, date): Comparable unit offered
- MoveCompleted(household, date): Household actually moved
- EvictionFiled(court, household, date): Eviction filed (prohibited without relocation complete)

Author: Formal Logic System
Date: April 2026
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Set, Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json


# ============================================================================
# PART 1: EVENT TYPES AND ENUMS
# ============================================================================

class EventType(Enum):
    """Types of events relevant to Section 18 demolition."""
    DEMOLITION_APPROVED = "DemolitionApproved"
    INTAKE_SUBMITTED = "IntakeSubmitted"
    INTAKE_RECEIVED = "IntakeReceived"
    INTAKE_FORWARDED = "IntakeForwarded"
    COUNSELING_DUE = "CounselingDue"
    COUNSELING_PROVIDED = "CounselingProvided"
    HQS_ANALYSIS_DUE = "HQSAnalysisDue"
    HQS_ANALYSIS_COMPLETED = "HQSAnalysisCompleted"
    RELOCATION_OFFERED = "RelocationOffered"
    MOVE_COMPLETED = "MoveCompleted"
    EVICTION_FILED = "EvictionFiled"
    RAD_CLOSED = "RADClosed"
    PHASE_1_COMPLETE = "Phase1Complete"
    PHASE_2_APPROVED = "Phase2Approved"


class EventState(Enum):
    """Lifecycle states for events."""
    SCHEDULED = "scheduled"   # Event is expected to happen
    OCCURRED = "occurred"     # Event actually happened
    OVERDUE = "overdue"       # Event should have happened but hasn't
    PENDING = "pending"       # Event preconditions not yet met


# ============================================================================
# PART 2: EVENT DATACLASSES
# ============================================================================

@dataclass(frozen=True)
class Event:
    """An event in the deontic timeline."""
    type_: EventType
    actor: str              # Who caused event (entity name)
    recipient: str          # Who is affected (entity name)
    property_: str          # Property involved (if applicable)
    occurred_date: Optional[datetime] = None  # When event actually happened
    deadline: Optional[datetime] = None       # When event should happen by
    raw_event_data: str = ""  # Metadata (email, court doc, etc.)
    
    def __hash__(self):
        return hash((self.type_, self.actor, self.recipient, self.property_))
    
    def __str__(self):
        status = "occurred" if self.occurred_date else f"deadline:{self.deadline}"
        return f"{self.type_.value}(actor={self.actor}, recipient={self.recipient}, property={self.property_}, {status})"


@dataclass(frozen=True)
class EventConstraint:
    """A temporal constraint relating two events."""
    event1: Event
    event2: Event
    relation: str  # "before", "after", "coincident", "within_days"
    days_offset: int = 0
    
    def evaluates_true(self) -> bool:
        """Check if constraint is satisfied given event dates."""
        if not self.event1.occurred_date or not self.event2.occurred_date:
            return None  # Cannot evaluate without both dates
        
        if self.relation == "before":
            return self.event1.occurred_date < self.event2.occurred_date
        elif self.relation == "after":
            return self.event1.occurred_date > self.event2.occurred_date
        elif self.relation == "coincident":
            return self.event1.occurred_date == self.event2.occurred_date
        elif self.relation == "within_days":
            delta = self.event2.occurred_date - self.event1.occurred_date
            return delta.days <= self.days_offset
        
        return None


# ============================================================================
# PART 3: EVENT RULE ENGINE
# ============================================================================

@dataclass
class EventRule:
    """A rule that derives new obligations from events."""
    name: str
    event_pattern: Callable[[Event], bool]  # Predicate to match events
    derived_obligations: List[Tuple[str, str, str]]  # List of (actor, action, deadline_days)
    condition_needed: Optional[Callable[[Dict[str, Event]], bool]] = None
    
    def applies(self, event: Event, event_history: Dict[str, Event]) -> bool:
        """Check if rule applies to event and event history."""
        if not self.event_pattern(event):
            return False
        if self.condition_needed and not self.condition_needed(event_history):
            return False
        return True


class EventCalculus:
    """Main event calculus engine for obligation reasoning."""
    
    def __init__(self):
        self.events: Set[Event] = set()
        self.event_history: Dict[str, Event] = {}  # event_id -> Event
        self.constraints: Set[EventConstraint] = set()
        self.rules: List[EventRule] = []
        self.derived_obligations: Set[Tuple[str, str, datetime]] = set()
        
        # Initialize Title 18 rules
        self._setup_title18_rules()
    
    def _setup_title18_rules(self):
        """Set up inference rules for Title 18 Section 18 demolition."""
        
        # Rule 1: When Phase 2 approved, HACC gets 90-day counseling deadline
        def phase2_pattern(event):
            return event.type_ == EventType.PHASE_2_APPROVED
        
        rule1 = EventRule(
            name="Phase2CounselingDeadline",
            event_pattern=phase2_pattern,
            derived_obligations=[("HACC", "provide_counseling", 90)],
        )
        self.rules.append(rule1)
        
        # Rule 2: When intake received by PM, PM must forward to PHA within 5 days
        def intake_received_pattern(event):
            return event.type_ == EventType.INTAKE_RECEIVED
        
        rule2 = EventRule(
            name="IntakeForwardingDeadline",
            event_pattern=intake_received_pattern,
            derived_obligations=[("Quantum", "forward_intake", 5)],
        )
        self.rules.append(rule2)
        
        # Rule 3: RAD conversion → property manager inherits PHA relocation duties
        def rad_closed_pattern(event):
            return event.type_ == EventType.RAD_CLOSED
        
        rule3 = EventRule(
            name="RADSuccessorObligations",
            event_pattern=rad_closed_pattern,
            derived_obligations=[("Quantum", "facilitate_relocation", 120)],
        )
        self.rules.append(rule3)
        
        # Rule 4: If counseling not provided by deadline, breach detected
        # (This is evaluated separately in breach_detection)
    
    def add_event(self, event: Event) -> None:
        """Record an event occurrence."""
        event_id = f"{event.type_.value}_{event.actor}_{event.recipient}"
        self.events.add(event)
        self.event_history[event_id] = event
    
    def add_constraint(self, event1: Event, event2: Event, relation: str, days_offset: int = 0) -> None:
        """Add temporal constraint between events."""
        constraint = EventConstraint(event1, event2, relation, days_offset)
        self.constraints.add(constraint)
    
    def infer_obligations_from_events(self) -> Dict[str, List[Tuple[str, datetime]]]:
        """Fire rules to derive obligations from events."""
        derived = {}  # actor -> [(obligation, deadline), ...]
        
        for event in self.events:
            for rule in self.rules:
                if rule.applies(event, self.event_history):
                    for actor, obligation, days_offset in rule.derived_obligations:
                        if actor not in derived:
                            derived[actor] = []
                        
                        # Calculate deadline
                        if event.deadline:
                            deadline = event.deadline + timedelta(days=days_offset)
                        elif event.occurred_date:
                            deadline = event.occurred_date + timedelta(days=days_offset)
                        else:
                            deadline = datetime.now() + timedelta(days=days_offset)
                        
                        derived[actor].append((obligation, deadline))
                        self.derived_obligations.add((actor, obligation, deadline))
        
        return derived
    
    def detect_deadline_breaches(self, current_date: datetime) -> List[Dict[str, Any]]:
        """Find obligations with missed deadlines as of a given date."""
        breaches = []
        
        for actor, obligation, deadline in self.derived_obligations:
            if current_date > deadline:
                # Check if obligation was actually fulfilled
                # (For now, assume not fulfilled unless explicitly added as accomplished)
                breaches.append({
                    "actor": actor,
                    "obligation": obligation,
                    "deadline": deadline,
                    "detected_as_overdue_on": current_date,
                    "days_overdue": (current_date - deadline).days
                })
        
        return breaches
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize event calculus state to JSON."""
        return {
            "events": [
                {
                    "type": event.type_.value,
                    "actor": event.actor,
                    "recipient": event.recipient,
                    "property": event.property_,
                    "occurred_date": event.occurred_date.isoformat() if event.occurred_date else None,
                    "deadline": event.deadline.isoformat() if event.deadline else None,
                    "raw_event_data": event.raw_event_data
                }
                for event in self.events
            ],
            "derived_obligations": [
                {
                    "actor": actor,
                    "obligation": obligation,
                    "deadline": deadline.isoformat()
                }
                for actor, obligation, deadline in self.derived_obligations
            ]
        }


# ============================================================================
# PART 4: TITLE 18 EVENT TIMELINE INSTANTIATION
# ============================================================================

def build_title18_event_timeline() -> EventCalculus:
    """Instantiate event calculus with Title 18 case facts."""
    ec = EventCalculus()
    
    # Key dates from case record
    rad_closed = datetime(2021, 1, 1)
    phase1_complete = datetime(2024, 9, 1)
    phase2_approved = datetime(2024, 9, 19)
    counseling_deadline = phase2_approved + timedelta(days=90)  # Dec 18, 2024
    
    intake_received_date = datetime(2024, 10, 5)  # Per Ferron email
    intake_forward_deadline = intake_received_date + timedelta(days=5)  # Oct 10, 2024
    
    relocation_deadline = phase2_approved + timedelta(days=120)  # Jan 17, 2025
    
    eviction_filed = datetime(2026, 4, 5)  # Case date
    
    # Event 1: RAD conversion closed (happened in past)
    rad_event = Event(
        type_=EventType.RAD_CLOSED,
        actor="HUD",
        recipient="Quantum",
        property_="Hillside Park",
        occurred_date=rad_closed,
        raw_event_data="RAD conversion finalized per HUD PIH 2019-23"
    )
    ec.add_event(rad_event)
    
    # Event 2: Phase 2 approved
    phase2_event = Event(
        type_=EventType.PHASE_2_APPROVED,
        actor="HUD",
        recipient="HACC",
        property_="Hillside Park",
        occurred_date=phase2_approved,
        raw_event_data="Section 18 Phase 2 demolition approval"
    )
    ec.add_event(phase2_event)
    
    # Event 3: Intake submitted/received
    intake_event = Event(
        type_=EventType.INTAKE_RECEIVED,
        actor="Quantum",  # As PM, received from household
        recipient="Benjamin Barber",
        property_="Hillside Park",
        occurred_date=intake_received_date,
        deadline=intake_forward_deadline,
        raw_event_data="Intake packet received per Ferron email Oct 5 2024"
    )
    ec.add_event(intake_event)
    
    # Event 4: Counseling due (derived from Phase 2)
    counseling_due_event = Event(
        type_=EventType.COUNSELING_DUE,
        actor="HACC",
        recipient="Benjamin Barber",
        property_="Hillside Park",
        deadline=counseling_deadline,
        raw_event_data="90-day counseling deadline per 42 USC 1437p(d)(1)"
    )
    ec.add_event(counseling_due_event)
    
    # Event 5: Eviction filed (BEFORE relocation complete = violation)
    eviction_event = Event(
        type_=EventType.EVICTION_FILED,
        actor="HACC",
        recipient="Benjamin Barber",
        property_="Hillside Park",
        occurred_date=eviction_filed,
        raw_event_data="Eviction filed in Clackamas County Circuit Court"
    )
    ec.add_event(eviction_event)
    
    # Constraints: temporal relationships
    ec.add_constraint(rad_event, phase2_event, "before")
    ec.add_constraint(phase2_event, intake_event, "before")
    ec.add_constraint(intake_event, counseling_due_event, "before")
    ec.add_constraint(counseling_due_event, eviction_event, "before")
    
    return ec


# ============================================================================
# PART 5: MAIN / TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TITLE 18 EVENT CALCULUS - DEMONSTRATING OBLIGATION INFERENCE")
    print("="*80)
    
    ec = build_title18_event_timeline()
    
    print("\n[EVENTS RECORDED]")
    for event in ec.events:
        print(f"  {event}")
    
    print("\n[INFERRING OBLIGATIONS FROM EVENTS]")
    derived = ec.infer_obligations_from_events()
    for actor, obligations in derived.items():
        print(f"\n  {actor}:")
        for obligation, deadline in obligations:
            print(f"    - {obligation} by {deadline.strftime('%Y-%m-%d')}")
    
    print("\n[BREACH DETECTION (as of April 5, 2026)]")
    current_date = datetime(2026, 4, 5)
    breaches = ec.detect_deadline_breaches(current_date)
    if breaches:
        for breach in breaches:
            print(f"  ❌ {breach['actor']}: {breach['obligation']}")
            print(f"     Deadline was {breach['deadline'].strftime('%Y-%m-%d')}")
            print(f"     {breach['days_overdue']} days overdue")
    else:
        print("  No breaches detected (all deadlines met)")
    
    print("\n[SERIALIZED TO JSON]")
    print(json.dumps(ec.to_dict(), indent=2, default=str))
