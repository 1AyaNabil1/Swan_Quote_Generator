# GitHub Actions Workflows

This directory contains the CI/CD workflows for the AI Quote Generator project.

## Workflows

### 1. CI Pipeline (`ci.yml`)

Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**

- **Backend Tests**: Runs pytest on Python 3.10 and 3.11
  - Unit tests
  - Integration tests (non-slow tests)
  
- **Frontend Tests & Build**: 
  - Installs Node.js dependencies
  - Builds the React application
  - Uploads build artifacts
  
- **Python Linting**:
  - Flake8 (PEP8 compliance)
  - Black (code formatting)
  - isort (import ordering)
  
- **Docker Build**: (only on main branch pushes)
  - Tests Docker image builds
  - Uses build cache for efficiency
  
- **Security Scanning**:
  - Trivy vulnerability scanner
  - Uploads results to GitHub Security tab

### 2. Deploy Pipeline (`deploy.yml`)

Runs on pushes to `main` branch or version tags.

**Jobs:**

- **Deploy**: Deploys to Vercel (or your preferred platform)

## Setup Instructions

### Required Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

#### For Vercel Deployment:

1. **VERCEL_TOKEN**: Your Vercel authentication token
   - Get it from: https://vercel.com/account/tokens
   
2. **VERCEL_ORG_ID**: Your Vercel organization ID
   - Run: `vercel whoami` or find in project settings
   
3. **VERCEL_PROJECT_ID**: Your Vercel project ID
   - Find in project settings on Vercel dashboard

### Optional Secrets

- **GEMINI_API_KEY**: If you need it for integration tests
- **REDIS_URL**: If running integration tests that require Redis

## Running Workflows

### Automatic Triggers:

- Push to `main` or `develop`: Runs full CI pipeline
- Pull request to `main` or `develop`: Runs full CI pipeline
- Push tag `v*`: Runs CI and deployment

### Manual Trigger:

You can manually trigger workflows from the Actions tab:
1. Go to Actions tab in GitHub
2. Select the workflow
3. Click "Run workflow"
4. Choose the branch

## Local Testing

Before pushing, you can run the tests locally:

```bash
# Backend tests
pytest tests/unit -v
pytest tests/integration -v

# Frontend build
cd app/static
npm install
npm run build

# Linting
pip install flake8 black isort
flake8 app/ tests/
black --check app/ tests/
isort --check-only app/ tests/

# Docker build
docker build -t ai-quote-generator .
```

## Status Badges

Add these to your main README.md:

```markdown
[![CI Pipeline](https://github.com/1AyaNabil1/Swan_Quote_Generator/actions/workflows/ci.yml/badge.svg)](https://github.com/1AyaNabil1/Swan_Quote_Generator/actions/workflows/ci.yml)
[![Deploy](https://github.com/1AyaNabil1/Swan_Quote_Generator/actions/workflows/deploy.yml/badge.svg)](https://github.com/1AyaNabil1/Swan_Quote_Generator/actions/workflows/deploy.yml)
```

## Troubleshooting

### Common Issues:

1. **Tests failing**: Check the logs in the Actions tab
2. **Build failing**: Ensure package-lock.json is committed
3. **Deployment failing**: Verify all secrets are set correctly
4. **Cache issues**: Clear GitHub Actions cache in Settings → Actions → Caches

### Skipping CI:

Add `[skip ci]` to your commit message to skip workflows:
```bash
git commit -m "Update docs [skip ci]"
```

## Workflow Optimization

The workflows use several optimization techniques:

- **Caching**: pip and npm dependencies are cached
- **Matrix builds**: Tests run in parallel on multiple Python versions
- **Conditional jobs**: Docker build only runs on main branch
- **Artifact uploads**: Frontend builds are saved for 7 days
- **Continue-on-error**: Non-critical checks don't block the pipeline

## Updating Workflows

When modifying workflows:

1. Test changes on a feature branch first
2. Use `workflow_dispatch` trigger for manual testing
3. Check the Actions tab for syntax errors
4. Update this README if adding new jobs or secrets

---

<div align="center">
  <em>Built by AyaNexus 🦢</em>
</div>