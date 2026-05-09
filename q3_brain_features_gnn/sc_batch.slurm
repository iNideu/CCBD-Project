#!/bin/bash
#SBATCH --job-name=SC_Matrix_Build
#SBATCH --partition=brain_compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:20:00
#SBATCH --array=1-673%100
#SBATCH --output=logs/%x_%A_%a.out
#SBATCH --error=logs/%x_%A_%a.err

WORK_DIR="/public/home/wangjiaqi2/zyz_analysis_v2/Q3"
BIDS_ROOT="/public/home/wangjiaqi2/BIDS_DATA/MRI_dmri_prep_20250829/v1"
ATLAS_ROOT="/public/home/wangjiaqi2/BIDS_DATA/MRI_smri_prep_20250829/v1"

LIST_FILE="${WORK_DIR}/subject_list.txt"
VOL_CSV="${WORK_DIR}/subject_features_gmv.csv"
PY_SCRIPT="${WORK_DIR}/process_single_sc.py"

OUT_DIR="${WORK_DIR}/SC_Matrices"
mkdir -p "${OUT_DIR}"
mkdir -p logs

NUM_SUBS=$(wc -l < "${LIST_FILE}")
if [ "${SLURM_ARRAY_TASK_ID}" -gt "${NUM_SUBS}" ]; then
    echo "Task ID ${SLURM_ARRAY_TASK_ID} exceeds file length ${NUM_SUBS}"
    exit 0
fi

SUB_ID=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "${LIST_FILE}")

if [[ -z "${SUB_ID}" ]]; then
    echo "Error: Failed to retrieve subject ID."
    exit 1
fi

echo "=========================================="
echo "Processing Subject: ${SUB_ID}"
echo "Node: $(hostname)"
echo "=========================================="

module load singularity

TCK_FILE="${BIDS_ROOT}/${SUB_ID}/dwi/fibtrk_metric/${SUB_ID}_acq-hardi_space-T1w_desc-preproc_desc-tracks_ifod2.tck"
WEIGHTS_FILE="${BIDS_ROOT}/${SUB_ID}/dwi/fibtrk_metric/${SUB_ID}_acq-hardi_space-T1w_desc-preproc_desc-siftweights_ifod2.csv"
ATLAS_FILE="${ATLAS_ROOT}/${SUB_ID}/anat/prep/${SUB_ID}_desc-aparcaseg_dseg.nii.gz"

RAW_CSV="${OUT_DIR}/${SUB_ID}_sc_raw.csv"
FINAL_NPY="${OUT_DIR}/${SUB_ID}_sc_final.npy"

if [ ! -f "${TCK_FILE}" ] || [ ! -f "${ATLAS_FILE}" ]; then
    echo "Error: Missing input files for ${SUB_ID}"
    exit 1
fi

echo "Running tck2connectome..."
tck2connectome "${TCK_FILE}" "${ATLAS_FILE}" "${RAW_CSV}" \
    -tck_weights_in "${WEIGHTS_FILE}" \
    -assignment_radial_search 2 -force

echo "Running Python matrix processing..."
python "${PY_SCRIPT}" "${RAW_CSV}" "${SUB_ID}" "${VOL_CSV}" "${FINAL_NPY}"

rm -f "${RAW_CSV}"

echo "Finished ${SUB_ID} successfully."
