import pandas as pd
class Ordinal:
    const=0
    def __init__(self):
         self.const=0
             
    def timenormalize(df,col):
                    df[col]=pd.to_datetime(df[col])
                    return (df[col].dt.year)+((df[col].dt.month)/12)+((df[col].dt.month)/(12*30))+((df[col].dt.day)/(12*30*24))

    def drug(df,col):
        l=[]
        for i in df[col]:
            if "-" in i:
                s1=i.split("-")
                if s1[0][-1].isalpha() or s1[1][-1].isalpha():
                    l.append(1)
                else:
                    s1=[float(j) for j in s1]
                    r=[j for j in range(int(s1[0]),int(s1[1])+1)]
                    l.append(sum(r)/(int(s1[1])-int(s1[1])+1))
            else :
                if "," in i:
                    s=""
                    for j in i:
                        if j!=",":
                            s+=j
                    l.append(float(s))
                else:
                    l.append(float(i))
        return l

    def medication1(df,col):
        medication_and_dosage = {
        'mcg': 1,
        'mcg/h': 2,
        'mcg/hr': 3,
        'mg': 4,
        'mg PE': 5,
        'g': 6,
        'gm': 7,
        'mEq': 8,
        'ml': 9,
        'mL': 10,
        'mmol': 11,
        'million units': 12,
        'dose': 13,
        'UNIT': 14,
        'UDCUP': 15,
        'gtt': 16,
        'DROP': 17,
        'BAG': 18,
        'PKT': 19,
        'CAP': 20,
        'TAB': 21,
        'LOZ': 22,
        'TROC': 23,
        'SPRY': 24,
        'SYR': 25,
        'PUFF': 26,
        'INH': 27,
        'NEB': 28,
        'Enema': 29,
        'AMP': 30,
        'VIAL': 31,
        'PTCH': 32,
        'Appl': 33,
        'L': 34,
        'in': 35
    }
        return df[col].apply(lambda x:medication_and_dosage[x])

    def medication2(df,col):

        medication_and_dosage1 = {
            '<NA>': 1,
            'g': 2,
            'gm': 3,
            'mg': 4,
            'mL': 5,
            'ml': 6,
            'million units': 7,
            'dose': 8,
            'UNIT': 9,
            'UDCUP': 10,
            'gtt': 11,
            'DRP': 12,
            'DROP': 13,
            'BAG': 14,
            'PKT': 15,
            'CAP': 16,
            'TAB': 17,
            'LOZ': 18,
            'TROC': 19,
            'SPRY': 20,
            'SYR': 21,
            'PUFF': 22,
            'INH': 23,
            'NEB': 24,
            'Enema': 25,
            'AMP': 26,
            'VIAL': 27,
            'PTCH': 28,
            'Appl': 29,
            'TUBE': 30,
            'AERO': 31,
            'CAN': 32,
            'KIT': 33,
            'DEV': 34,
            'BTL': 35,
            'DBTL': 36,
            'SUPP': 37
        }
        return df[col].apply(lambda x:medication_and_dosage1[x] if x in medication_and_dosage1 else 1)

