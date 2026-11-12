# KitchenSum 🍳
**Predictive Cloud Resource Allocation for Food-Delivery Workloads**

KitchenSum is an educational cloud-computing prototype featuring a FastAPI order API, React dashboard, synthetic workload generator, Random Forest predictor, Prometheus monitoring and opt-in Kubernetes replica scaling.

## Quick start (macOS / Linux / Windows with Docker Desktop)

```bash
# Optional: train a model locally first (Python 3.11 recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install scikit-learn joblib numpy
python ml/train.py

docker compose up --build
```

Open dashboard at **http://localhost:5173**, API docs at **http://localhost:8000/docs**, Prometheus at **http://localhost:9090**.

The app runs without a trained model using a baseline predictor. For trained predictions, train before building the backend image and rebuild with `docker compose up --build`.

### Simulate sustained load
```bash
pip install requests
python simulator/load.py --rate 20 --seconds 30
```
Or use Locust:
```bash
pip install locust
locust -f simulator/locustfile.py --host http://localhost:8000
```

### Kubernetes (local kind / minikube)
```bash
docker build -t kitchensum-api:latest backend
# For kind: kind load docker-image kitchensum-api:latest
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/deployment.yaml
kubectl port-forward svc/kitchensum-api 8000:8000
kubectl get pods -w
```
For a real cluster, push the image to your container registry and change `image` in the deployment. The deployment defaults to `ENABLE_SCALING=false` (safe dry-run). To allow replica changes, set it to `true` in the deployment and apply again. **Protect the scaling endpoint with authentication before exposing it publicly.** Do not run a competing HPA on the same Deployment while testing the custom scaler.

### AWS deployment
Deploy the image to an EC2 VM with Docker Compose or use EKS for Kubernetes. Configure registry, VPC, IAM, secrets, security groups and TLS. These steps require your own AWS account and are not performed by this package. Kubernetes manifests are a starting point, not a production-hardened deployment.

## Project structure
- `backend/` REST API, metrics, prediction, scaling controller
- `frontend/` React dashboard
- `ml/` synthetic-data generator and Random Forest training
- `simulator/` load generator and Locust workload
- `monitoring/` Prometheus scrape configuration
- `k8s/` Deployment, Service, service-account permissions
- `tests/` smoke tests

## Academic experiment
Compare baseline fixed replicas, reactive CPU-threshold scaling, and predictive scaling on identical workloads. Measure p95 latency, failed requests, pod-minutes and scale-up delay. Record results; **do not claim predictive scaling wins before testing**. Synthetic training data is for demonstration only; real traffic traces will improve validity.

## Important limitations
- The UI's simulator sends a finite burst, not a sustained 10-minute workload. Use Locust for real stress tests.
- Dashboard order counts are per-process in-memory counters and may not represent total cluster traffic; use Prometheus aggregation across pods for distributed monitoring.
- `POST /scale/{replicas}` is a manual scaling action based on the displayed prediction. An autonomous periodic controller and HPA comparison remain extensions, not completed features.
- The prototype does not provide production-grade auth, TLS, rate limiting or persistent cluster-wide workload history.
