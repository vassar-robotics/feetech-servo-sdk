# Publishing vassar-feetech-servo-sdk to PyPI

## Prerequisites

✅ Package built (wheel and source distribution)
✅ Twine installed
❓ PyPI account
❓ API token configured

## Step 1: Create PyPI Accounts

You'll need accounts on both TestPyPI (for testing) and PyPI (for production):

1. **TestPyPI** (recommended for first test): https://test.pypi.org/account/register/
2. **PyPI** (for production release): https://pypi.org/account/register/

## Step 2: Create API Tokens

For security, use API tokens instead of passwords:

### TestPyPI Token:
1. Go to https://test.pypi.org/manage/account/token/
2. Create a token with scope "Entire account"
3. Save the token (starts with `pypi-`)

### PyPI Token:
1. Go to https://pypi.org/manage/account/token/
2. Create a token with scope "Entire account"
3. Save the token (starts with `pypi-`)

## Step 3: Configure Authentication

Create or edit `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

Secure the file:
```bash
chmod 600 ~/.pypirc
```

## Step 4: Check Package (Optional but Recommended)

```bash
twine check dist/*
```

## Step 5: Upload to TestPyPI First

Test your package on TestPyPI before the real PyPI:

```bash
twine upload --repository testpypi dist/*
```

After upload, test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ vassar-feetech-servo-sdk
```

Note: The `--extra-index-url` is needed because TestPyPI doesn't have all dependencies (like pyserial).

## Step 6: Upload to PyPI

Once you've verified everything works on TestPyPI:

```bash
twine upload dist/*
```

## Step 7: Verify Installation

After uploading to PyPI, test the installation:

```bash
pip install vassar-feetech-servo-sdk
```

## Alternative: Using Environment Variables

If you prefer not to save tokens in `~/.pypirc`, you can use environment variables:

```bash
# For TestPyPI
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-YOUR-TEST-TOKEN twine upload --repository testpypi dist/*

# For PyPI
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-YOUR-PRODUCTION-TOKEN twine upload dist/*
```

## Package URLs

After publishing, your package will be available at:

- **TestPyPI**: https://test.pypi.org/project/vassar-feetech-servo-sdk/
- **PyPI**: https://pypi.org/project/vassar-feetech-servo-sdk/

## Troubleshooting

### "Package already exists" Error
If you get this error, you need to increment the version in `pyproject.toml` and rebuild:
```bash
# Edit pyproject.toml to increment version (e.g., 0.1.0 -> 0.1.1)
# Then rebuild
python -m build
# Upload new version
twine upload dist/vassar_feetech_servo_sdk-0.1.1*
```

### Authentication Issues
- Make sure you're using `__token__` as the username
- Ensure your token starts with `pypi-`
- Check that your token has the correct permissions

### Installation Issues After Publishing
- Wait a few minutes for PyPI to update its index
- Try clearing pip's cache: `pip cache purge`

## Next Steps After Publishing

1. Update your GitHub repository with installation instructions
2. Create a release on GitHub with the same version number
3. Consider setting up GitHub Actions for automated releases
4. Add badges to your README (version, downloads, etc.)

## Version Management

For future releases:
1. Update version in `pyproject.toml`
2. Update version in `vassar_feetech_servo_sdk/__init__.py`
3. Add release notes to a CHANGELOG.md
4. Tag the release in git: `git tag v0.1.0`