import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import io
import uuid
import boto3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ===============================
#  CONFIG (cho MinIO / S3)
# ===============================

S3_BUCKET = os.getenv("S3_BUCKET", "charts")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_PREFIX = os.getenv("S3_PREFIX", "charts")

# MinIO endpoint (vd: http://localhost:9000)
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")


# ===============================
#  UPLOAD HELPER
# ===============================

def upload_bytes_to_s3(bytes_data: bytes, filename: str, content_type="image/png"):
    """
    Upload ảnh lên MinIO hoặc S3, trả về URL công khai.
    """
    s3 = boto3.client(
        "s3",
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
    )

    key = f"{S3_PREFIX}/{filename}"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=bytes_data,
        ContentType=content_type,
        ACL="public-read"  # Cho phép truy cập trực tiếp (tạm thời, bạn có thể thay bằng presigned URL)
    )

    # Nếu dùng MinIO local
    if S3_ENDPOINT.startswith("http://localhost") or "127.0.0.1" in S3_ENDPOINT:
        return f"{S3_ENDPOINT}/{S3_BUCKET}/{key}"
    else:
        return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"


# ===============================
#  CHART GENERATION + UPLOAD
# ===============================

def run_plot_code_and_upload(data_records, chart_type="line", x_field="date", y_field="close"):
    """
    Vẽ chart (line/bar) theo dữ liệu và upload lên MinIO/S3.
    Trả về URL công khai của ảnh.
    """
    if not data_records or not isinstance(data_records, list):
        raise ValueError("data_records must be a non-empty list of dicts")

    df = pd.DataFrame(data_records)

    if x_field not in df.columns or y_field not in df.columns:
        raise ValueError(f"Missing required fields for chart: {x_field}, {y_field}")

    # Convert date field nếu có
    if "date" in x_field.lower():
        try:
            df[x_field] = pd.to_datetime(df[x_field])
        except Exception:
            pass

    # Vẽ chart
    fig, ax = plt.subplots(figsize=(8, 4))
    if chart_type == "line":
        ax.plot(df[x_field], df[y_field], marker="o", linewidth=2)
    elif chart_type == "bar":
        ax.bar(df[x_field], df[y_field])
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    ax.set_title(f"{y_field.capitalize()} vs {x_field.capitalize()}")
    ax.set_xlabel(x_field.capitalize())
    ax.set_ylabel(y_field.capitalize())
    plt.tight_layout()

    # Lưu ảnh vào buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    # Upload lên MinIO/S3
    filename = f"chart_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}.png"
    url = upload_bytes_to_s3(buf.read(), filename)
    return url
