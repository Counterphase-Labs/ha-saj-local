FROM python:3.14-slim@sha256:c3e521df8b2b498a7a682e7e18676771cb80c6b75b8699af886b2d554ce40151

RUN useradd --system --no-create-home mock
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt
COPY saj_modbus_mock ./saj_modbus_mock
COPY static ./static
COPY scenarios/hs3-battery.yaml /config/config.yaml
RUN mkdir /data && chown mock /data
USER mock

EXPOSE 502 8080
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD ["python", "-m", "saj_modbus_mock", "healthcheck"]
CMD ["python", "-m", "saj_modbus_mock"]
