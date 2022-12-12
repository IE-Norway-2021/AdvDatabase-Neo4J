FROM python:3.9.16-bullseye
COPY src/ src
RUN pip install -r src/requirements.txt
RUN python3 src/clean.py
CMD ["python3", "src/main.py"]