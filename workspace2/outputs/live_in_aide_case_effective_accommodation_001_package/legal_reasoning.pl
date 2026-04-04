% legal_reasoning.pl
% Prototype rule set for live-in aide reasonable accommodation analysis

% ---------- Facts ----------
tenant(mother).
disabled(mother).
needs_live_in_aide(mother).

person(aide).
live_in_aide(aide).
live_in_aide_for(aide, mother).

housing_authority(ha1).

room(living1).
living_room(living1).
shared_space(living1).

room(bed1).
bedroom(bed1).


requested(mother, separate_bedroom_for(aide)).
medical_verification(mother, separate_bedroom_for(aide)).
approved_in_principle(ha1, live_in_aide_status(aide, mother)).
works_remotely(aide).

% Optional harms

% ---------- Derived factual harms ----------
sleep_interruption(A) :-
    sleeps_in(A, R),
    living_room(R),
    shared_space(R),
    live_in_aide_for(A, T),
    night_access_needed(T, R).

work_interference(A) :-
    works_remotely(A),
    sleep_interruption(A).

caregiving_impairment(A) :-
    sleep_interruption(A).

privacy_loss(A) :-
    sleeps_in(A, R),
    living_room(R),
    shared_space(R).

% ---------- Legal elements ----------
medically_supported(separate_bedroom_for(A)) :-
    live_in_aide_for(A, T),
    medical_verification(T, separate_bedroom_for(A)).

necessary(separate_bedroom_for(A)) :-
    sleep_interruption(A).

necessary(separate_bedroom_for(A)) :-
    work_interference(A).

necessary(separate_bedroom_for(A)) :-
    caregiving_impairment(A).

necessary(separate_bedroom_for(A)) :-
    privacy_loss(A).

reasonable(separate_bedroom_for(A), HA) :-
    medically_supported(separate_bedroom_for(A)),
    necessary(separate_bedroom_for(A)),
    not undue_burden(HA, separate_bedroom_for(A)),
    not fundamental_alteration(HA, separate_bedroom_for(A)).

duty_to_grant(HA, separate_bedroom_for(A)) :-
    requested(T, separate_bedroom_for(A)),
    live_in_aide_for(A, T),
    disabled(T),
    needs_live_in_aide(T),
    reasonable(separate_bedroom_for(A), HA).

effective(separate_bedroom_for(A)) :-
    not denied(ha1, separate_bedroom_for(A)),
    not sleep_interruption(A).

not_effective(separate_bedroom_for(A)) :-
    denied(ha1, separate_bedroom_for(A)),
    sleep_interruption(A).

constructive_denial(HA, separate_bedroom_for(A)) :-
    approved_in_principle(HA, live_in_aide_status(A, T)),
    denied(HA, separate_bedroom_for(A)),
    live_in_aide_for(A, T),
    not_effective(separate_bedroom_for(A)).

violates_duty_to_accommodate(HA, separate_bedroom_for(A)) :-
    duty_to_grant(HA, separate_bedroom_for(A)),
    denied(HA, separate_bedroom_for(A)).

violates_duty_to_accommodate(HA, separate_bedroom_for(A)) :-
    constructive_denial(HA, separate_bedroom_for(A)).

% ---------- Canonical theorem ----------
claim_valid(HA, Aide, Tenant) :-
    housing_authority(HA),
    live_in_aide_for(Aide, Tenant),
    disabled(Tenant),
    needs_live_in_aide(Tenant),
    requested(Tenant, separate_bedroom_for(Aide)),
    medical_verification(Tenant, separate_bedroom_for(Aide)),
    sleep_interruption(Aide),
    not undue_burden(HA, separate_bedroom_for(Aide)),
    not fundamental_alteration(HA, separate_bedroom_for(Aide)).

result(HA, Aide, violation_and_constructive_denial) :-
    claim_valid(HA, Aide, _),
    approved_in_principle(HA, live_in_aide_status(Aide, _)),
    denied(HA, separate_bedroom_for(Aide)).
