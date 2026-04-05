"""
Temporal Deontic First-Order Logic for Title 18 (Section 18) Demolition Obligations
====================================================================================

This module implements a formal logic system to reason about:
- Temporal constraints (when obligations arise, expire, must be satisfied)
- Deontic modalities (obligation, permission, prohibition)
- First-order predicates for legal entities, actions, and facts
- Automatic computation of what each party owes to whom

Parties: Benjamin Barber, Jane Cortez, HACC, Quantum Residential, HUD
Core Obligation Model: HACC must comply with 42 USC 1437p (Section 18)

Author: Formal Logic System for HACC v. Barber/Cortez
Date: April 5, 2026
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Set, Dict, List, Tuple, Optional, Any, FrozenSet
from datetime import datetime, timedelta
import json
from abc import ABC, abstractmethod


# ============================================================================
# PART 1: TEMPORAL & DEONTIC OPERATORS
# ============================================================================

class DeonticModality(Enum):
    """Deontic modalities in temporal deontic logic."""
    OBLIGATORY = "O"      # Must do / is obligated to do
    PERMITTED = "P"       # May do / is permitted to do
    PROHIBITED = "◇"      # Must not do / is forbidden to do
    OPTIONAL = "◆"        # May or may not do / is optional


class TemporalOperator(Enum):
    """Allen temporal relations for ordering events."""
    BEFORE = "Before"                # e1 before e2
    AFTER = "After"                  # e1 after e2
    COINCIDENT = "Coincident"        # e1 at same time as e2
    DURING = "During"                # e1 during e2
    OVERLAPS = "Overlaps"            # e1 overlaps with e2
    STARTS = "Starts"                # e1 starts e2
    FINISHES = "Finishes"            # e1 finishes e2
    EQUALS = "Equals"                # e1 equals e2


class LogicalOperator(Enum):
    """Standard first-order logical connectives."""
    AND = "∧"
    OR = "∨"
    NOT = "¬"
    IMPLIES = "→"
    IFF = "↔"
    FORALL = "∀"
    EXISTS = "∃"


# ============================================================================
# PART 2: BASE ENTITIES & TYPES
# ============================================================================

@dataclass(frozen=True)
class TimeInterval:
    """Represents a time interval with optional bounds."""
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    duration_days: Optional[int] = None

    def resolved_end(self) -> Optional[datetime]:
        if self.end is not None:
            return self.end
        if self.start is not None and self.duration_days is not None:
            return self.start + timedelta(days=self.duration_days)
        return None

    def contains(self, at_time: datetime) -> bool:
        resolved_end = self.resolved_end()
        if self.start is not None and at_time < self.start:
            return False
        if resolved_end is not None and at_time > resolved_end:
            return False
        return True
    
    def __str__(self):
        resolved_end = self.resolved_end()
        if self.start and resolved_end:
            return f"[{self.start.date()} to {resolved_end.date()}]"
        elif self.duration_days:
            return f"{self.duration_days} days from start"
        else:
            return "unbounded"


@dataclass(frozen=True)
class Party:
    """Represents a legal entity/party."""
    name: str
    role: str  # e.g., "PHA", "Resident", "Property Manager", "Federal Agency"
    entity_id: str
    
    def __str__(self):
        return f"{self.name} ({self.role})"
    
    def __hash__(self):
        return hash((self.name, self.role, self.entity_id))
    
    def __eq__(self, other):
        if not isinstance(other, Party):
            return False
        return self.entity_id == other.entity_id


@dataclass(frozen=True)
class Action:
    """Represents an action/event that can be obligated, permitted, or prohibited."""
    verb: str  # e.g., "provide", "complete", "pay", "refuse"
    object_noun: str  # e.g., "relocation counseling", "intake packet", "moving expenses"
    action_id: str
    
    def __str__(self):
        return f"{self.verb} {self.object_noun}"
    
    def __hash__(self):
        return hash(self.action_id)


@dataclass(frozen=True)
class DeonticStatement:
    """
    Core unit of deontic logic: expresses what a party must do, may do, or must not do.
    
    Syntax: [Modality](Actor, Action, Recipient, TimeInterval, Condition)
    
    Example: O(HACC, provide_relocation_counseling, Barber/Cortez, before_90_days, true)
    Meaning: "HACC is obligated to provide relocation counseling to Barber/Cortez 
             before 90 days from now, unconditionally"
    """
    modality: DeonticModality
    actor: Party  # Who must/may do it
    action: Action  # What must/may be done
    recipient: Optional[Party] = None  # To whom (optional)
    time_interval: Optional[TimeInterval] = None  # When must/may it be done
    condition: Optional['Proposition'] = None  # Under what condition
    
    def __str__(self):
        recipient_str = f" to {self.recipient}" if self.recipient else ""
        time_str = f" {self.time_interval}" if self.time_interval else ""
        cond_str = f" when {self.condition}" if self.condition else ""
        return f"{self.modality.value}({self.actor}, {self.action}{recipient_str}{time_str}{cond_str})"
    
    def __hash__(self):
        return hash((self.modality, self.actor, self.action, self.recipient, 
                    self.time_interval, str(self.condition)))


# ============================================================================
# PART 3: PROPOSITIONS & FACTS (First-Order Logic)
# ============================================================================

class Proposition(ABC):
    """Base class for logical propositions."""
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def evaluate(self, model: Dict[str, Any]) -> bool:
        """Evaluate proposition in given model/context."""
        pass


@dataclass(frozen=True)
class Predicate(Proposition):
    """First-order predicate: Pred(arg1, arg2, ...)"""
    name: str
    args: Tuple[Any, ...] = field(default_factory=tuple)
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.name}({args_str})"
    
    def __hash__(self):
        return hash((self.name, self.args))
    
    def evaluate(self, model: Dict[str, Any]) -> bool:
        # Simplified evaluation - in full system would use knowledge base
        key = str(self)
        return model.get(key, False)


@dataclass(frozen=True)
class Conjunction(Proposition):
    """Logical AND of propositions."""
    left: Proposition
    right: Proposition
    
    def __str__(self):
        return f"({self.left} ∧ {self.right})"
    
    def __hash__(self):
        return hash(("AND", self.left, self.right))
    
    def evaluate(self, model: Dict[str, Any]) -> bool:
        return self.left.evaluate(model) and self.right.evaluate(model)


@dataclass(frozen=True)
class Disjunction(Proposition):
    """Logical OR of propositions."""
    left: Proposition
    right: Proposition
    
    def __str__(self):
        return f"({self.left} ∨ {self.right})"
    
    def __hash__(self):
        return hash(("OR", self.left, self.right))
    
    def evaluate(self, model: Dict[str, Any]) -> bool:
        return self.left.evaluate(model) or self.right.evaluate(model)


@dataclass(frozen=True)
class Negation(Proposition):
    """Logical NOT of proposition."""
    prop: Proposition
    
    def __str__(self):
        return f"¬({self.prop})"
    
    def __hash__(self):
        return hash(("NOT", self.prop))
    
    def evaluate(self, model: Dict[str, Any]) -> bool:
        return not self.prop.evaluate(model)


@dataclass(frozen=True)
class Implication(Proposition):
    """Logical implication."""
    antecedent: Proposition
    consequent: Proposition
    
    def __str__(self):
        return f"({self.antecedent} → {self.consequent})"
    
    def __hash__(self):
        return hash(("IMPLIES", self.antecedent, self.consequent))
    
    def evaluate(self, model: Dict[str, Any]) -> bool:
        # Material implication: false only when antecedent true and consequent false
        return not self.antecedent.evaluate(model) or self.consequent.evaluate(model)


# ============================================================================
# PART 4: DEONTIC KNOWLEDGE BASE
# ============================================================================

class DeonticKnowledgeBase:
    """
    Stores and manages deontic statements (obligations, permissions, prohibitions).
    Implements Horn clause reasoning and deontic logic inference.
    """
    
    def __init__(self):
        self.statements: Set[DeonticStatement] = set()
        self.rules: List[Tuple[Proposition, DeonticStatement]] = []  # condition -> obligation
        self.facts: Dict[str, bool] = {}  # Ground facts
        self.derived_obligations: Set[DeonticStatement] = set()
    
    def add_statement(self, stmt: DeonticStatement) -> None:
        """Add (register) a deontic statement."""
        self.statements.add(stmt)
    
    def add_rule(self, condition: Proposition, obligation: DeonticStatement) -> None:
        """
        Add a deontic rule: if condition holds, then obligation applies.
        Example: if demolition_approved(HACC) then O(HACC, provide_relocation_counseling, ...)
        """
        self.rules.append((condition, obligation))
    
    def add_fact(self, fact_str: str, value: bool = True) -> None:
        """Register a fact."""
        self.facts[fact_str] = value
    
    def infer_obligations(self) -> Set[DeonticStatement]:
        """
        Apply modus ponens to infer obligations from rules.
        Returns set of all derived obligations.
        """
        derived = set(self.statements)
        changed = True
        
        while changed:
            changed = False
            for condition, obligation in self.rules:
                if condition.evaluate(self.facts) and obligation not in derived:
                    derived.add(obligation)
                    changed = True
        
        self.derived_obligations = derived
        return derived
    
    def get_obligations_for_party(self, party: Party) -> Set[DeonticStatement]:
        """Get all obligations binding on a specific party (as actor)."""
        return {stmt for stmt in self.derived_obligations 
                if stmt.modality == DeonticModality.OBLIGATORY and stmt.actor == party}
    
    def get_obligations_to_party(self, party: Party) -> Set[DeonticStatement]:
        """Get all obligations owed to a specific party (as recipient)."""
        return {stmt for stmt in self.derived_obligations 
                if stmt.modality == DeonticModality.OBLIGATORY and stmt.recipient == party}
    
    def get_permissions_for_party(self, party: Party) -> Set[DeonticStatement]:
        """Get all permissions granted to a specific party."""
        return {stmt for stmt in self.derived_obligations 
                if stmt.modality == DeonticModality.PERMITTED and stmt.actor == party}
    
    def get_prohibitions_on_party(self, party: Party) -> Set[DeonticStatement]:
        """Get all prohibitions binding on a specific party."""
        return {stmt for stmt in self.derived_obligations 
                if stmt.modality == DeonticModality.PROHIBITED and stmt.actor == party}
    
    def check_compliance(self, party: Party, action: Action, 
                        at_time: datetime) -> Tuple[bool, str]:
        """
        Check if party's action at time is compliant with obligations/prohibitions.
        Returns (is_compliant, reason)
        """
        obligations = self.get_obligations_for_party(party)
        prohibitions = self.get_prohibitions_on_party(party)
        
        # Check if obligated action is being performed
        for obligation in obligations:
            if obligation.action == action:
                if obligation.time_interval:
                    if obligation.time_interval.contains(at_time):
                        return (True, f"Complying with {obligation}")
                else:
                    return (True, f"Complying with {obligation}")
        
        # Check if prohibited action is being performed
        for prohibition in prohibitions:
            if prohibition.action == action:
                return (False, f"Violating prohibition: {prohibition}")
        
        return (True, "Action not obligated or prohibited")
    
    def to_dict(self) -> Dict:
        """Serialize knowledge base to dictionary."""
        return {
            "statements": [str(stmt) for stmt in self.statements],
            "derived_obligations": [str(stmt) for stmt in self.derived_obligations],
            "facts": self.facts
        }


# ============================================================================
# PART 5: TITLE 18 OBLIGATION SYSTEM (INSTANTIATION)
# ============================================================================

def build_title18_deontic_system() -> DeonticKnowledgeBase:
    """
    Constructs the complete deontic logic system for Title 18 (Section 18)
    demolition and relocation obligations.
    
    Reference: 42 USC 1437p(d)
    """
    kb = DeonticKnowledgeBase()
    
    # === DEFINE PARTIES ===
    barber_cortez = Party(
        name="Benjamin Barber & Jane Cortez",
        role="Resident",
        entity_id="resident:barber_cortez"
    )
    hacc = Party(
        name="Housing Authority of Clackamas County",
        role="PHA",
        entity_id="pha:hacc"
    )
    quantum = Party(
        name="Quantum Residential Property Management",
        role="Property Manager",
        entity_id="pm:quantum"
    )
    hud = Party(
        name="Department of Housing and Urban Development",
        role="Federal Agency",
        entity_id="federal:hud"
    )
    
    # === DEFINE ACTIONS ===
    action_relocation_counseling = Action(
        verb="provide",
        object_noun="relocation counseling",
        action_id="action:reloc_counsel"
    )
    action_hqs_analysis = Action(
        verb="complete",
        object_noun="HQS comparability analysis",
        action_id="action:hqs_analysis"
    )
    action_moving_expenses = Action(
        verb="pay or commit to pay",
        object_noun="relocation moving expenses",
        action_id="action:moving_expenses"
    )
    action_resident_consultation = Action(
        verb="conduct",
        object_noun="resident consultation re: relocation",
        action_id="action:consultation"
    )
    action_furnish_comparable_unit = Action(
        verb="furnish or offer",
        object_noun="comparable housing unit",
        action_id="action:comparable_unit"
    )
    action_accessible_unit = Action(
        verb="provide",
        object_noun="accessible housing (disability accommodation)",
        action_id="action:accessible"
    )
    action_intake_processing = Action(
        verb="process and forward",
        object_noun="resident intake packet",
        action_id="action:intake_process"
    )
    action_relocation_completion = Action(
        verb="complete",
        object_noun="household relocation",
        action_id="action:reloc_completion"
    )
    
    # === CORE TITLE 18 OBLIGATIONS ===
    # Per 42 USC 1437p(d), before demolition/disposition:
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=hacc,
        action=action_resident_consultation,
        recipient=barber_cortez,
        time_interval=TimeInterval(
            start=datetime(2024, 9, 19),  # Phase II approved
            duration_days=90
        ),
        condition=Predicate("section18_phase2_approved", (hacc,))
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=hacc,
        action=action_relocation_counseling,
        recipient=barber_cortez,
        time_interval=TimeInterval(
            start=datetime(2024, 9, 19),
            duration_days=90
        ),
        condition=Predicate("section18_phase2_approved", (hacc,))
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=hacc,
        action=action_hqs_analysis,
        recipient=barber_cortez,
        time_interval=TimeInterval(
            start=datetime(2024, 9, 19),
            duration_days=90
        ),
        condition=Predicate("section18_phase2_approved", (hacc,))
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=hacc,
        action=action_moving_expenses,
        recipient=barber_cortez,
        time_interval=TimeInterval(start=datetime(2024, 9, 19)),
        condition=Predicate("section18_phase2_approved", (hacc,))
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=hacc,
        action=action_furnish_comparable_unit,
        recipient=barber_cortez,
        time_interval=TimeInterval(
            start=datetime(2024, 9, 19),
            duration_days=120
        ),
        condition=Conjunction(
            Predicate("section18_phase2_approved", (hacc,)),
            Predicate("ready_to_relocate", (barber_cortez,))
        )
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=hacc,
        action=action_accessible_unit,
        recipient=barber_cortez,
        time_interval=TimeInterval(
            start=datetime(2024, 9, 19),
            duration_days=120
        ),
        condition=Conjunction(
            Predicate("section18_phase2_approved", (hacc,)),
            Predicate("disability_accommodation_needed", (barber_cortez,))
        )
    ))
    
    # === QUANTUM'S RAD SUCCESSOR OBLIGATIONS (PIH 2019-23) ===
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=quantum,
        action=action_intake_processing,
        recipient=barber_cortez,
        time_interval=TimeInterval(duration_days=5),  # Timely processing
        condition=Conjunction(
            Predicate("rad_conversion_closed", (quantum,)),
            Predicate("intake_packet_received", (quantum, barber_cortez))
        )
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=quantum,
        action=Action(
            verb="cooperate and coordinate",
            object_noun="with HACC on relocation",
            action_id="action:reloc_cooperation"
        ),
        recipient=hacc,
        time_interval=TimeInterval(start=datetime(2021, 1, 1)),  # RAD conversion date
        condition=Predicate("rad_successor_property_manager", (quantum,))
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=quantum,
        action=action_relocation_completion,
        recipient=barber_cortez,
        time_interval=TimeInterval(
            start=datetime(2024, 9, 19),
            duration_days=120
        ),
        condition=Conjunction(
            Predicate("rad_successor_property_manager", (quantum,)),
            Predicate("household_displaced_from_rad_property", (barber_cortez, quantum))
        )
    ))
    
    # === HUD OVERSIGHT OBLIGATIONS ===
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=hud,
        action=Action(
            verb="approve",
            object_noun="Section 18 Phase II relocation plan",
            action_id="action:hud_approval"
        ),
        recipient=hacc,
        time_interval=TimeInterval(duration_days=60),
        condition=Predicate("section18_phase1_complete", (hacc,))
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.OBLIGATORY,
        actor=hud,
        action=Action(
            verb="monitor and enforce",
            object_noun="Section 18 relocation compliance",
            action_id="action:hud_monitor"
        ),
        recipient=hacc,
        time_interval=TimeInterval(start=datetime(2024, 9, 19)),
        condition=Predicate("section18_phase2_approved", (hacc,))
    ))
    
    # === RESIDENT RIGHTS & PERMISSIONS ===
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.PERMITTED,
        actor=barber_cortez,
        action=Action(
            verb="refuse",
            object_noun="inferior housing offers",
            action_id="action:refuse_inferior"
        ),
        recipient=None,
        condition=Predicate("not_hqs_comparable", (barber_cortez,))
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.PERMITTED,
        actor=barber_cortez,
        action=Action(
            verb="remain in",
            object_noun="current unit under right-to-return",
            action_id="action:right_to_return"
        ),
        recipient=None,
        condition=Conjunction(
            Predicate("rad_successor_property_manager", (quantum,)),
            Predicate("pih_2019_23_applies", (quantum,))
        )
    ))
    
    # === PROHIBITIONS ON NON-COMPLIANCE ===
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.PROHIBITED,
        actor=hacc,
        action=Action(
            verb="proceed with",
            object_noun="eviction before relocation complete",
            action_id="action:premature_eviction"
        ),
        recipient=None,
        condition=Conjunction(
            Predicate("section18_phase2_approved", (hacc,)),
            Negation(Predicate("relocation_completed", (barber_cortez,)))
        )
    ))
    
    kb.add_statement(DeonticStatement(
        modality=DeonticModality.PROHIBITED,
        actor=quantum,
        action=Action(
            verb="interfere with or obstruct",
            object_noun="resident intake and relocation",
            action_id="action:intake_obstruction"
        ),
        recipient=None,
        condition=Predicate("rad_successor_property_manager", (quantum,))
    ))
    
    # === FACTS (GROUND TRUTH FROM CASE) ===
    kb.add_fact("section18_phase2_approved(hacc)", True)
    kb.add_fact("section18_phase2_approved_date", True)  # Sept 19, 2024
    kb.add_fact("rad_conversion_closed(quantum)", True)
    kb.add_fact("rad_conversion_date", True)  # Jan 1, 2021
    kb.add_fact("rad_successor_property_manager(quantum)", True)
    kb.add_fact("pih_2019_23_applies(quantum)", True)
    kb.add_fact("household_displaced_from_rad_property(barber_cortez, quantum)", True)
    kb.add_fact("disability_accommodation_needed(barber_cortez)", True)  # 3rd floor inaccessible
    kb.add_fact("intake_packet_received(quantum, barber_cortez)", True)  # Per Ferron email
    kb.add_fact("relocation_counseling_not_provided(hacc)", True)  # As of Apr 5, 2026
    kb.add_fact("hqs_analysis_not_completed(hacc)", True)
    kb.add_fact("moving_expenses_not_committed(hacc)", True)
    kb.add_fact("relocation_completed(barber_cortez)", False)  # Still in eviction action
    kb.add_fact("ready_to_relocate(barber_cortez)", True)  # Has applied, submitted intake
    
    return kb


# ============================================================================
# PART 6: OBLIGATION INFERENCE & ANALYSIS
# ============================================================================

def infer_all_obligations(kb: DeonticKnowledgeBase) -> Dict[str, Set[str]]:
    """
    Compute all obligations for each party.
    Returns dict mapping party name -> set of obligation descriptions.
    """
    all_obligations = kb.infer_obligations()
    
    party_obligations = {}
    
    # Group by actor
    for party_name in ["Benjamin Barber & Jane Cortez", "Housing Authority of Clackamas County",
                       "Quantum Residential Property Management", "Department of Housing and Urban Development"]:
        party_obligations[f"{party_name} (must do)"] = set()
        party_obligations[f"{party_name} (may do)"] = set()
        party_obligations[f"{party_name} (must not do)"] = set()
    
    for obligation in all_obligations:
        if obligation.modality == DeonticModality.OBLIGATORY:
            key = f"{obligation.actor.name} (must do)"
        elif obligation.modality == DeonticModality.PERMITTED:
            key = f"{obligation.actor.name} (may do)"
        elif obligation.modality == DeonticModality.PROHIBITED:
            key = f"{obligation.actor.name} (must not do)"
        else:
            continue
        
        party_obligations[key].add(str(obligation))
    
    return party_obligations


# ============================================================================
# PART 7: BREACH DETECTION
# ============================================================================

def detect_breaches(kb: DeonticKnowledgeBase, current_date: datetime = None) -> List[str]:
    """
    Detects breaches of obligations.
    Returns list of breach descriptions.
    """
    if current_date is None:
        current_date = datetime(2026, 4, 5)  # Case date
    
    breaches = []
    
    hacc = Party(name="Housing Authority of Clackamas County", role="PHA", entity_id="pha:hacc")
    quantum = Party(name="Quantum Residential Property Management", role="Property Manager", 
                   entity_id="pm:quantum")
    barber_cortez = Party(name="Benjamin Barber & Jane Cortez", role="Resident", 
                        entity_id="resident:barber_cortez")
    
    # Check HACC obligations
    hacc_obligations = kb.get_obligations_for_party(hacc)
    for obligation in hacc_obligations:
        if obligation.time_interval:
            resolved_end = obligation.time_interval.resolved_end()
            if resolved_end and current_date > resolved_end:
                # Check if obligation was fulfilled
                if obligation.action.verb == "provide" and \
                   f"{obligation.action.object_noun}_not_provided(hacc)" in kb.facts and \
                   kb.facts.get(f"{obligation.action.object_noun}_not_provided(hacc)", False):
                    breaches.append(
                        f"BREACH by HACC: Failed to {obligation.action} to {obligation.recipient} "
                        f"by {resolved_end.date()}"
                    )
    
    # Check Quantum obligations
    quantum_obligations = kb.get_obligations_for_party(quantum)
    for obligation in quantum_obligations:
        if "intake" in obligation.action.object_noun.lower():
            if kb.facts.get("intake_packet_received(quantum, barber_cortez)", False):
                breaches.append(
                    f"BREACH by Quantum: Failed to {obligation.action} despite receipt of intake packet"
                )
    
    return breaches


if __name__ == "__main__":
    # Build and test the system
    kb = build_title18_deontic_system()
    kb.infer_obligations()
    
    print("=" * 80)
    print("TITLE 18 DEONTIC LOGIC SYSTEM - OBLIGATION ANALYSIS")
    print("=" * 80)
    print()
    
    obligations = infer_all_obligations(kb)
    for party, obls in obligations.items():
        if obls:
            print(f"\n{party.upper()}:")
            print("-" * 40)
            for obl in sorted(obls):
                print(f"  • {obl}")
    
    print("\n" + "=" * 80)
    print("BREACH ANALYSIS (as of April 5, 2026):")
    print("=" * 80)
    breaches = detect_breaches(kb)
    for breach in breaches:
        print(f"⚠️  {breach}")
    
    print("\n" + "=" * 80)
    print("SERIALIZED KNOWLEDGE BASE:")
    print("=" * 80)
    print(json.dumps(kb.to_dict(), indent=2, default=str))
