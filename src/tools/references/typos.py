
import random

# ----------
# Typo tools
# ----------

class Typofier:

    _FATSWAP_RATIO = 2/3        # Fatfingers are twice as likely as swaps.
    _TYPOFY_FREQUENCY = 1/20    # 1 + len(string)*tf typos (1 + 1 per 10 chars).

    # Swap char at index with adjacent key (on the keyboard).
    @staticmethod
    def typo_fatfinger(word, index):
        QWERTY = ["qwertyuiop",
                  "asdfghjkl;",
                  "zxcvbnmn,."]     # !! Sometimes the non alphanumerics would cause issue. Decisions are to remove alpha check in mutator or remove those chars here. @todo think
        typo = None
        for ri, row in enumerate(QWERTY):
            if (li := row.find(word[index].lower())) != -1:
                row_shift = [0]
                if ri > 0: row_shift.append(-1)         # Stupid. Will break easy if row or letter counts change.
                if ri < 2: row_shift.append(1)
                row_shift = random.choice(row_shift)
                let_shift = []
                if li > 0: let_shift.append(-1)
                if row_shift != 0: let_shift.append(0)
                if li < 9: let_shift.append(1)
                let_shift = random.choice(let_shift)
                typo = word[:index]+QWERTY[ri+row_shift][li+let_shift]+word[index+1:]
                break
        # Janky fallback. If we really care there's probably some library to translate foreign keys -> QWERTY or do the whole thing for us.
        if not typo:
            #print(f"! bad fatfinger {(word, index)}, falling back to letter swap")
            #typo = typo_swapletter(word, index) # Potential bug, will crash if len(word) < 2
            print(f"! bad fatfinger {(word, index)}, picking random char")
            typo = word[:index]+QWERTY[random.randint(0,2)][random.randint(0,9)]+word[index+1:]
        return typo

    # Swap char at index with adjacent char in string.
    @staticmethod
    def typo_swapletter(word, index):
        print("! ", word)
        right = (index == 0 or (random.random()>.5 and index < len(word)-1))
        typo = None
        if right:
            typo = word[0:index]+word[index+1]+word[index]+word[index+2:]
        else:
            typo = word[0:index-1]+word[index]+word[index-1]+word[index+1:]
        #print(f"{index*" "}{index}{int(right)*"-"}\n{typo}")
        return typo

    # Randomly pick between fatfinger or swap typo types.
    @classmethod
    def fatswap(cls, string, index):
        typo = None
        if random.random() <= cls._FATSWAP_RATIO or len(string) == 1: # An unswappable length vetos the ratio.
            typo = cls.typo_fatfinger(string, index)
        else:
            typo = cls.typo_swapletter(string, index)
        return typo

    # Randomly add typos (random index) to a string. Increasing typo count with length.
    @classmethod
    def typofy(cls, string):
        # Another arbitrary definition of typos
        #  - Typos are place randomly within the string
        #  - There is always at least 1 typo, with more for every 10 characters in the title.
        for i in range(int(len(string) * cls._TYPOFY_FREQUENCY) + 1):
            string = cls.fatswap(string, random.randint(0, len(string)-1)) # Any random character.
        return string

    #def typofy_freq    If we end up caring enough to remove author typo stuff from EntryMutator
    #def typofy_prob
