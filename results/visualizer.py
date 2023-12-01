import matplotlib.pyplot as plt
import numpy as np

data = np.load("qtable-10000steps.npz")
data = data['arr_0']
# Slices of the array
row_slice = slice(4, 22)
col_slice = slice(2, 12)

# Updating the plotting code
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

for i,name in enumerate(['Hit','Stand']):
    ax = axes[i]
    heatmap = ax.imshow(data[row_slice, col_slice, i])
    ax.set_title(f"Q Table for {name}")
    fig.colorbar(heatmap, ax=ax)

    # Setting axis labels to reflect the slice
    ax.set_xlabel('Player Score')
    ax.set_ylabel('Dealer Upcard')

    # Adjusting the tick labels to match the slice
    ax.set_xticks(np.arange(data[row_slice, col_slice, i].shape[1]))
    ax.set_yticks(np.arange(data[row_slice, col_slice, i].shape[0]))

    ax.set_xticklabels(np.arange(col_slice.start, col_slice.stop))
    ax.set_yticklabels(np.arange(row_slice.start, row_slice.stop))

plt.tight_layout()
plt.show()