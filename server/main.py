import io
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, __version__, UploadFile, Query
from pydantic import BaseModel, conint, Field, confloat
from scipy.io import wavfile
from starlette.responses import StreamingResponse

from configs.config import Config, logger
from infer.modules.vc.modules import VC

vrc_info = {}

logger.warning(f"__version__: {__version__}")
app = FastAPI(title='charspeak_rvc')


@app.on_event("startup")
async def startup_event():
    logger.info('Loading dotenv...')
    load_dotenv()
    logger.info('Creating config...')
    config = Config()
    logger.info('Initializing VC...')
    vc = VC(config)
    logger.info('Loading experiment path...')
    vc.get_vc('experiment_1_e185_s2960.pth')
    vrc_info['vc'] = vc
    logger.info('VC loaded successfully.')


@app.get('/ping')
def ping():
    logger.info(vrc_info)
    return 'pong'


class InferConvert(BaseModel):
    speaker_id: conint(ge=0, le=2333) = Field(
        0,
        description="Select Speaker/Singer ID")
    # audio_path: str = Field(
    #     description="Enter the path of the audio file to be processed (default is the correct format example)"
    # )
    transpose: int = Field(
        0,
        description="Transpose (integer, number of semitones, raise by an octave: 12, lower by an octave: -12)")

    curve_file: Optional[str] = Field(
        None,
        description="F0 curve file (optional). One pitch per line. Replaces the default F0 and pitch modulation."
    )
    pm: str = Field(
        "rmvpe",
        description="""
Select the pitch extraction algorithm:
'pm': faster extraction but lower-quality speech;
'harvest': better bass but extremely slow;
'crepe': better quality but GPU intensive),
'rmvpe': best quality, and little GPU requirement'
"""
    )
    feature_index_file: Optional[str] = Field(
        None,
        description="Path to the feature index file.",
    )
    search_feature_ratio: confloat(ge=0, le=1) = Field(
        0.75,
        description="Search feature ratio (controls accent strength, too high has artifacting)",
    )
    filter_radius: confloat(ge=0, le=7) = Field(
        3,
        description="If >=3: apply median filtering to the harvested pitch results. "
                    "The value represents the filter radius and can reduce breathiness."
    )
    resample_sr: confloat(ge=0, le=48000) = Field(
        0,
        description="Resample the output audio in post-processing to the final sample rate. Set to 0 for no resampling."
    )
    rms_mix_rate: confloat(ge=0, le=1) = Field(
        0.25,
        description="Adjust the volume envelope scaling. "
                    "Closer to 0, the more it mimicks the volume of the original vocals. "
                    "Can help mask noise and make volume sound more natural when set relatively low. "
                    "Closer to 1 will be more of a consistently loud volume."
    )

    protection: confloat(ge=0, le=0.5) = Field(
        0.33,
        description="Protect voiceless consonants and breath sounds to prevent artifacts "
                    "such as tearing in electronic music. Set to 0.5 to disable. "
                    "Decrease the value to increase protection, but it may reduce indexing accuracy."
    )

    def get_args(self, input_file: str):
        # assert self.feature_index_file.exists()
        return (
            self.speaker_id,
            input_file,
            self.transpose,
            self.curve_file,
            self.pm,
            self.feature_index_file,
            None,
            self.search_feature_ratio,
            self.filter_radius,
            self.resample_sr,
            self.rms_mix_rate,
            self.protection,
        )


@app.post('/infer')
async def make_inference(
        input_file: UploadFile,
        speaker_id: conint(ge=0, le=2333) = Query(
            0,
            description="Select Speaker/Singer ID"),
        # audio_path: str = Field(
        #     description="Enter the path of the audio file to be processed (default is the correct format example)"
        # )
        transpose: int = Query(
            0,
            description="Transpose (integer, number of semitones, raise by an octave: 12, lower by an octave: -12)"),

        curve_file: Optional[str] = Query(
            None,
            description="F0 curve file (optional). One pitch per line. Replaces the default F0 and pitch modulation."
        ),
        pm: str = Query(
            "rmvpe",
            description="""
        Select the pitch extraction algorithm:
        'pm': faster extraction but lower-quality speech;
        'harvest': better bass but extremely slow;
        'crepe': better quality but GPU intensive),
        'rmvpe': best quality, and little GPU requirement'
        """
        ),
        feature_index_file: Optional[str] = Query(
            None,
            description="Path to the feature index file.",
        ),
        search_feature_ratio: confloat(ge=0, le=1) = Query(
            0.75,
            description="Search feature ratio (controls accent strength, too high has artifacting)",
        ),
        filter_radius: confloat(ge=0, le=7) = Query(
            3,
            description="If >=3: apply median filtering to the harvested pitch results. "
                        "The value represents the filter radius and can reduce breathiness."
        ),
        resample_sr: confloat(ge=0, le=48000) = Query(
            0,
            description="Resample the output audio in post-processing to the final sample rate. Set to 0 for no resampling."
        ),
        rms_mix_rate: confloat(ge=0, le=1) = Query(
            0.25,
            description="Adjust the volume envelope scaling. "
                        "Closer to 0, the more it mimicks the volume of the original vocals. "
                        "Can help mask noise and make volume sound more natural when set relatively low. "
                        "Closer to 1 will be more of a consistently loud volume."
        ),

        protection: confloat(ge=0, le=0.5) = Query(
            0.33,
            description="Protect voiceless consonants and breath sounds to prevent artifacts "
                        "such as tearing in electronic music. Set to 0.5 to disable. "
                        "Decrease the value to increase protection, but it may reduce indexing accuracy."
        ),
):
    path = '/storage/input_qwe.wav'
    with open(path, 'wb') as file:
        file.write(input_file.file.read())

    # infer_convert = infer_convert or InferConvert()
    # # args = arg_parse()
    _, (rate, data) = vrc_info['vc'].vc_single(
        speaker_id,
        path,
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
    out = io.BytesIO()
    # out = '/storage/qwe.wav'
    wavfile.write(out, rate, data)
    out.seek(0)
    return StreamingResponse(out, media_type="audio/wav")
