FROM python:3.14-slim@sha256:c3e521df8b2b498a7a682e7e18676771cb80c6b75b8699af886b2d554ce40151

RUN useradd --system --no-create-home mock
WORKDIR /app
COPY saj_modbus_mock ./saj_modbus_mock
USER mock

CMD ["python", "-m", "saj_modbus_mock"]
