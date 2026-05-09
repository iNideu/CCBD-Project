import sys

import numpy as np
import pandas as pd


def main():
    if len(sys.argv) != 5:
        print("Usage: python process_single_sc.py <raw_csv_path> <sub_id> <vol_csv_path> <output_npy_path>")
        sys.exit(1)

    raw_matrix_path = sys.argv[1]
    sub_id = sys.argv[2]
    vol_csv_path = sys.argv[3]
    output_npy_path = sys.argv[4]

    subcortical = [10, 11, 12, 13, 17, 18, 26, 28, 49, 50, 51, 52, 53, 54, 58, 60]
    cortical_lh = [i for i in range(1001, 1036) if i != 1004]
    cortical_rh = [i for i in range(2001, 2036) if i != 2004]
    white_list = subcortical + cortical_lh + cortical_rh
    n_nodes = len(white_list)

    df_volumes = pd.read_csv(vol_csv_path)
    sub_data = df_volumes[df_volumes["sub"] == sub_id]
    if sub_data.empty:
        print(f"Error: {sub_id} not found in {vol_csv_path}")
        sys.exit(1)

    sub_data = sub_data.iloc[0]
    roi_volumes = np.array([sub_data[f"ROI_{roi}_vol"] for roi in white_list])

    sc_raw_huge = np.loadtxt(raw_matrix_path, delimiter=",")
    sc_subset = np.zeros((n_nodes, n_nodes))
    for i, orig_idx_i in enumerate(white_list):
        for j, orig_idx_j in enumerate(white_list):
            if orig_idx_i < sc_raw_huge.shape[0] and orig_idx_j < sc_raw_huge.shape[1]:
                sc_subset[i, j] = sc_raw_huge[orig_idx_i, orig_idx_j]

    vol_matrix = np.sqrt(np.outer(roi_volumes, roi_volumes))
    vol_matrix[vol_matrix == 0] = 1
    sc_norm = sc_subset / vol_matrix

    k = 15
    sc_sparse = np.zeros_like(sc_norm)
    for i in range(n_nodes):
        top_k_idx = np.argsort(sc_norm[i])[-k:]
        sc_sparse[i, top_k_idx] = sc_norm[i, top_k_idx]
    sc_sparse = (sc_sparse + sc_sparse.T) / 2

    sc_max, sc_min = np.max(sc_sparse), np.min(sc_sparse)
    sc_final = (sc_sparse - sc_min) / (sc_max - sc_min) if sc_max > sc_min else sc_sparse

    np.save(output_npy_path, sc_final)
    print(f"Success: {sub_id} SC matrix saved to {output_npy_path}")


if __name__ == "__main__":
    main()
