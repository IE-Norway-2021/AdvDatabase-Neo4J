FROM python:3.9.16-bullseye
COPY src/ src
RUN pip install -r src/requirements.txt
CMD ["python3", "-u", "src/main.py"]