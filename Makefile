.PHONY: build deploy test lint clean invoke-local requirements

# ─── Development ─────────────────────────────────────────────────────
test:
	uv run pytest -v

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff format src/ tests/

# ─── SAM Build & Deploy ─────────────────────────────────────────────

# Regenerate requirements.txt from pyproject.toml
requirements:
	uv pip compile pyproject.toml -o src/requirements.txt --no-header

# Build Lambda package (generates .aws-sam/)
build: requirements
	sam build

# Deploy to AWS (requires prior `sam deploy --guided` for first run)
deploy: build
	sam deploy

# First-time deploy — interactive, prompts for all parameters
deploy-guided: build
	sam deploy --guided

# ─── Local Testing ───────────────────────────────────────────────────

# Invoke Lambda locally via SAM (requires Docker)
invoke-local: build
	sam local invoke ScraperFunction --event events/schedule.json

# ─── Production Utilities ────────────────────────────────────────────

# Manually trigger the Lambda in AWS
invoke-remote:
	aws lambda invoke \
		--function-name agenda-rouen-scraper \
		--invocation-type Event \
		--payload '{}' \
		/dev/null

# Invalidate CloudFront cache
invalidate-cache:
	@DIST_ID=$$(aws cloudformation describe-stacks \
		--stack-name agenda-rouen \
		--query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" \
		--output text) && \
	aws cloudfront create-invalidation \
		--distribution-id $$DIST_ID \
		--paths "/api/v1/*"

# Stream Lambda logs
logs:
	sam logs --name ScraperFunction --stack-name agenda-rouen --tail

# Print the CloudFront URL
url:
	@aws cloudformation describe-stacks \
		--stack-name agenda-rouen \
		--query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomain'].OutputValue" \
		--output text

# Delete the stack
destroy:
	sam delete --stack-name agenda-rouen

clean:
	rm -rf .aws-sam/
