#!/bin/bash
#SBATCH --job-name=sc_test
#SBATCH --partition=demo_compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --output=logs/%j_sc_test.out
#SBATCH --error=logs/%j_sc_test.err

module load singularity

SIF_IMAGE="/public/share/all/ccbd_qsiprep_v1.0.2.sif"
BIND_ARGS="-B /public/home/wangjiaqi2:/public/home/wangjiaqi2"

SUB_ID="sub-44gauv"

WORK_DIR="/public/home/wangjiaqi2/zyz_analysis_v2/Q3"
HOST_DWI_PATH="/public/home/wangjiaqi2/BIDS_DATA/MRI_dmri_prep_20250829/v1"
HOST_SMRI_PATH="/public/home/wangjiaqi2/BIDS_DATA/MRI_smri_prep_20250829/v1"
HOST_OUT_PATH="${WORK_DIR}/SC_Matrices_Demo"

PY_SCRIPT="${WORK_DIR}/process_single_sc.py"
VOL_CSV="${WORK_DIR}/subject_features_gmv.csv"

mkdir -p logs
mkdir -p "${HOST_OUT_PATH}"

TCK_FILE="${HOST_DWI_PATH}/${SUB_ID}/dwi/fibtrk_metric/${SUB_ID}_acq-hardi_space-T1w_desc-preproc_desc-tracks_ifod2.tck"
WEIGHTS_FILE="${HOST_DWI_PATH}/${SUB_ID}/dwi/fibtrk_metric/${SUB_ID}_acq-hardi_space-T1w_desc-preproc_desc-siftweights_ifod2.csv"
ATLAS_FILE="${HOST_SMRI_PATH}/${SUB_ID}/anat/prep/${SUB_ID}_desc-aparcaseg_dseg.nii.gz"

RAW_CSV="${HOST_OUT_PATH}/${SUB_ID}_sc_raw.csv"
FINAL_NPY="${HOST_OUT_PATH}/${SUB_ID}_sc_final.npy"

echo "=========================================="
echo "Starting job on node: $(hostname)"
echo "Processing Subject: ${SUB_ID}"
echo "=========================================="

if [ ! -f "${TCK_FILE}" ]; then
    echo "Error: 找不到 TCK 文件 -> ${TCK_FILE}"
    exit 1
fi
if [ ! -f "${ATLAS_FILE}" ]; then
    echo "Error: 找不到图谱文件 -> ${ATLAS_FILE}"
    exit 1
fi

echo "[1/2] 正在容器内运行 tck2connectome 提取原始矩阵..."
singularity exec ${BIND_ARGS} ${SIF_IMAGE} \
    tck2connectome "${TCK_FILE}" "${ATLAS_FILE}" "${RAW_CSV}" \
    -tck_weights_in "${WEIGHTS_FILE}" \
    -assignment_radial_search 2 -force

echo "[2/2] 正在容器内运行 Python 脚本进行后处理..."
singularity exec ${BIND_ARGS} ${SIF_IMAGE} \
    python "${PY_SCRIPT}" "${RAW_CSV}" "${SUB_ID}" "${VOL_CSV}" "${FINAL_NPY}"

if [ -f "${FINAL_NPY}" ]; then
    echo "矩阵处理成功！清理临时文件..."
    rm -f "${RAW_CSV}"
else
    echo "Error: 最终 NPY 文件生成失败！"
fi

echo "Job finished completely at $(date)"
