# Lab-06 – Containerized Build Stage Automation (Linear Regression API)

How evaluation works: the instructor's script checks your API is **DOWN** → pushes a commit to your repo →
GitHub webhook triggers Jenkins → pipeline runs `docker compose up -d` → after 3 min the script checks the API is **UP** and the prediction is correct.
So the API must be **off** when you submit, and the **webhook push** must turn it **on**.

```
lab06-repo/
├── app/
│   ├── app.py            # Flask API  (edit REGISTRATION_NUMBER + STUDENT_ROLL_NUMBER)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml    # edit image name
├── Jenkinsfile           # Build stage: compose down -> up -d -> smoke test
└── ec2-setup.sh          # one-time Jenkins + Docker install on EC2
```

---

## Step 1 – Put in your details

`app/app.py`
```python
REGISTRATION_NUMBER = "FA23-BDS-049"
STUDENT_ROLL_NUMBER = 49
```
`docker-compose.yml`
```yaml
image: <your-dockerhub-username>/lr-predict-api:v1
```

## Step 2 – EC2 instance

- Ubuntu 22.04/24.04, **t3.small or bigger** (Jenkins struggles on t2.micro), 15–20 GB disk.
- Security group inbound: **22**, **8080** (Jenkins), **5000** (API) from `0.0.0.0/0`.
- Recommended: attach an **Elastic IP** so the public IP doesn't change before evaluation.

SSH in, copy `ec2-setup.sh` over (or paste it) and run:
```bash
bash ec2-setup.sh
exit        # log back in so 'ubuntu' gets docker group
```
Open `http://<EC2_IP>:8080`, paste the admin password, **Install suggested plugins** (includes Git, GitHub, Pipeline), create admin user.

## Step 3 – Build & push the image to Docker Hub (on the EC2)

```bash
git clone https://github.com/<you>/<repo>.git && cd <repo>/app
docker login                                  # Docker Hub username + access token
docker build -t <dockerhub-user>/lr-predict-api:v1 .
docker push <dockerhub-user>/lr-predict-api:v1
```
Building on the EC2 avoids the Apple-Silicon/amd64 mismatch. (If you build on an M1/M2 Mac instead, use
`docker buildx build --platform linux/amd64 -t ... --push .`)

Quick local check before pushing:
```bash
docker run --rm -d -p 5000:5000 --name t <dockerhub-user>/lr-predict-api:v1
curl "http://localhost:5000/predict?x1=2&x2=3&x3=1"
docker rm -f t
```

## Step 4 – GitHub repo

1. Create a **public** repo, push all files (branch `main`).
2. Settings → Collaborators → add **qasimalik@gmail.com** (write access).
3. Settings → Webhooks → **Add webhook**
   - Payload URL: `http://<EC2_IP>:8080/github-webhook/`  ← trailing slash matters
   - Content type: `application/json`
   - Event: **Just the push event** → Add. Check it shows a green ✔ after the first delivery.

## Step 5 – Jenkins pipeline job

New Item → name `lab06-lr-api` → **Pipeline** → OK
- Build Triggers: ✅ **GitHub hook trigger for GITScm polling**
- Pipeline → Definition: **Pipeline script from SCM**
  - SCM: Git, Repository URL: `https://github.com/<you>/<repo>.git`
  - Branch: `*/main`, Script Path: `Jenkinsfile`
- Save → **Build Now** once (this first manual run registers the webhook trigger).

Console output should end with the JSON and `API is UP`. Check from your browser:
`http://<EC2_IP>:5000/predict?x1=2&x2=3&x3=1`

## Step 6 – Test the trigger yourself

```bash
# 1) bring it DOWN
sudo docker rm -f lr-predict-api        # or: docker compose -p lr-api down
curl http://<EC2_IP>:5000/predict?x1=2&x2=3&x3=1   # should fail (connection refused)

# 2) push a commit from your laptop
git commit --allow-empty -m "trigger test" && git push
```
Jenkins should start a build on its own within seconds and the API comes back UP.

## Step 7 – Leave it DOWN and submit ⚠️

```bash
sudo docker rm -f lr-predict-api
```
Confirm the URL fails, then submit the Google form with: GitHub repo URL, EC2 public IP, image `user/lr-predict-api:v1`.
Keep the EC2 instance **running** (and Jenkins up) until evaluation is done.

---

### Troubleshooting

| Symptom | Fix |
|---|---|
| `permission denied ... docker.sock` in Jenkins | `sudo usermod -aG docker jenkins && sudo systemctl restart jenkins` |
| `docker: 'compose' is not a docker command` | Docker wasn't installed from get.docker.com — install `docker-compose-plugin` |
| Webhook red ✖ in GitHub | Port 8080 not open, wrong IP, or missing `/github-webhook/` trailing slash |
| Push doesn't start a build | Run one manual **Build Now** first; make sure the hook-trigger checkbox is ticked |
| `exec format error` in container | Image was built on ARM Mac — rebuild with `--platform linux/amd64` |
| `Conflict. The container name ... is already in use` | `sudo docker rm -f lr-predict-api` then rebuild |
