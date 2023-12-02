import matplotlib.pyplot as plt
import numpy as np

data = np.load("qtable-1000000steps.npz")
data = data['arr_0']
# Slices of the array
row_slice = slice(4, 22)
col_slice = slice(2, 12)
# Creating the difference array
difference = data[row_slice, col_slice, 0] - data[row_slice, col_slice, 1]


# Updating thef plotting code
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for i,name in enumerate(['Hit','Stand']):
    ax = axes[i]
    heatmap = ax.imshow(data[row_slice, col_slice, i])
    ax.set_title(f"Q Table for {name}")
    fig.colorbar(heatmap, ax=ax)

    # Setting axis labels to reflect the slice
    ax.set_xlabel('Dealer Upcard')
    ax.set_ylabel('Player Score')

    # Adjusting the tick labels to match the slice
    ax.set_xticks(np.arange(data[row_slice, col_slice, i].shape[1]))
    ax.set_yticks(np.arange(data[row_slice, col_slice, i].shape[0]))

    ax.set_xticklabels(np.arange(col_slice.start, col_slice.stop))
    ax.set_yticklabels(np.arange(row_slice.start, row_slice.stop))

# Plotting the difference heatmap
ax = axes[2]
diff_heatmap = ax.imshow(difference, cmap='coolwarm')  # Using a diverging colormap
ax.set_title("Difference (Hit - Stand)")
fig.colorbar(diff_heatmap, ax=ax)

# Setting axis labels and adjusting tick labels for the difference plot
ax.set_xlabel('Dealer Upcard')
ax.set_ylabel('Player Score')
ax.set_xticks(np.arange(difference.shape[1]))
ax.set_yticks(np.arange(difference.shape[0]))
ax.set_xticklabels(np.arange(col_slice.start, col_slice.stop))
ax.set_yticklabels(np.arange(row_slice.start, row_slice.stop))


plt.tight_layout()
plt.show()
