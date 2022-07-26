OLEV = 600
MAXALTDIFF = 600
MINSEP = 300
NOZCROSS = 100
NO_INTENT = 0
DO_NOT_CLIMB = 1
DO_NOT_DESCEND = 2
TCAS_TA = 1
OTHER = 2
UNRESOLVED = 0
UPWARD_RA = 1
DOWNWARD_RA = 2
POSITIVE_RA_ALT_THRESH_0 = 400
POSITIVE_RA_ALT_THRESH_1 = 500
POSITIVE_RA_ALT_THRESH_2 = 640
POSITIVE_RA_ALT_THRESH_3 = 740


class Tcas:
    def __init__(self, parameters):
        self.Cur_Vertical_Sep = parameters['Cur_Vertical_Sep']
        self.High_Confidence = parameters['High_Confidence']
        self.Two_of_Three_Reports_Valid = parameters['Two_of_Three_Reports_Valid']
        self.Own_Tracked_Alt = parameters['Own_Tracked_Alt']
        self.Own_Tracked_Alt_Rate = parameters['Own_Tracked_Alt_Rate']
        self.Other_Tracked_Alt = parameters['Other_Tracked_Alt']
        self.Alt_Layer_Value = parameters['Alt_Layer_Value']
        self.Up_Separation = parameters['Up_Separation']
        self.Down_Separation = parameters['Down_Separation']
        self.Other_RAC = parameters['Other_RAC']
        self.Other_Capability = parameters['Other_Capability']
        self.Climb_Inhibit = parameters['Climb_Inhibit']

    def ALIM(self):
        if self.Alt_Layer_Value == 0:
            return POSITIVE_RA_ALT_THRESH_0
        elif self.Alt_Layer_Value == 1:
            return POSITIVE_RA_ALT_THRESH_1
        elif self.Alt_Layer_Value == 2:
            return POSITIVE_RA_ALT_THRESH_2
        else:
            return POSITIVE_RA_ALT_THRESH_3

    def Inhibit_Biased_Climb(self):
        if self.Climb_Inhibit > 0:
            return self.Up_Separation + NOZCROSS
        else:
            return self.Up_Separation
    
    def Non_Crossing_Biased_Climb(self):
        if self.Inhibit_Biased_Climb() > self.Down_Separation:
            upward_preferred = 1
        else:
            upward_preferred = 0
        if upward_preferred != 0:
            result = not(self.Own_Below_Threat()) or (self.Own_Below_Threat() and (not(self.Down_Separation >= self.ALIM())))
        else:
            result = self.Own_Above_Threat() and (self.Cur_Vertical_Sep >= MINSEP) and (self.Up_Separation >= self.ALIM())
        return result
    
    def Non_Crossing_Biased_Descend(self):
        if self.Inhibit_Biased_Climb() >= self.Down_Separation:  # Fault9: operator mutation
            upward_preferred = 1
        else:
            upward_preferred = 0
        if upward_preferred != 0:
            result = self.Own_Below_Threat() and (self.Cur_Vertical_Sep >= MINSEP) and (self.Down_Separation >= self.ALIM())
        else:
            result = not(self.Own_Above_Threat()) or ((self.Own_Above_Threat()) and (self.Up_Separation >= self.ALIM()))
        return result
    
    def Own_Below_Threat(self):
        return self.Own_Tracked_Alt < self.Other_Tracked_Alt
    
    def Own_Above_Threat(self):
        return self.Other_Tracked_Alt < self.Own_Tracked_Alt
    
    def alt_sep_test(self):
        enabled = self.High_Confidence and (self.Own_Tracked_Alt_Rate <= OLEV) and (self.Cur_Vertical_Sep > MAXALTDIFF)
        tcas_equipped = self.Other_Capability == TCAS_TA
        intent_not_known = self.Two_of_Three_Reports_Valid and self.Other_RAC == NO_INTENT

        if enabled and ((tcas_equipped and intent_not_known) or not tcas_equipped):
            need_upward_RA = self.Non_Crossing_Biased_Climb() and self.Own_Below_Threat()
            need_downward_RA = self.Non_Crossing_Biased_Descend() and self.Own_Above_Threat()
            if need_upward_RA and need_downward_RA:
                # unreachable: requires Own_Below_Threat and Own_Above_Threat to both be true - that requires
                # Own_Tracked_Alt < Other_Tracked_Alt and Other_Tracked_Alt < Own_Tracked_Alt, which isn't possible
                alt_sep = UNRESOLVED
            elif need_upward_RA:
                alt_sep = UPWARD_RA
            elif need_downward_RA:
                alt_sep = DOWNWARD_RA
            else:
                alt_sep = UNRESOLVED
        else:
            alt_sep = UNRESOLVED
        return alt_sep
