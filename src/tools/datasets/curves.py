
# Defining the probability curves of each supported mutation along the dataset gradient.

# We could define different kinds of gradients ...
#  - The initial idea used the word 'severity', but mean more human error increasing -> fabrication -> complete hallucinations
# Different sets of curves represent different kinds of sets.

from tools.datasets.mutators import MutationType as M
from tools.references.refdata import ReferenceComponent as C
import matplotlib.pyplot as plt
import math

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
plt.scatter(x_points, [1]*steps, color='black', marker='o', linestyle=':', linewidth=2)

precision = 100  # 10 points (x) to define curves (y).
step_size = x_range/(precision-1)   # Zeroth x is considered first point, space rest evenly.
x_points = [i*step_size for i in range(precision)]
print(x_points)
plt.scatter(x_points, [2]*steps, color='red', marker='o', linestyle=':', linewidth=2)

print()
# Quantize (x = discrete dataset entry)
print([round(x) for x in x_points])
x_points = [round(x) for x in x_points[:-1]] + [math.ceil(x_points[-1])]
print(x_points)
# Just quantize 

plt.scatter(x_points, [3]*steps, color='blue', marker='o', linestyle=':', linewidth=2)
plt.xlabel("Dataset")
plt.ylabel("Probability")

plt.ylim(0, 10)
plt.show()


quit()

curves = {
    (C.AUTHORS, M.TYPO):                    [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.AUTHORS, M.MISMATCH):                [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.AUTHORS, M.HALLUCINATION):           [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.AUTHORS, M.SHUFFLE):                 [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.AUTHORS, M.OMISSION):                [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.TITLE, M.TYPO):                      [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.TITLE, M.MISMATCH):                  [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.TITLE, M.HALLUCINATION):             [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.TITLE, M.OMISSION):                  [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_NAME, M.TYPO):               [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_NAME, M.MISMATCH):           [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_NAME, M.HALLUCINATION):      [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_NAME, M.OMISSION):           [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_VOLUME, M.HALLUCINATION):    [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_VOLUME, M.OMISSION):         [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_ISSUE, M.HALLUCINATION):     [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_ISSUE, M.OMISSION):          [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_PAGE, M.HALLUCINATION):      [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.JOURNAL_PAGE, M.OMISSION):           [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.ELOCATOR, M.MISMATCH):               [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.ELOCATOR, M.HALLUCINATION):          [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.ELOCATOR, M.OMISSION):               [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PUBLICATION_DATE, M.HALLUCINATION):  [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PUBLICATION_DATE, M.OMISSION):       [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PMCID, M.TYPO):                      [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PMCID, M.MISMATCH):                  [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PMCID, M.HALLUCINATION):             [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PMCID, M.OMISSION):                  [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PMID, M.TYPO):                       [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PMID, M.MISMATCH):                   [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PMID, M.HALLUCINATION):              [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.PMID, M.OMISSION):                   [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.DOI, M.TYPO):                        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.DOI, M.MISMATCH):                    [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.DOI, M.HALLUCINATION):               [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    (C.DOI, M.OMISSION):                    [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
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
