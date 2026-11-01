import argparse
import hashlib
import os
from pathlib import Path
import tempfile
from urllib.request import urlopen


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
CHUNK_SIZE = 1024 * 1024


def download_model(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        if _sha256(destination) != MODEL_SHA256:
            raise ValueError(f"Existing model checksum does not match: {destination}")
        return destination

    digest = hashlib.sha256()
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            with urlopen(MODEL_URL, timeout=60) as response:
                while chunk := response.read(CHUNK_SIZE):
                    digest.update(chunk)
                    temporary_file.write(chunk)

        if digest.hexdigest() != MODEL_SHA256:
            raise ValueError("Downloaded hand-landmarker model checksum mismatch")

        os.chmod(temporary_path, 0o644)
        os.replace(temporary_path, destination)
        temporary_path = None
        return destination
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as model_file:
        while chunk := model_file.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and verify the pinned MediaPipe hand-landmarker model."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "models"
        / "hand_landmarker.task",
    )
    args = parser.parse_args()
    model_path = download_model(args.output)
    print(f"Verified MediaPipe hand-landmarker model: {model_path}")


if __name__ == "__main__":
    main()
