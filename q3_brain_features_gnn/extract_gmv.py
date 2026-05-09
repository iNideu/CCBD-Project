import os

import nibabel as nib
import numpy as np
import pandas as pd


def calculate_roi_volumes_for_subject(file_path, roi_list, voxel_size=0.8):
    """计算单个被试指定 ROI 列表的体积。"""
    if not os.path.exists(file_path):
        print(f"警告: 找不到文件 {file_path}")
        return {f"ROI_{roi}_vol": np.nan for roi in roi_list}

    img = nib.load(file_path)
    data = img.get_fdata()

    single_voxel_vol = voxel_size**3

    volumes = {}
    for roi_id in roi_list:
        voxel_count = np.sum(data == roi_id)
        volumes[f"ROI_{roi_id}_vol"] = voxel_count * single_voxel_vol

    return volumes


def batch_process_gmv(subject_csv, bids_root, output_csv):
    """批量处理所有被试的灰质体积，并保存到 CSV。"""
    subcortical_list = [10, 11, 12, 13, 17, 18, 26, 28, 49, 50, 51, 52, 53, 54, 58, 60]
    cortical_lh = [i for i in range(1001, 1036) if i != 1004]
    cortical_rh = [i for i in range(2001, 2036) if i != 2004]

    white_list = subcortical_list + cortical_lh + cortical_rh

    df = pd.read_csv(subject_csv)
    all_volumes_list = []

    print(f"开始提取 {len(df)} 名被试的灰质体积特征，共 {len(white_list)} 个脑区...")

    for index, row in df.iterrows():
        sub_id = row["sub"]
        file_path = os.path.join(
            bids_root,
            sub_id,
            "anat",
            "prep",
            f"{sub_id}_desc-aparcaseg_dseg.nii.gz",
        )

        vols = calculate_roi_volumes_for_subject(file_path, white_list, voxel_size=0.8)
        all_volumes_list.append(vols)

        if (index + 1) % 50 == 0:
            print(f"已处理 {index + 1} / {len(df)} 名被试...")

    df_volumes = pd.DataFrame(all_volumes_list)
    df_final = pd.concat([df, df_volumes], axis=1)

    df_final.to_csv(output_csv, index=False)
    print(f"\n提取完成！特征数据已保存至: {output_csv}")


BIDS_ROOT_DIR = "/public/home/wangjiaqi2/BIDS_DATA/MRI_smri_prep_20250829/v1"
SUBJECT_CSV = "common_subjects_with_age.csv"
OUTPUT_CSV = "subject_features_gmv.csv"

batch_process_gmv(SUBJECT_CSV, BIDS_ROOT_DIR, OUTPUT_CSV)
