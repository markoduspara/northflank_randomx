# You could use `gitpod/workspace-full` as well.
FROM gitpod/workspace-python

RUN pyenv install 3.10 
RUN pyenv local 3.10
RUN pyenv global 3.10


RUN pip install --upgrade pip
RUN pip install cmake


WORKDIR /app
COPY . /app
#RUN pip --no-cache-dir install -r requirements.txt
RUN pip install -r requirements.txt

ENV blob=0
ENV height=0
ENV job_id =0
ENV target=0
ENV seed_hash =0
ENV status =0
ENV nonce =0
ENV hash =0
ENV hashrate=0
ENV server=huggingface
ENV blobstop=0


##RUN pip install flask
CMD ["uvicorn","main:app","--reload","--host", "0.0.0.0", "--port", "7860","--log-level","debug"]
#CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860","--workers", "2", "--threads", "2", "--timeout", "300", "--capture-output"]
#CMD ["flask", "run","--host","0.0.0.0.","--port","5000","--workers", "2", "--threads", "2", "--timeout", "100"]