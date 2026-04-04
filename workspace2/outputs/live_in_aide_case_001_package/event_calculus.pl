% event_calculus.pl
% Event calculus style export for the live-in aide accommodation dispute

% Happens(Event, Time)
% HoldsAt(Fluent, Time)
% Initiates(Event, Fluent, Time)
% Terminates(Event, Fluent, Time)

happens(request_accommodation(mother, separate_bedroom_for(aide)), t1).
happens(submit_medical_verification(mother, separate_bedroom_for(aide)), t2).
happens(approve_aide_in_principle(ha1, aide, mother), t3).
happens(deny_separate_bedroom(ha1, aide), t4).
happens(night_use(mother, living1), t5).

initiates(request_accommodation(T, A), requested(T, A), Tm).
initiates(submit_medical_verification(T, A), medically_supported(A), Tm).
initiates(approve_aide_in_principle(HA, Aide, T), approved_in_principle(HA, live_in_aide_status(Aide, T)), Tm).
initiates(deny_separate_bedroom(HA, Aide), denied(HA, separate_bedroom_for(Aide)), Tm).
initiates(night_use(T, living1), shared_night_conflict(living1), Tm).

holds_at(sleeps_in(aide, living1), t5).
holds_at(shared_night_conflict(living1), t5).

holds_at(sleep_interruption(aide), Tm) :-
    holds_at(sleeps_in(aide, living1), Tm),
    holds_at(shared_night_conflict(living1), Tm).

holds_at(not_effective(separate_bedroom_for(aide)), Tm) :-
    holds_at(sleep_interruption(aide), Tm),
    holds_at(denied(ha1, separate_bedroom_for(aide)), Tm).

holds_at(constructive_denial(separate_bedroom_for(aide)), Tm) :-
    holds_at(approved_in_principle(ha1, live_in_aide_status(aide, mother)), Tm),
    holds_at(not_effective(separate_bedroom_for(aide)), Tm).
