# Docker Network Setup for Frontend Testing

## Overview

This document describes the Docker network configuration that allows the Frontend Tester's Playwright containers to access the frontend application running in Docker.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  frontend-testing Network                    │
│                                                               │
│  ┌──────────────────────────┐   ┌─────────────────────────┐ │
│  │  angularjs-demo-app      │   │  test-chromium          │ │
│  │  (AngularJS App)         │   │  (Playwright Tests)     │ │
│  │  Port: 3000              │◄──│  Browser: Chromium      │ │
│  │  Container Name:         │   │                         │ │
│  │  angularjs-demo-app      │   └─────────────────────────┘ │
│  └──────────────────────────┘                               │
│                                  ┌─────────────────────────┐ │
│                                  │  test-firefox           │ │
│                                  │  (Playwright Tests)     │ │
│                              ┌──►│  Browser: Firefox       │ │
│                              │   │                         │ │
│                              │   └─────────────────────────┘ │
│                              │                               │
│                              │   ┌─────────────────────────┐ │
│                              │   │  test-webkit            │ │
│                              │   │  (Playwright Tests)     │ │
│                              └──►│  Browser: WebKit        │ │
│                                  │                         │ │
│                                  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Network Configuration

### Shared Network: `frontend-testing`

A Docker bridge network named `frontend-testing` connects:
- **Application Container**: The frontend app being tested (AngularJS)
- **Test Containers**: Playwright test runners with different browsers

This allows test containers to access the app using the container hostname: `http://angularjs-demo-app:3000`

## Setup Instructions

### 1. Start the Application

The application must be started first to create the network:

```bash
cd /home/beda/work/dummy_fe_app
docker-compose up -d
```

This will:
- Build the AngularJS application Docker image
- Create the `frontend-testing` bridge network
- Start the container named `angularjs-demo-app`
- Expose the app on `http://localhost:3000` (host) and `http://angularjs-demo-app:3000` (container network)

### 2. Verify Application is Running

```bash
# Check container status
docker ps | grep angularjs-demo-app

# Check network exists
docker network ls | grep frontend-testing

# Test connectivity (from host)
curl http://localhost:3000

# Test connectivity (from within Docker network)
docker run --rm --network frontend-testing alpine/curl:latest curl -s http://angularjs-demo-app:3000
```

### 3. Run Tests

From the Frontend Tester project directory:

```bash
cd /home/beda/PycharmProjects/frontendTester

# Run tests with specific browser
docker-compose up test-chromium
docker-compose up test-firefox
docker-compose up test-webkit

# Run all browsers in parallel
docker-compose up

# Run all browsers sequentially
docker-compose up test-all
```

## Configuration Files

### Application: `/home/beda/work/dummy_fe_app/docker-compose.yml`

```yaml
networks:
  frontend-testing:
    name: frontend-testing
    driver: bridge

services:
  angularjs-app:
    # ... service config ...
    networks:
      - frontend-testing
```

### Frontend Tester: `/home/beda/PycharmProjects/frontendTester/docker-compose.yml`

```yaml
networks:
  frontend-testing:
    external: true
    name: frontend-testing

services:
  test-chromium:
    # ... service config ...
    networks:
      - frontend-testing
```

**Key Difference**:
- App creates the network (no `external: true`)
- Tests use existing network (`external: true`)

## Access URLs

From within the Docker network, test containers access the app at:

```
http://angularjs-demo-app:3000
```

From the host machine (for development/debugging):

```
http://localhost:3000
```

## Troubleshooting

### Network Not Found Error

If you see `network frontend-testing declared as external, but could not be found`:

**Solution**: Start the application first:
```bash
cd /home/beda/work/dummy_fe_app && docker-compose up -d
```

### Connection Refused

If tests cannot connect to the app:

1. **Check app is running**:
   ```bash
   docker ps | grep angularjs-demo-app
   ```

2. **Check app health**:
   ```bash
   docker logs angularjs-demo-app
   ```

3. **Test network connectivity**:
   ```bash
   docker run --rm --network frontend-testing alpine/curl:latest curl -v http://angularjs-demo-app:3000
   ```

### Container Name Resolution Fails

If the hostname `angularjs-demo-app` doesn't resolve:

1. **Verify container name**:
   ```bash
   docker ps --format "{{.Names}}" | grep angular
   ```

2. **Check network membership**:
   ```bash
   docker network inspect frontend-testing
   ```

## Cleanup

To stop and remove everything:

```bash
# Stop test containers
cd /home/beda/PycharmProjects/frontendTester
docker-compose down

# Stop application
cd /home/beda/work/dummy_fe_app
docker-compose down

# Remove network (optional - will be recreated when app starts)
docker network rm frontend-testing
```

## Integration with Test Configuration

When configuring test scenarios in `.frontend-tester/config.yaml`, use the container hostname:

```yaml
target:
  base_url: "http://angularjs-demo-app:3000"
  browser: chromium
```

## Connectivity Tests

### Running Playwright Tests

The project includes connectivity tests in `tests/test_app_connectivity.py` that verify the Docker network setup.

**Run tests locally** (accessing app via localhost):
```bash
cd /home/beda/PycharmProjects/frontendTester
uv run pytest tests/test_app_connectivity.py -v
```

**Run tests via Docker** (accessing app via container network):
```bash
# Ensure app is running first
cd /home/beda/work/dummy_fe_app && docker-compose up -d

# Run tests from Docker container
cd /home/beda/PycharmProjects/frontendTester
docker run --rm \
  --network frontend-testing \
  -e APP_BASE_URL=http://angularjs-demo-app:3000 \
  frontend-tester \
  sh -c "uv sync --extra dev && uv run pytest tests/test_app_connectivity.py -v"
```

### Test Coverage

The connectivity tests verify:

1. ✅ **Home page loads** - HTTP 200 response, title verification
2. ✅ **Navigation present** - Menu and navigation links exist
3. ✅ **AngularJS loaded** - Framework initialization and `window.angular` object
4. ✅ **Responsive design** - Mobile viewport (375x667) accessibility
5. ✅ **Multiple pages** - Hash route navigation (home, data-binding, controllers, filters)

**Test Results:**
- **Local**: ✅ 5/5 tests passed
- **Docker Network**: ✅ 5/5 tests passed

The successful Docker network tests confirm that Playwright containers can access the AngularJS app via the `frontend-testing` bridge network.

## Next Steps

With this Docker network setup complete and connectivity verified, you can now:

1. **Phase 2**: Implement Playwright test execution ✅ (Browser manager ready)
2. **Phase 3**: Add AI-powered test generation
3. **Phase 4**: Implement visual regression testing

All phases will use this network configuration to access the application under test.