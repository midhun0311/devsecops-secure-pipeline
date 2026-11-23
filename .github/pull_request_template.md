## Pull Request Checklist

Before requesting review, please confirm:

### Code Quality
- [ ] All tests pass locally (`pytest`)
- [ ] No new linting errors (`ruff check .`)
- [ ] Type checks pass (`mypy app/`)

### Security
- [ ] No secrets, credentials, or API keys are hardcoded
- [ ] All new user inputs are validated via Pydantic schemas
- [ ] Any new SQL queries use ORM/parameterised queries (no f-strings building SQL)
- [ ] Dependencies added to `requirements.txt` are pinned to a specific version
- [ ] Dockerfile changes do not add unnecessary packages or run as root

### Documentation
- [ ] New behaviour is reflected in the README if user-facing
- [ ] Any ignored findings have a written justification

---

> **Note:** The CI pipeline will automatically run SAST, SCA, secrets scanning, and container scanning. Do not merge until all checks are green.
