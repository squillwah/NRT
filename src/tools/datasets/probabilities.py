
# Defining the probability curves of each supported mutation along the dataset gradient.

# We could define different kinds of gradients ...
#  - The initial idea used the word 'severity', but mean more human error increasing -> fabrication -> complete hallucinations
# Different sets of curves represent different kinds of sets.

import numpy as np

def check_curves(curves, all_possible_mutations):
    all_defined = all(bool(mutation in curves) for mutation in all_possible_mutations)
    no_erroneous = all(bool(mutation in all_possible_mutations) for mutation in curves)
    return all_defined, no_erroneous

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
        fig, axs = plt.subplots(nrows=6, ncols=6, sharey=True, sharex=True, layout="constrained")
        fig.suptitle("Mutation Probabilties Across Dataset", fontweight="bold", fontsize=14)
        order = list(self.curves.keys())
        order.sort(key=lambda c: str(c[1]))
        axx, axy = 0, 0
        for curve in order:
            x, y = zip(*self.curves[curve])
            ax = axs[axx, axy]
            ax.set_title(f"{str(curve[1]).capitalize()}: {str(curve[0])}", fontsize=10, fontweight="bold")
            ax.plot(x, y, color="blue")
            axx += 1
            if axx > 5: 
                axx = 0
                axy += 1

    # Linearly interpolate between points.
    def probability(self, component, mutation, x):
        x_points, y_points = zip(*self.curves[(component, mutation)])
        return np.interp(x, x_points, y_points)

def test():
    from tools.references.refdata import ReferenceComponent
    from tools.datasets.mutators import EntryMutator, MutationType
    from tools.datasets.curves import MutationCurves
    import matplotlib.pyplot as plt
    import random
    
#    print(*[m for m in EntryMutator.mutations(flat=True)], sep="\n")
#    print(*[m for m in MutationCurves], sep="\n")
#    print(check_curves(MutationCurves, EntryMutator.mutations(flat=True)))

    MP = MutationProbability(1000, MutationCurves)
    MP.plot(plt)

    for i in range(0, 1001, 25):
        p = MP.probability(ReferenceComponent.TITLE, MutationType.HALLUCINATION, i)
        print(random.random() < p)
    
    plt.show()

#test()


