# Q3 - 脑功能、脑结构特征

Notion 当前分类：

- 图神经网络（GNN）
- 灰质体积
- DTI / 结构连接矩阵

## Files

- `extract_gmv.py` - 从 aparcaseg 图谱中提取 ROI 灰质体积。
- `sc_test.slurm` - 单被试结构连接矩阵 demo 任务。
- `sc_batch.slurm` - SLURM array 批处理结构连接矩阵任务。
- `process_single_sc.py` - 裁剪、体积归一化、稀疏化、Min-Max 缩放结构连接矩阵。
- `multimodal_gnn_notes.md` - Notion 中关于 FC、SC、sMRI、INT、SC-FC Coupling 与 MaskGNN 融合的设计说明。
