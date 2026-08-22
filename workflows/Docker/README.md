# Docker Build and Push Workflow

This workflow automatically builds, tags, and pushes Docker images to GitHub Container Registry (GHCR) on every push to `main` or when semantic version tags are created.

## Features

- **Multi-platform builds**: Builds for both `linux/amd64` and `linux/arm64` architectures
- **Automatic tagging**:
  - Branch name (e.g., `main`)
  - Pull request number
  - Semantic versions (e.g., `v1.2.3`, `v1.2`)
  - Commit SHA
- **Image signing**: Uses Cosign to sign images for supply chain security
- **Build caching**: Leverages GitHub Actions cache for faster builds
- **PR validation**: Builds but doesn't push on pull requests

## Prerequisites

1. **Dockerfile**: Ensure you have a `Dockerfile` in your repository root
2. **Package permissions**: Enable "Read and write" permissions for packages:
   - Go to Repository Settings → Actions → General
   - Under "Workflow permissions", select "Read and write permissions"
   - Or add this to your workflow file (already included)

## Usage

### Automatic Deployment
Push to `main` branch:
```bash
git push origin main
```

### Release with Version Tag
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Manual Trigger
Go to Actions tab → "Docker Build and Push" → "Run workflow"

## Image Names

Images are pushed to GHCR with the following naming convention:
```
ghcr.io/<owner>/<repo>:<tag>
```

Examples:
- `ghcr.io/username/myapp:main`
- `ghcr.io/username/myapp:v1.0.0`
- `ghcr.io/username/myapp:sha-abc123`

## Customization

### Change Registry
To use Docker Hub instead of GHCR, modify the `REGISTRY` env var:
```yaml
env:
  REGISTRY: docker.io
```

Add Docker Hub credentials as secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Update the login step:
```yaml
- name: Log into registry
  uses: docker/login-action@v3.3.0
  with:
    registry: docker.io
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### Add More Platforms
Edit the `platforms` parameter:
```yaml
platforms: linux/amd64,linux/arm64,linux/arm/v7
```

### Custom Dockerfile Path
Change the `file` parameter:
```yaml
file: ./docker/Dockerfile.prod
```

## Viewing Your Images

After a successful run, view your container images at:
```
https://github.com/<owner>/<repo>/pkgs/container/<repo>
```

## Pulling the Image

```bash
docker pull ghcr.io/<owner>/<repo>:main
```

Or with authentication:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin
docker pull ghcr.io/<owner>/<repo>:main
```

## Security

- Images are signed using [Sigstore Cosign](https://github.com/sigstore/cosign)
- Transparency data is logged to Rekor (for public repositories)
- No secrets are exposed in logs

## Troubleshooting

### Permission Denied
Ensure "Read and write" permissions are enabled for packages in repository settings.

### Build Too Slow
- Enable build caching (already configured)
- Use multi-stage builds in your Dockerfile
- Reduce image layers

### Multi-arch Build Fails
Ensure your Dockerfile supports all target architectures or remove unsupported platforms.
