"""
Test Render Deployment (PR 22)

Verifies that both frontend and backend services are deployed and healthy on Render.
"""
import pytest
import httpx


BACKEND_URL = "https://ultrai-jff.onrender.com"
FRONTEND_URL = "https://ultrai-jff-frontend.onrender.com"


@pytest.mark.pr22
@pytest.mark.asyncio
async def test_backend_health_endpoint():
    """
    Test that backend API /health endpoint responds with 200 OK.

    Verifies:
    - Backend service is deployed and running
    - Health check endpoint is accessible
    - Response contains expected status
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BACKEND_URL}/health")

        assert response.status_code == 200, (
            f"Backend health check failed with status {response.status_code}"
        )

        data = response.json()
        assert data.get("status") == "ok", (
            f"Backend health status should be 'ok', got {data.get('status')}"
        )


@pytest.mark.pr22
@pytest.mark.asyncio
async def test_frontend_static_site_loads():
    """
    Test that frontend static site loads and returns HTML with expected content.

    Verifies:
    - Frontend service is deployed and serving static files
    - index.html is accessible
    - HTML contains React root div and app title
    """
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(FRONTEND_URL)

        assert response.status_code == 200, (
            f"Frontend site failed to load with status {response.status_code}"
        )

        html = response.text

        # Check for React root div
        assert '<div id="root"></div>' in html, (
            "Frontend HTML should contain React root div"
        )

        # Check for Vite-generated assets (script tags)
        assert '<script' in html, (
            "Frontend HTML should contain script tags for bundled JS"
        )


@pytest.mark.pr22
@pytest.mark.asyncio
async def test_frontend_has_pr22_wizard_ui():
    """
    Test that frontend is actually deployed with PR 22 wizard components.

    This test fetches the JavaScript bundle and checks for PR 22-specific
    component code like StepIndicator, OrderReceipt, wizard flow.

    Verifies:
    - PR 22 components are in the deployed bundle
    - Not just the PR 20 foundation scaffold
    """
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # First get the HTML to find the JS bundle filename
        html_response = await client.get(FRONTEND_URL)
        html = html_response.text

        # Extract JS bundle filename (e.g., index-X7sDomHt.js)
        import re
        js_match = re.search(r'src="/assets/(index-[^"]+\.js)"', html)
        assert js_match, "Could not find JS bundle in HTML"

        js_filename = js_match.group(1)
        js_url = f"{FRONTEND_URL}/assets/{js_filename}"

        # Fetch the JS bundle
        js_response = await client.get(js_url)
        assert js_response.status_code == 200, (
            f"Failed to load JS bundle from {js_url}"
        )

        js_code = js_response.text

        # Check for PR 22-specific UI strings in the bundle
        # Note: Component names like "StepIndicator" get minified in production,
        # so we check for actual UI text that appears in the wizard
        pr22_indicators = [
            "Enter Query",    # Step 1 text
            "Choose Cocktail",  # Step 2 text
            "Activate UltrAI",  # Step 3 button
            "Confirm & Activate",  # Step 3 label
        ]

        missing = [
            indicator for indicator in pr22_indicators
            if indicator not in js_code
        ]

        assert not missing, (
            f"Frontend appears to be PR 20 (foundation), not PR 22 (wizard). "
            f"Missing PR 22 components: {missing}. "
            f"The service may be deploying from 'main' branch instead of "
            f"'feature/pr22-ui-components'. Check Render service settings."
        )


@pytest.mark.pr22
@pytest.mark.asyncio
async def test_cors_allows_frontend_origin():
    """
    Test that backend CORS allows requests from frontend domain.

    Verifies:
    - CORS headers are present in responses
    - Frontend origin is allowed
    - Preflight requests work correctly
    """
    headers = {
        "Origin": FRONTEND_URL,
        "Access-Control-Request-Method": "GET",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test preflight request (OPTIONS)
        response = await client.options(f"{BACKEND_URL}/health", headers=headers)

        assert response.status_code in [200, 204], (
            f"CORS preflight failed with status {response.status_code}"
        )

        # Check CORS headers
        assert "access-control-allow-origin" in response.headers, (
            "CORS Allow-Origin header missing in response"
        )

        # Verify frontend origin is allowed
        allowed_origin = response.headers.get("access-control-allow-origin")
        assert allowed_origin in [FRONTEND_URL, "*"], (
            f"Frontend origin {FRONTEND_URL} not allowed by CORS. "
            f"Got: {allowed_origin}"
        )


@pytest.mark.pr22
@pytest.mark.asyncio
async def test_frontend_api_connectivity():
    """
    Test that frontend can successfully connect to backend API.

    This simulates what the frontend does when it makes API calls.

    Verifies:
    - Frontend domain can make requests to backend
    - CORS headers allow the request
    - Backend responds correctly to cross-origin requests
    """
    headers = {
        "Origin": FRONTEND_URL,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BACKEND_URL}/health",
            headers=headers
        )

        assert response.status_code == 200, (
            f"Frontend-to-backend request failed with status {response.status_code}"
        )

        # Check that CORS headers are present
        assert "access-control-allow-origin" in response.headers, (
            "CORS headers missing - frontend won't be able to make requests"
        )


@pytest.mark.pr22
def test_deployment_urls_are_documented():
    """
    Test that deployment URLs are documented in project files.

    Verifies:
    - render.yaml contains correct service names
    - CORS configuration references correct frontend URL
    """
    import pathlib

    # Check render.yaml
    render_yaml = pathlib.Path("render.yaml").read_text()
    assert "ultrai-jff-frontend" in render_yaml, (
        "render.yaml should contain frontend service name"
    )
    assert "https://ultrai-jff.onrender.com" in render_yaml, (
        "render.yaml should reference backend URL for frontend env var"
    )

    # Check CORS configuration in api.py
    api_py = pathlib.Path("ultrai/api.py").read_text()
    assert "ultrai-jff-frontend.onrender.com" in api_py, (
        "api.py CORS should reference frontend URL"
    )
