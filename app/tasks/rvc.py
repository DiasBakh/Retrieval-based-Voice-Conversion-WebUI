import os

from loguru import logger
import io
from typing import Optional

from celery import Task as _Task
from dotenv import load_dotenv
from scipy.io import wavfile

from app.celery import app
from configs.config import Config
from infer.lib.rmvpe import RMVPE
from infer.modules.vc.modules import VC
from infer.modules.vc.pipeline import Pipeline
from infer.modules.vc.utils import load_hubert


class Task(_Task):
    name = 'rvc'
    queue = 'rvc'

    vc = None
    max_retries = 0
    current_model_name: str = None

    tgt_sr: int = 40000

    def run_rvc(self, *args) -> io.BytesIO:
        _, (rate, data) = self.vc.vc_single(*args)
        out = io.BytesIO()
        wavfile.write(out, rate, data)
        out.seek(0)
        return out

    def run(self, model_name: str = None, *args) -> Optional[io.BytesIO]:

        if self.vc is None:
            logger.info(f'Loading vc...')
            load_dotenv()
            self.vc = VC(config=Config())
            self.vc.hubert_model = load_hubert(self.vc.config)
            self.vc.pipeline = Pipeline(self.tgt_sr, self.vc.config)
            self.vc.pipeline.model_rmvpe = RMVPE(
                f"{os.environ['rmvpe_root']}/rmvpe.pt",
                is_half=self.vc.pipeline.is_half,
                device=self.vc.pipeline.device,
            )
            logger.info(f'VC+Hubert+RMVPE loaded successfully.')

        if model_name is None:
            return
        if self.current_model_name != model_name:
            logger.info(f'Loading {model_name}...')
            self.vc.get_vc(f"{model_name}.pth")

            assert self.vc.tgt_sr == self.tgt_sr
            self.current_model_name = model_name

        return self.run_rvc(*args)


task = Task()
app.register_task(task)
