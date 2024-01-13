import io
import os
from pathlib import Path

import faiss
from dotenv import load_dotenv
from loguru import logger
from scipy.io import wavfile

from configs.config import Config
from infer.lib.rmvpe import RMVPE
from infer.modules.vc.modules import VC
from infer.modules.vc.pipeline import Pipeline
from infer.modules.vc.utils import load_hubert


def main():
    tgt_sr = 40000
    model_name = 'experiment_1_e185_s2960'
    speaker_id = 0
    tmp_path = '/storage/generated.wav'
    transpose = 0
    curve_file = None
    pm = 'rmvpe'
    feature_index_file = '/storage/logs/added_IVF209_Flat_nprobe_1_experiment_1_v2.index'
    # feature_index_file = None
    # feature_index_file2 = None
    # feature_index_file2 = '/storage/logs/added_IVF209_Flat_nprobe_1_experiment_1_v2.index'
    # index = faiss.read_index(feature_index_file2)
    # big_npy = index.reconstruct_n(0, index.ntotal)
    # print(big_npy.shape)
    # print(big_npy)
    # return
    search_feature_ratio = 0.75
    filter_radius = 3
    resample_sr = 0
    rms_mix_rate = 0.25
    protection = 0.33

    args = (
        speaker_id,
        str(tmp_path),
        transpose,
        curve_file,
        pm,
        feature_index_file,
        None,
        search_feature_ratio,
        filter_radius,
        resample_sr,
        rms_mix_rate,
        protection,
    )
    load_dotenv()
    vc = VC(config=Config())
    vc.hubert_model = load_hubert(vc.config)
    vc.pipeline = Pipeline(tgt_sr, vc.config)
    vc.pipeline.model_rmvpe = RMVPE(
        f"{os.environ['rmvpe_root']}/rmvpe.pt",
        is_half=vc.pipeline.is_half,
        device=vc.pipeline.device,
    )
    logger.info(f'VC+Hubert+RMVPE loaded successfully.')
    vc.get_vc(f"{model_name}.pth")

    _, (rate, data) = vc.vc_single(*args)
    # out = io.BytesIO()

    with open(f'{Path(tmp_path).stem}_index_file={bool(feature_index_file)}.wav', 'wb') as file:
        wavfile.write(file, rate, data)
    # out.seek(0)

    pass


if __name__ == '__main__':
    main()
