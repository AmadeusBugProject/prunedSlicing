OLEV = 600
MAXALTDIFF = 600
NO_INTENT = 0
TCAS_TA = 1
UNRESOLVED = 0
UPWARD_RA = 1
DOWNWARD_RA = 2
High_Confidence = True
Own_Tracked_Alt_Rate = 500
Cur_Vertical_Sep = 700
Other_Capability = 1
Two_of_Three_Reports_Valid = False
Other_RAC = 0
Non_Crossing_Biased_Climb = True
Own_Below_Threat = True
enabled = High_Confidence and (Own_Tracked_Alt_Rate <= OLEV) and (Cur_Vertical_Sep > MAXALTDIFF)
tcas_equipped = Other_Capability == TCAS_TA
intent_not_known = Two_of_Three_Reports_Valid and Other_RAC == NO_INTENT
if enabled and ((intent_not_known and tcas_equipped) or not tcas_equipped):
    need_upward_RA = Non_Crossing_Biased_Climb and Own_Below_Threat
    if need_upward_RA:
        alt_sep = UPWARD_RA
    else:
        alt_sep = DOWNWARD_RA
else:
    alt_sep = UNRESOLVED
alt_sep = alt_sep