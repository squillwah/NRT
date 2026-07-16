
# Defining the probability curves of each supported mutation along the dataset gradient.

# We could define different kinds of gradients ...
#  - The initial idea used the word 'severity', but mean more human error increasing -> fabrication -> complete hallucinations
# Different sets of curves represent different kinds of sets.

from tools.datasets.mutators import MutationType as M
from tools.references.refdata import ReferenceComponent as C
import matplotlib.pyplot as plt
import math
import random

# Defining the probabilty curves of each possible mutation as we move through the dataset.

steps = 100      # Setting probability points at the bounds of 10 equal chunks

x_range = 400   # Size of the subset being mutated, 0 -> x_range (-1?, no). Using 1 -> x_range, inclusive. Represents the item, not the offset in an array.

step_size, step_over = x_range // (steps-1), x_range % (steps-1)    # 0 is included as point 1, so divide step_size as 1/9 of range max

# 0 is start, 400 is end

# Quantized.

x_points = [i*step_size for i in range(steps)]

print(x_points, step_over)
if step_over:
    x_points[-1] += step_over 
    distribute = int(steps / step_over)
    for i in range(1, step_over):
        x_points[i*distribute] += 1
print(x_points)
#plt.scatter(x_points, [1]*steps, color='black', marker='o', linestyle=':', linewidth=2)

precision = 100  # 10 points (x) to define curves (y).
step_size = x_range/(precision-1)   # Zeroth x is considered first point, space rest evenly.
x_points = [i*step_size for i in range(precision)]
print(x_points)
#plt.scatter(x_points, [2]*steps, color='red', marker='o', linestyle=':', linewidth=2)

print()
# Quantize (x = discrete dataset entry)
print([round(x) for x in x_points])
x_points = [round(x) for x in x_points[:-1]] + [math.ceil(x_points[-1])]
print(x_points)
# Just quantize 

#plt.scatter(x_points, [3]*steps, color='blue', marker='o', linestyle=':', linewidth=2)
#plt.xlabel("Dataset")
#plt.ylabel("Probability")
#
#plt.ylim(0, 10)
#plt.show()


# Really it should just be the points themselves, instead of relying on an even distribution...
# Axis are already normalized
# (0, .1), (.5, 1), ...

#@dataclass
#class MutationCurveSet:
#    x_precision: int
#    y_values: dict[tuple[ReferenceComponent, MutationType], tuple[float]]

curves = {
    (C.AUTHORS, M.TYPO):                    ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.AUTHORS, M.MISMATCH):                ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.AUTHORS, M.HALLUCINATION):           ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.AUTHORS, M.SHUFFLE):                 ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.AUTHORS, M.OMISSION):                ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.TITLE, M.TYPO):                      ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.TITLE, M.MISMATCH):                  ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.TITLE, M.HALLUCINATION):             ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.TITLE, M.OMISSION):                  ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_NAME, M.TYPO):               ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_NAME, M.MISMATCH):           ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_NAME, M.HALLUCINATION):      ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_NAME, M.OMISSION):           ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_VOLUME, M.HALLUCINATION):    ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_VOLUME, M.OMISSION):         ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_ISSUE, M.HALLUCINATION):     ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_ISSUE, M.OMISSION):          ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_PAGE, M.HALLUCINATION):      ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.JOURNAL_PAGE, M.OMISSION):           ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.ELOCATOR, M.MISMATCH):               ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.ELOCATOR, M.HALLUCINATION):          ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.ELOCATOR, M.OMISSION):               ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PUBLICATION_DATE, M.HALLUCINATION):  ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PUBLICATION_DATE, M.OMISSION):       ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PMCID, M.TYPO):                      ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PMCID, M.MISMATCH):                  ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PMCID, M.HALLUCINATION):             ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PMCID, M.OMISSION):                  ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PMID, M.TYPO):                       ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PMID, M.MISMATCH):                   ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PMID, M.HALLUCINATION):              ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.PMID, M.OMISSION):                   ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.DOI, M.TYPO):                        ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.DOI, M.MISMATCH):                    ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.DOI, M.HALLUCINATION):               ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)),
    (C.DOI, M.OMISSION):                    ((0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0))
}

def check_curves(curves, all_possible_mutations):
    all_defined = all(bool(mutation in curves) for mutation in all_possible_mutations)
    no_erroneous = all(bool(mutation in all_possible_mutations) for mutation in curves)
    return all_defined, no_erroneous

#from tools.datasets.mutators import EntryMutator
#print(*[m for m in EntryMutator.mutations(flat=True)], sep="\n")
#print(*[m for m in curves], sep="\n")
#print(check_curves(curves, EntryMutator.mutations(flat=True)))

class MutationProbability:
    def __init__(self, subset_size, curves):
        # Distribute the normalized points along an X axis fitting the subset_size
        self.curves = dict.fromkeys(curves)
        for curve, points in curves.items():
            self.curves[curve] = [None]*len(points)
            for point, (x, y) in enumerate(points):
                x *= subset_size
                self.curves[curve][point] = (x, y)

    def plot(self, plt):
        #colors = [(random.random(), random.random(), random.random()) for _ in range(len(self.curves))]
        fig, axs = plt.subplots(nrows=6, ncols=6, sharey=True, sharex=True, layout="constrained")
        fig.suptitle("Mutation Probabilties Across Dataset", fontweight="bold", fontsize=14)
        axx, axy = 0, 0
        order = list(self.curves.keys())
        order.sort(key=lambda c: str(c[1]))
        #sort_sames = curves.sort(key=lambda c: c.keys()[1]) # Group mutation types together
        #for i, (curve, points) in enumerate(sort_sames.items()):
        for curve in order:
            x, y = zip(*self.curves[curve])
            ax = axs[axx, axy]
            ##ax.set_title(label="::".join(curve))
            ax.set_title(f"{str(curve[1]).capitalize()}: {str(curve[0])}", fontsize=10, fontweight="bold")
            ax.plot(x, y, color="blue")
            axx += 1
            if axx > 5: 
                axx = 0
                axy += 1


# By luck, number of mutation is square of 6
#def on_pick(event):
#    line = event.artist
print(len(curves)) 
#quit()



#m = MutationProbability(400, curves)
import curvepoints
CURVES = {
    # ── AUTHORS ─────────────────────────────────────────────────────────────
    # Full arc: subtle typo/shuffle -> mismatch -> hallucination
    (C.AUTHORS, M.TYPO):                    ((0.1, 0.15), (0.2, 0.25), (0.3, 0.30), (0.4, 0.28), (0.5, 0.22), (0.6, 0.15), (0.7, 0.10), (0.8, 0.06), (0.9, 0.03), (1.0, 0.02)),
    (C.AUTHORS, M.SHUFFLE):                 ((0.1, 0.05), (0.2, 0.12), (0.3, 0.20), (0.4, 0.28), (0.5, 0.30), (0.6, 0.25), (0.7, 0.18), (0.8, 0.10), (0.9, 0.05), (1.0, 0.02)),
    (C.AUTHORS, M.MISMATCH):                ((0.1, 0.05), (0.2, 0.10), (0.3, 0.18), (0.4, 0.28), (0.5, 0.40), (0.6, 0.50), (0.7, 0.55), (0.8, 0.52), (0.9, 0.45), (1.0, 0.35)),
    (C.AUTHORS, M.OMISSION):                ((0.1, 0.15), (0.2, 0.20), (0.3, 0.22), (0.4, 0.18), (0.5, 0.12), (0.6, 0.10), (0.7, 0.12), (0.8, 0.18), (0.9, 0.25), (1.0, 0.30)),
    (C.AUTHORS, M.HALLUCINATION):           ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.05), (0.5, 0.10), (0.6, 0.20), (0.7, 0.35), (0.8, 0.55), (0.9, 0.75), (1.0, 0.90)),

    # ── TITLE ───────────────────────────────────────────────────────────────
    # Omission scaled down (titles are almost never legitimately missing);
    # hallucination scaled up (fully fabricated titles are a hallmark tell)
    (C.TITLE, M.TYPO):                      ((0.1, 0.15), (0.2, 0.25), (0.3, 0.30), (0.4, 0.28), (0.5, 0.22), (0.6, 0.15), (0.7, 0.10), (0.8, 0.06), (0.9, 0.03), (1.0, 0.02)),
    (C.TITLE, M.MISMATCH):                  ((0.1, 0.05), (0.2, 0.09), (0.3, 0.15), (0.4, 0.22), (0.5, 0.30), (0.6, 0.36), (0.7, 0.38), (0.8, 0.34), (0.9, 0.28), (1.0, 0.22)),
    (C.TITLE, M.OMISSION):                  ((0.1, 0.03), (0.2, 0.04), (0.3, 0.05), (0.4, 0.05), (0.5, 0.04), (0.6, 0.04), (0.7, 0.05), (0.8, 0.07), (0.9, 0.09), (1.0, 0.10)),
    (C.TITLE, M.HALLUCINATION):             ((0.1, 0.00), (0.2, 0.01), (0.3, 0.03), (0.4, 0.06), (0.5, 0.12), (0.6, 0.25), (0.7, 0.42), (0.8, 0.62), (0.9, 0.80), (1.0, 0.93)),

    # ── JOURNAL_NAME ────────────────────────────────────────────────────────
    (C.JOURNAL_NAME, M.TYPO):               ((0.1, 0.15), (0.2, 0.25), (0.3, 0.30), (0.4, 0.28), (0.5, 0.22), (0.6, 0.15), (0.7, 0.10), (0.8, 0.06), (0.9, 0.03), (1.0, 0.02)),
    (C.JOURNAL_NAME, M.MISMATCH):           ((0.1, 0.05), (0.2, 0.10), (0.3, 0.18), (0.4, 0.28), (0.5, 0.40), (0.6, 0.50), (0.7, 0.55), (0.8, 0.52), (0.9, 0.45), (1.0, 0.35)),
    (C.JOURNAL_NAME, M.OMISSION):           ((0.1, 0.15), (0.2, 0.20), (0.3, 0.22), (0.4, 0.18), (0.5, 0.12), (0.6, 0.10), (0.7, 0.12), (0.8, 0.18), (0.9, 0.25), (1.0, 0.30)),
    (C.JOURNAL_NAME, M.HALLUCINATION):      ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.05), (0.5, 0.11), (0.6, 0.22), (0.7, 0.38), (0.8, 0.58), (0.9, 0.76), (1.0, 0.90)),

    # ── JOURNAL_VOLUME ──────────────────────────────────────────────────────
    # Only omission/hallucination exist for this field; omission baseline
    # raised since volume is often legitimately absent even in clean refs
    (C.JOURNAL_VOLUME, M.OMISSION):         ((0.1, 0.20), (0.2, 0.25), (0.3, 0.24), (0.4, 0.20), (0.5, 0.15), (0.6, 0.12), (0.7, 0.12), (0.8, 0.15), (0.9, 0.20), (1.0, 0.24)),
    (C.JOURNAL_VOLUME, M.HALLUCINATION):    ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.05), (0.5, 0.10), (0.6, 0.20), (0.7, 0.35), (0.8, 0.55), (0.9, 0.75), (1.0, 0.90)),

    # ── JOURNAL_ISSUE ───────────────────────────────────────────────────────
    # Omission baseline highest of all fields (many journals have no issue
    # numbers at all); hallucination slightly damped as it's a minor detail
    (C.JOURNAL_ISSUE, M.OMISSION):          ((0.1, 0.25), (0.2, 0.28), (0.3, 0.26), (0.4, 0.22), (0.5, 0.18), (0.6, 0.16), (0.7, 0.18), (0.8, 0.22), (0.9, 0.26), (1.0, 0.30)),
    (C.JOURNAL_ISSUE, M.HALLUCINATION):     ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.04), (0.5, 0.08), (0.6, 0.16), (0.7, 0.28), (0.8, 0.45), (0.9, 0.62), (1.0, 0.78)),

    # ── JOURNAL_PAGE ────────────────────────────────────────────────────────
    # Omission raised (many modern refs use elocators instead of page ranges)
    (C.JOURNAL_PAGE, M.OMISSION):           ((0.1, 0.20), (0.2, 0.24), (0.3, 0.24), (0.4, 0.20), (0.5, 0.16), (0.6, 0.14), (0.7, 0.16), (0.8, 0.20), (0.9, 0.24), (1.0, 0.28)),
    (C.JOURNAL_PAGE, M.HALLUCINATION):      ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.05), (0.5, 0.10), (0.6, 0.20), (0.7, 0.35), (0.8, 0.55), (0.9, 0.75), (1.0, 0.90)),

    # ── ELOCATOR ────────────────────────────────────────────────────────────
    # No typo (identifier is more atomic); omission raised (still an
    # inconsistently-adopted field across journals/eras)
    (C.ELOCATOR, M.MISMATCH):               ((0.1, 0.03), (0.2, 0.07), (0.3, 0.13), (0.4, 0.20), (0.5, 0.30), (0.6, 0.38), (0.7, 0.42), (0.8, 0.40), (0.9, 0.34), (1.0, 0.26)),
    (C.ELOCATOR, M.OMISSION):               ((0.1, 0.25), (0.2, 0.28), (0.3, 0.27), (0.4, 0.22), (0.5, 0.18), (0.6, 0.16), (0.7, 0.18), (0.8, 0.22), (0.9, 0.26), (1.0, 0.30)),
    (C.ELOCATOR, M.HALLUCINATION):          ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.05), (0.5, 0.10), (0.6, 0.20), (0.7, 0.35), (0.8, 0.55), (0.9, 0.75), (1.0, 0.90)),

    # ── PUBLICATION_DATE ────────────────────────────────────────────────────
    # Omission kept low (a year at minimum is almost always present)
    (C.PUBLICATION_DATE, M.OMISSION):       ((0.1, 0.08), (0.2, 0.10), (0.3, 0.10), (0.4, 0.08), (0.5, 0.06), (0.6, 0.05), (0.7, 0.06), (0.8, 0.08), (0.9, 0.10), (1.0, 0.12)),
    (C.PUBLICATION_DATE, M.HALLUCINATION):  ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.05), (0.5, 0.10), (0.6, 0.20), (0.7, 0.35), (0.8, 0.55), (0.9, 0.75), (1.0, 0.90)),

    # ── PMCID ───────────────────────────────────────────────────────────────
    # Typo boosted (digit transposition is classic for these IDs);
    # hallucination boosted (fabricated identifiers are the signature tell)
    (C.PMCID, M.TYPO):                      ((0.1, 0.18), (0.2, 0.28), (0.3, 0.32), (0.4, 0.28), (0.5, 0.20), (0.6, 0.14), (0.7, 0.09), (0.8, 0.05), (0.9, 0.03), (1.0, 0.02)),
    (C.PMCID, M.MISMATCH):                  ((0.1, 0.05), (0.2, 0.10), (0.3, 0.18), (0.4, 0.28), (0.5, 0.40), (0.6, 0.50), (0.7, 0.55), (0.8, 0.52), (0.9, 0.45), (1.0, 0.35)),
    (C.PMCID, M.OMISSION):                  ((0.1, 0.20), (0.2, 0.22), (0.3, 0.20), (0.4, 0.16), (0.5, 0.13), (0.6, 0.12), (0.7, 0.14), (0.8, 0.18), (0.9, 0.22), (1.0, 0.26)),
    (C.PMCID, M.HALLUCINATION):             ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.05), (0.5, 0.12), (0.6, 0.25), (0.7, 0.42), (0.8, 0.65), (0.9, 0.82), (1.0, 0.95)),

    # ── PMID ────────────────────────────────────────────────────────────────
    (C.PMID, M.TYPO):                       ((0.1, 0.18), (0.2, 0.28), (0.3, 0.32), (0.4, 0.28), (0.5, 0.20), (0.6, 0.14), (0.7, 0.09), (0.8, 0.05), (0.9, 0.03), (1.0, 0.02)),
    (C.PMID, M.MISMATCH):                   ((0.1, 0.05), (0.2, 0.10), (0.3, 0.18), (0.4, 0.28), (0.5, 0.40), (0.6, 0.50), (0.7, 0.55), (0.8, 0.52), (0.9, 0.45), (1.0, 0.35)),
    (C.PMID, M.OMISSION):                   ((0.1, 0.15), (0.2, 0.20), (0.3, 0.22), (0.4, 0.18), (0.5, 0.12), (0.6, 0.10), (0.7, 0.12), (0.8, 0.18), (0.9, 0.25), (1.0, 0.30)),
    (C.PMID, M.HALLUCINATION):              ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.05), (0.5, 0.12), (0.6, 0.25), (0.7, 0.42), (0.8, 0.65), (0.9, 0.82), (1.0, 0.95)),

    # ── DOI ─────────────────────────────────────────────────────────────────
    # Hallucination highest of the whole dataset: fabricated DOIs are the
    # single most recognizable LLM citation-hallucination pattern.
    # Omission kept low: DOIs are near-universal now, rarely legitimately absent.
    (C.DOI, M.TYPO):                        ((0.1, 0.18), (0.2, 0.28), (0.3, 0.32), (0.4, 0.28), (0.5, 0.20), (0.6, 0.14), (0.7, 0.09), (0.8, 0.05), (0.9, 0.03), (1.0, 0.02)),
    (C.DOI, M.MISMATCH):                    ((0.1, 0.05), (0.2, 0.10), (0.3, 0.18), (0.4, 0.28), (0.5, 0.40), (0.6, 0.50), (0.7, 0.55), (0.8, 0.52), (0.9, 0.45), (1.0, 0.35)),
    (C.DOI, M.OMISSION):                    ((0.1, 0.10), (0.2, 0.12), (0.3, 0.12), (0.4, 0.10), (0.5, 0.08), (0.6, 0.07), (0.7, 0.08), (0.8, 0.10), (0.9, 0.13), (1.0, 0.16)),
    (C.DOI, M.HALLUCINATION):               ((0.1, 0.00), (0.2, 0.01), (0.3, 0.02), (0.4, 0.05), (0.5, 0.13), (0.6, 0.27), (0.7, 0.45), (0.8, 0.68), (0.9, 0.85), (1.0, 0.97)),
}
print(CURVES)
m = MutationProbability(400, CURVES)
m.plot(plt)
#plt.legend(loc='upper left', bbox_to_anchor=(1.05,1), title="Mutations")
#plt.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=5)
#plt.legend(loc='upper left', bbox_to_anchor=(-.2,1), ncols = 1, title="Mutations")
#plt.legend(ncols = 3, title="Mutations")
plt.show()
quit()
class MutationProbability2:
    _PRECISION = 10 # How many points make up the curves. Or should this be dynamic, based on size of set array? 
                    # Each point is assumed to be evenly distributed anyways
                    # There's be a minimum of at least one, if it's constant (flat line).
                    # What would all this look like as a picture? Matrix.


    def __init__(self, subset_size):
        # Finding x points (even distribution)
        step_size = subset_size / (self._PRECISION-1)
        self.x_points = [round(i*step_size) for i in range(self._PRECISION)] # Quantized, each point is discrete dataset entry.

    

curves = {
    (C.AUTHORS, M.TYPO):                    (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.AUTHORS, M.MISMATCH):                (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.AUTHORS, M.HALLUCINATION):           (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.AUTHORS, M.SHUFFLE):                 (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.AUTHORS, M.OMISSION):                (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.TITLE, M.TYPO):                      (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.TITLE, M.MISMATCH):                  (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.TITLE, M.HALLUCINATION):             (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.TITLE, M.OMISSION):                  (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_NAME, M.TYPO):               (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_NAME, M.MISMATCH):           (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_NAME, M.HALLUCINATION):      (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_NAME, M.OMISSION):           (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_VOLUME, M.HALLUCINATION):    (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_VOLUME, M.OMISSION):         (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_ISSUE, M.HALLUCINATION):     (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_ISSUE, M.OMISSION):          (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_PAGE, M.HALLUCINATION):      (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.JOURNAL_PAGE, M.OMISSION):           (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.ELOCATOR, M.MISMATCH):               (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.ELOCATOR, M.HALLUCINATION):          (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.ELOCATOR, M.OMISSION):               (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PUBLICATION_DATE, M.HALLUCINATION):  (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PUBLICATION_DATE, M.OMISSION):       (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PMCID, M.TYPO):                      (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PMCID, M.MISMATCH):                  (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PMCID, M.HALLUCINATION):             (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PMCID, M.OMISSION):                  (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PMID, M.TYPO):                       (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PMID, M.MISMATCH):                   (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PMID, M.HALLUCINATION):              (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.PMID, M.OMISSION):                   (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.DOI, M.TYPO):                        (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.DOI, M.MISMATCH):                    (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.DOI, M.HALLUCINATION):               (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    (C.DOI, M.OMISSION):                    (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
}



#@dataclass
#class Grumple:
if True:
    duplications = 5    # How many times are the source references duplicated (size of the gradient)
    
    # Need a key for each specific mutation type .... Could use tuples as keys?

    # 1 Add omission to mutators
    # 2 Create get_mutations method
    #  - Retun tuple? Use tuples as keys, or create new constants?

    # Splitting along x
    # 0, 1/4, 1/2, 3/4, 1
    x = [0, 1/4, 1/2, 3/4, 1]
    y = [.5, 1, .25, .1, .01]
    #(C.M[.5 1 .25 0 0]
    plt.plot(x, y, color='blue', marker='o', linestyle=':', linewidth=2)
    plt.xlabel("Dataset")
    plt.ylabel("Probability")

    plt.show()

    # Specific down to component mutations or broad mutation categories?
