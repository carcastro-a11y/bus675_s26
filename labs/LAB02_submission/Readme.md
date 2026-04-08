# Lab 2 Submission README

## Student Information
- Name: Carlo Castro
- Date: 2026-04-07

## Deliverables Included
- `inference_api/Dockerfile`
- `preprocessor/Dockerfile`
- `inference_api/app.py` (with `/health` and `/stats`)
- `sample_classifications_20.jsonl` (first 20 lines from logs)
- `Reflection.md`

## Docker Build Commands Used

### Inference API
```bash
cd LAB02_submission/inference_api
docker build -t congo-inference-api .
```

### Preprocessor
```bash
cd LAB02_submission/preprocessor
docker build -t congo-preprocessor .
```

## Docker Run Commands Used

### Inference API Container
```bash
docker run -d \
  --name inference-api \
  -p 8000:8000 \
  -v ~/logs:/logs \
  congo-inference-api
```

### Preprocessor Container
```bash
docker run -d \
  --name preprocessor \
  -v ~/incoming:/incoming \
  -e API_URL=http://host.docker.internal:8000 \
  congo-preprocessor
```

## Brief Explanation: How the Containers Communicate

The preprocessor container watches the host's `~/incoming/` folder (bind-mounted to `/incoming` inside the container) for new image files. When it detects one, it reads the filename to extract `customer_id` and `product_id`, then sends the image as a multipart HTTP POST to the inference API's `/predict` endpoint. The inference API URL is injected at runtime via the `API_URL` environment variable, set to `http://host.docker.internal:8000`. The special hostname `host.docker.internal` is provided by Docker Desktop on macOS and resolves to the host machine's IP, this is necessary because from inside a container, `localhost` refers to that container itself, not the host. The inference API writes a JSON log entry for each classification to `/logs/classifications.jsonl`, which is bind-mounted from the host's `~/logs/` folder, so log data persists even if the container is stopped or replaced. The two containers never communicate directly with each other; all coordination flows through the host's filesystem (for images and logs) and HTTP over the host network.

