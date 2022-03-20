import json
import numpy as np
import matplotlib.pyplot as plt


show = False
save = True

# with open("../data/results/_total_results.json", "r") as f:
#     data = json.load(f)

with open("../data/resultsV2/_total_results.json", "r") as f:
    data = json.load(f)

output_dir = "../data/imagesV2"

compression_ratios = []
cost_ratios = []
for d in data:
    compression_ratios.append(d["compression_ratio"])
    cost_ratios.append(d["cost_ratio"])

compression_ratios = np.array(compression_ratios)
cost_ratios = np.array(cost_ratios)

median_compression = np.median(compression_ratios)
median_cost = np.median(cost_ratios)
median_ratio = np.median(compression_ratios/cost_ratios)

print(f"Max compression ratio: {compression_ratios.max()}")
print(f"Median compression ratio: {median_compression}")
print(f"Min compression ratio: {compression_ratios.min()}")

print(f"Max cost ratio: {cost_ratios.max()}")
print(f"Median cost ratio: {median_cost}")
print(f"Min cost ratio: {cost_ratios.min()}")

plt.title("Compression Ratio")
plt.hist(compression_ratios, bins=1000, range=(1, 7))
plt.axvline(median_compression, label=f"median = {median_compression:.2f}", color="red")
plt.ylabel('N')
plt.xlabel("Compression Ratio")
plt.legend()
if save:
    plt.savefig(f"{output_dir}/compression_ratio_hist.png")
if show:
    plt.show()
plt.close("all")

plt.title("Cost Ratio")
plt.hist(cost_ratios, bins=1000, range=(1, 7))
plt.axvline(median_cost, label=f"median = {median_cost:.2f}", color="red")
plt.ylabel('N')
plt.xlabel("Cost Ratio")
plt.legend()
if save:
    plt.savefig(f"{output_dir}/cost_ratio_hist.png")
if show:
    plt.show()
plt.close("all")

x = np.arange(len(compression_ratios))
plt.title("Compression Ratio vs Batch Number")
plt.plot(x, compression_ratios)
plt.axhline(median_compression, label=f"median={median_compression:.2f}", color="red")
plt.legend()
if save:
    plt.savefig(f"{output_dir}/compression_ratio.png")
if show:
    plt.show()
plt.close("all")

plt.title("Cost Ratio vs Batch Number")
plt.plot(x, cost_ratios)
plt.axhline(median_cost, label=f"median={median_cost:.2f}", color="red")
plt.xlabel("Batch")
plt.ylabel("Cost Ratio")
# plt.ylim(1, 5)
plt.legend()
if save:
    plt.savefig(f"{output_dir}/cost_ratio.png")
if show:
    plt.show()
plt.close("all")

plt.title("Overestimation Ratio vs Batch Number")
plt.plot(x, compression_ratios/cost_ratios)
plt.axhline(median_ratio, label=f"median={median_ratio:.2f}", color="red")
plt.xlabel("Batch")
plt.ylabel("Overestimation")
plt.legend()
if save:
    plt.savefig(f"{output_dir}/overestimation_ratio.png")
if show:
    plt.show()
plt.close("all")