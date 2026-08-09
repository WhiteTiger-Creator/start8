FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

ENV DEBIAN_FRONTEND=noninteractive

# Least-volatile layers first: fix the working directory before the apt and
# dependency layers so a change to those never invalidates the WORKDIR layer.
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

# /app/data/settled_collections.json ships holding the servicer's UNRECONCILED
# draft exactly as the failed period close left it; the raw collections file and
# the control totals beside it are the sources the responder has to reconcile
# back into the authoritative settled set.
COPY app/ /app/
RUN cp /app/workflow/distribute.py /app/workflow/.distribute.original \
    && chmod a-w /app/workflow/.distribute.original
